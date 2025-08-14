import streamlit as st, pandas as pd
st.title("Admin / Data Preview")
for name in ["guidelines","trials","drugs"]:
    st.subheader(name.title()); st.dataframe(pd.read_csv(f"app/backend/data/{name}.csv"), use_container_width=True)
