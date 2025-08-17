import streamlit as st
import io
import zipfile
import pandas as pd
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.engine import find_evidence

st.title("3) Evidence Pack")

st.markdown("""
Download a comprehensive evidence package containing all relevant guidelines, trials, 
and drug information for this patient case.
""")

profile = st.session_state.get("patient_profile")
if not profile:
    st.warning("⚠️ No patient profile found. Complete the **Patient Profile** page first.")
    st.stop()

# Use cached evidence if available, otherwise regenerate
if "evidence_results" in st.session_state:
    e = st.session_state["evidence_results"]
else:
    with st.spinner("Generating evidence..."):
        patient_obj = type("PatientProfile", (object,), profile)()
        e = find_evidence(patient_obj)

gl, tr, dr = e["guidelines"], e["trials"], e["drugs"]

# Show summary before download
st.subheader("📊 Evidence Package Contents")
col1, col2, col3 = st.columns(3)
col1.metric("Guidelines", len(gl))
col2.metric("Trials", len(tr))
col3.metric("Drugs", len(dr))

# Create ZIP file
mem = io.BytesIO()
try:
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        # Patient profile
        z.writestr("patient_profile.json", json.dumps(profile, indent=2))
        
        # Evidence files
        if gl:
            z.writestr("guidelines.csv", pd.DataFrame(gl).to_csv(index=False))
        if tr:
            z.writestr("trials.csv", pd.DataFrame(tr).to_csv(index=False))
        if dr:
            z.writestr("drugs.csv", pd.DataFrame(dr).to_csv(index=False))
        
        # Add README
        readme_content = f"""# Evidence Package

Generated for: {profile['age']} year old {profile['sex']} with {profile['disease']}
Disease Activity: {profile['disease_activity']}
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Files Included:
- patient_profile.json: Complete patient information
- guidelines.csv: Ranked clinical guidelines ({len(gl)} items)
- trials.csv: Relevant clinical trials ({len(tr)} items)  
- drugs.csv: Suggested medications ({len(dr)} items)

## Disclaimer:
This is a demonstration system using synthetic data. 
Not for actual clinical use.
"""
        z.writestr("README.md", readme_content)
        
except Exception as e:
    st.error(f"Error creating evidence package: {str(e)}")
    st.stop()

mem.seek(0)

# Download button
patient_name = f"{profile['disease'].replace(' ', '_')}_{profile['age']}yo_{profile['sex']}"
filename = f"evidence_pack_{patient_name}.zip"

st.download_button(
    label="📥 Download Evidence Pack (ZIP)",
    data=mem.read(),
    file_name=filename,
    mime="application/zip",
    help="Download complete evidence package with all relevant clinical data"
)

# Preview contents
st.markdown("---")
st.subheader("📋 Package Preview")

tab1, tab2, tab3, tab4 = st.tabs(["Patient Profile", "Guidelines", "Trials", "Drugs"])

with tab1:
    st.json(profile)

with tab2:
    if gl:
        st.dataframe(pd.DataFrame(gl), use_container_width=True)
    else:
        st.info("No guidelines found")

with tab3:
    if tr:
        st.dataframe(pd.DataFrame(tr), use_container_width=True)
    else:
        st.info("No trials found")

with tab4:
    if dr:
        st.dataframe(pd.DataFrame(dr), use_container_width=True)
    else:
        st.info("No drugs found")
