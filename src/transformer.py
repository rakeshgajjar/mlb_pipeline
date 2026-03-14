import csv
import json
import logging
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd

logger = logging.getLogger(__name__)

class DataTransformer:
    def __init__(self, json_filepath: str):
        self.json_filepath = json_filepath
        self.output_dir = os.path.dirname(json_filepath)
        self.base_name = os.path.splitext(os.path.basename(json_filepath))[0]

    def _load_json(self) -> dict:
        try:
            with open(self.json_filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON: {e}")
            raise

    def to_csv(self) -> str:
        data = self._load_json()
        games_list = []
        
        # Parse MLB schedule schema safely
        for date_info in data.get('dates', []):
            date = date_info.get('date', 'Unknown')
            for game in date_info.get('games', []):
                game_dict = {
                    'game_pk': game.get('gamePk'),
                    'game_type': game.get('gameType'),
                    'season': game.get('season'),
                    'game_date': game.get('gameDate'),
                    'status': game.get('status', {}).get('detailedState'),
                    'away_team': game.get('teams', {}).get('away', {}).get('team', {}).get('name'),
                    'away_score': game.get('teams', {}).get('away', {}).get('score'),
                    'home_team': game.get('teams', {}).get('home', {}).get('team', {}).get('name'),
                    'home_score': game.get('teams', {}).get('home', {}).get('score'),
                    'venue': game.get('venue', {}).get('name')
                }
                games_list.append(game_dict)
                
        if not games_list:
            logger.warning("No games found in JSON payload.")
            return ""

        df = pd.DataFrame(games_list)
        csv_path = os.path.join(self.output_dir, f"{self.base_name}.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"Generated CSV output at {csv_path}")
        return csv_path

    def to_xml(self) -> str:
        data = self._load_json()
        
        root = ET.Element("MLBSchedule")
        
        for date_info in data.get('dates', []):
            date_elem = ET.SubElement(root, "Date", value=date_info.get('date', 'Unknown'))
            for game in date_info.get('games', []):
                game_elem = ET.SubElement(date_elem, "Game")
                
                ET.SubElement(game_elem, "GamePk").text = str(game.get('gamePk', ''))
                ET.SubElement(game_elem, "GameType").text = str(game.get('gameType', ''))
                ET.SubElement(game_elem, "GameDate").text = str(game.get('gameDate', ''))
                
                status_elem = ET.SubElement(game_elem, "Status")
                status_elem.text = str(game.get('status', {}).get('detailedState', ''))
                
                teams_elem = ET.SubElement(game_elem, "Teams")
                away = ET.SubElement(teams_elem, "Away")
                away_team = game.get('teams', {}).get('away', {})
                ET.SubElement(away, "Name").text = str(away_team.get('team', {}).get('name', ''))
                ET.SubElement(away, "Score").text = str(away_team.get('score', ''))
                
                home = ET.SubElement(teams_elem, "Home")
                home_team = game.get('teams', {}).get('home', {})
                ET.SubElement(home, "Name").text = str(home_team.get('team', {}).get('name', ''))
                ET.SubElement(home, "Score").text = str(home_team.get('score', ''))
                
                venue_elem = ET.SubElement(game_elem, "Venue")
                venue_elem.text = str(game.get('venue', {}).get('name', ''))

        # Pretty-print XML
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="    ")
        
        xml_path = os.path.join(self.output_dir, f"{self.base_name}.xml")
        with open(xml_path, "w", encoding='utf-8') as f:
            f.write(xmlstr)
            
        logger.info(f"Generated XML output at {xml_path}")
        return xml_path

    def run(self):
        try:
            csv_path = self.to_csv()
            xml_path = self.to_xml()
            return csv_path, xml_path
        except Exception as e:
            logger.error(f"Transformer failed: {e}")
            raise
