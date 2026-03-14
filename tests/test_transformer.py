import os
import tempfile
import json
import pytest
from src.transformer import DataTransformer

@pytest.fixture
def mock_mlb_json():
    return {
        "dates": [
            {
                "date": "2023-08-01",
                "games": [
                    {
                        "gamePk": 123456,
                        "gameType": "R",
                        "season": "2023",
                        "gameDate": "2023-08-01T23:05:00Z",
                        "status": {"detailedState": "Final"},
                        "teams": {
                            "away": {"team": {"name": "Away Team"}, "score": 5},
                            "home": {"team": {"name": "Home Team"}, "score": 3}
                        },
                        "venue": {"name": "Test Stadium"}
                    }
                ]
            }
        ]
    }

def test_data_transformer(mock_mlb_json):
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "test_data.json")
        with open(json_path, 'w') as f:
            json.dump(mock_mlb_json, f)
            
        transformer = DataTransformer(json_path)
        csv_path, xml_path = transformer.run()
        
        assert os.path.exists(csv_path)
        assert os.path.exists(xml_path)
        
        # Verify CSV
        with open(csv_path, 'r') as f:
            content = f.read()
            assert "gamePk" in content or "game_pk" in content
            assert "123456" in content
            assert "Away Team" in content
            
        # Verify XML
        with open(xml_path, 'r') as f:
            content = f.read()
            assert "<MLBSchedule>" in content
            assert "<GamePk>123456</GamePk>" in content
            assert "<Name>Home Team</Name>" in content
