import streamlit as st
import pandas as pd
import sys
import os

st.title("Admin / Data Preview")

st.markdown("""
This page shows the synthetic datasets used by the evidence mapper.
In a production system, this would connect to real clinical databases.
""")

# Try both possible paths for data files
data_path = None
for path in ["backend/data", "app/backend/data"]:
    if os.path.exists(f"{path}/guidelines.csv"):
        data_path = path
        break

if not data_path:
    st.error("Could not find data files. Please check the file structure.")
    st.stop()

st.info(f"📁 Loading data from: {data_path}")

for name in ["guidelines", "trials", "drugs"]:
    st.subheader(f"📊 {name.title()} Dataset")
    
    try:
        df = pd.read_csv(f"{data_path}/{name}.csv")
        
        # Show summary stats
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Total Records", len(df))
            st.metric("Columns", len(df.columns))
        
        with col2:
            st.dataframe(df, use_container_width=True)
            
        # Show column info
        with st.expander(f"Column Details for {name}"):
            for col in df.columns:
                unique_vals = df[col].nunique()
                null_count = df[col].isnull().sum()
                st.write(f"**{col}**: {unique_vals} unique values, {null_count} nulls")
                
    except Exception as e:
        st.error(f"Error loading {name}.csv: {str(e)}")
    
    st.markdown("---")

# System info
st.subheader("🔧 System Information")
st.write(f"**Python Path**: {sys.path}")
st.write(f"**Current Working Directory**: {os.getcwd()}")
st.write(f"**Data Path**: {data_path}")
