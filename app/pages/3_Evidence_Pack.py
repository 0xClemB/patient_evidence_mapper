import streamlit as st, io, zipfile, pandas as pd, json
from app.backend.engine import find_evidence
st.title("3) Evidence Pack")
profile = st.session_state.get("patient_profile")
if not profile: st.warning("No patient profile found. Complete the Patient Profile page first."); st.stop()
e = find_evidence(type("P",(object,),profile)())
gl, tr, dr = e["guidelines"], e["trials"], e["drugs"]
mem = io.BytesIO()
with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("patient_profile.json", json.dumps(profile, indent=2))
    if gl: z.writestr("guidelines.csv", pd.DataFrame(gl).to_csv(index=False))
    if tr: z.writestr("trials.csv", pd.DataFrame(tr).to_csv(index=False))
    if dr: z.writestr("drugs.csv", pd.DataFrame(dr).to_csv(index=False))
mem.seek(0)
st.download_button("Download Evidence Pack (ZIP)", data=mem.read(), file_name="evidence_pack.zip")
