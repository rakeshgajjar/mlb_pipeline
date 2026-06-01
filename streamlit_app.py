import streamlit as st
import pandas as pd
import os
import glob
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="MLB Score & Stats Dashboard", layout="wide", page_icon="⚾")

st.title("⚾ MLB Data Pipeline Dashboard")
st.markdown("This dashboard automatically visualizes the latest data pulled by the MLB data pipeline.")


@st.cache_data
def load_latest_data(prefix: str) -> pd.DataFrame | None:
    """Load the latest CSV file for a given data prefix.
    
    Args:
        prefix: Data prefix to search for (e.g., 'schedule', 'standings')
        
    Returns:
        DataFrame with loaded data, or None if not found or error occurred
    """
    data_dir = "./data"
    if not os.path.exists(data_dir):
        logger.warning(f"Data directory not found: {data_dir}")
        return None
    
    # Find all CSV files matching the prefix
    csv_files = glob.glob(os.path.join(data_dir, f"mlb_{prefix}_*.csv"))
    if not csv_files:
        logger.info(f"No CSV files found for prefix: {prefix}")
        return None
        
    # Get the latest file based on modification time
    latest_file = max(csv_files, key=os.path.getmtime)
    logger.info(f"Loading latest data from {latest_file}")
    
    try:
        df = pd.read_csv(latest_file)
        logger.info(f"Successfully loaded {len(df)} records from {latest_file}")
        return df
    except Exception as e:
        logger.error(f"Error loading {latest_file}: {e}", exc_info=True)
        st.error(f"Error loading {latest_file}: {e}")
        return None

# Load all schemas
schedule_df = load_latest_data("schedule")
standings_df = load_latest_data("standings")
hitting_df = load_latest_data("hitting_stats")
pitching_df = load_latest_data("pitching_stats")

# Tabs for clear separation
tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings & Leaderboard", "🔥 Hitting Stats", "🎯 Pitching Stats", "📅 Scheduling"])

with tab1:
    st.header("🏆 Team Standings")
    if standings_df is not None and not standings_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Teams Tracked", len(standings_df))
        with col2:
            st.metric("Leagues", standings_df['league'].nunique() if 'league' in standings_df else "N/A")
            
        st.subheader("Leaderboard Preview")
        # Sort by wins
        if 'wins' in standings_df:
            standings_df = standings_df.sort_values(by="wins", ascending=False)
            
        st.dataframe(standings_df.head(20), use_container_width=True)
    else:
        st.info("No Standings Data Available")

with tab2:
    st.header("🔥 Player Hitting Leaderboard")
    if hitting_df is not None and not hitting_df.empty:
        # Display key hitting metrics if available
        if 'homeRuns' in hitting_df:
            st.subheader("Top 10 Home Run Leaders")
            hr_leaders = hitting_df.sort_values(by="homeRuns", ascending=False).head(10)
            st.bar_chart(hr_leaders.set_index('player')['homeRuns'])

        if 'strikeOuts' in hitting_df:
            st.subheader("Top 10 Batters by Strikeouts")
            so_leaders = hitting_df.sort_values(by="strikeOuts", ascending=False).head(10)
            st.bar_chart(so_leaders.set_index('player')['strikeOuts'])

        st.subheader("Detailed Hitting Metrics")
        display_cols = ['player', 'team', 'gamesPlayed', 'runs', 'hits', 'homeRuns', 'strikeOuts', 'avg', 'obp', 'slg', 'ops']
        available_cols = [c for c in display_cols if c in hitting_df.columns]
        st.dataframe(hitting_df[available_cols].head(30), use_container_width=True)
    else:
        st.info("No Hitting Data Available")

with tab3:
    st.header("🎯 Player Pitching Leaderboard")
    if pitching_df is not None and not pitching_df.empty:
        if 'strikeOuts' in pitching_df:
            st.subheader("Top 10 Pitching Strikeout Leaders")
            so_pitchers = pitching_df.sort_values(by="strikeOuts", ascending=False).head(10)
            st.bar_chart(so_pitchers.set_index('player')['strikeOuts'])
            
        if 'era' in pitching_df:
            st.subheader("Top 10 Pitchers by ERA (Lowest is Better)")
            # Filter out extreme anomalies where era might be '-'
            pitching_df['era'] = pd.to_numeric(pitching_df['era'], errors='coerce')
            era_leaders = pitching_df.dropna(subset=['era']).sort_values(by="era", ascending=True).head(10)
            st.bar_chart(era_leaders.set_index('player')['era'])

        st.subheader("Detailed Pitching Metrics")
        display_cols = ['player', 'team', 'gamesPlayed', 'wins', 'losses', 'era', 'strikeOuts', 'whip']
        available_cols = [c for c in display_cols if c in pitching_df.columns]
        st.dataframe(pitching_df[available_cols].head(30), use_container_width=True)
    else:
        st.info("No Pitching Data Available")

with tab4:
    st.header("📅 Game Schedules")
    if schedule_df is not None and not schedule_df.empty:
        st.subheader("Raw Data Preview")
        st.dataframe(schedule_df.head(50), use_container_width=True)
        
        # Basic Visualizations
        if 'status' in schedule_df:
            st.subheader("Game Status Distribution")
            status_df = schedule_df['status'].value_counts().reset_index()
            status_df.columns = ['Status', 'Count']
            st.bar_chart(status_df.set_index('Status'))
    else:
        st.info("No Schedule Data Available")
