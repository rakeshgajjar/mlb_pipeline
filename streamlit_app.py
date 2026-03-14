import streamlit as st
import pandas as pd
import os
import glob

st.set_page_config(page_title="MLB Schedule Dashboard", layout="wide")

st.title("⚾ MLB Data Pipeline Dashboard")
st.markdown("This dashboard automatically visualizes the latest data pulled by the MLB data pipeline.")

@st.cache_data
def load_latest_data():
    data_dir = "./data"
    if not os.path.exists(data_dir):
        return None
    
    # Find all CSV files in the data directory
    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not csv_files:
        return None
        
    # Get the latest file based on modification time
    latest_file = max(csv_files, key=os.path.getmtime)
    
    try:
        df = pd.read_csv(latest_file)
        return df, latest_file
    except Exception as e:
        st.error(f"Error loading {latest_file}: {e}")
        return None

result = load_latest_data()

if result is None:
    st.info("No MLB schedule data found in the `data/` directory. Run the pipeline to fetch data!")
else:
    df, filename = result
    
    st.success(f"Successfully loaded latest data: `{os.path.basename(filename)}`")
    
    # Show high-level metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Games", len(df))
    with col2:
        st.metric("Total Venues", df['venue'].nunique() if 'venue' in df else "N/A")
    with col3:
        status_counts = df['status'].value_counts() if 'status' in df else {}
        scheduled = status_counts.get("Scheduled", 0)
        final = status_counts.get("Final", 0)
        st.metric("Scheduled / Final", f"{scheduled} / {final}")

    st.subheader("Raw Data Preview")
    st.dataframe(df.head(50), use_container_width=True)
    
    # Basic Visualizations
    if not df.empty and 'status' in df:
        st.subheader("Game Status Distribution")
        status_df = df['status'].value_counts().reset_index()
        status_df.columns = ['Status', 'Count']
        st.bar_chart(status_df.set_index('Status'))
        
    if not df.empty and 'venue' in df:
        st.subheader("Games per Venue (Top 10)")
        venue_df = df['venue'].value_counts().head(10).reset_index()
        venue_df.columns = ['Venue', 'Count']
        st.bar_chart(venue_df.set_index('Venue'))
