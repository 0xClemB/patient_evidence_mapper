import streamlit as st, pandas as pd
from app.backend.engine import find_evidence, contraindication_flags
from app.backend.ai import summarize_guideline, summarize_trial, generate_patient_plan
st.title("2) Evidence")
profile = st.session_state.get("patient_profile")
if not profile:
    st.warning("No patient profile found. Please complete the Patient Profile page first."); st.stop()
e = find_evidence(type("P",(object,),profile)())
gl, tr, dr = e["guidelines"], e["trials"], e["drugs"]
st.subheader("Guidelines (ranked)")
st.dataframe(pd.DataFrame(gl)[["id","source","recommendation","line_of_therapy","score"]] if gl else pd.DataFrame(), use_container_width=True)
st.subheader("Key Trials (ranked)")
st.dataframe(pd.DataFrame(tr)[["id","title","intervention","comparator","primary_outcome","result_summary","year","score"]] if tr else pd.DataFrame(), use_container_width=True)
st.subheader("Suggested Drugs (from trials)")
st.dataframe(pd.DataFrame(dr)[["name","moa","indications","black_box","monitoring","source_trial"]] if dr else pd.DataFrame(), use_container_width=True)
st.markdown("---"); st.subheader("AI Summaries (template)")
st.json({"guidelines":[summarize_guideline(x) for x in gl], "trials":[summarize_trial(x) for x in tr]})
plan = generate_patient_plan(profile, gl, tr, dr)
st.markdown("**Proposed Care Plan (draft)**"); st.write(plan.get("plan_summary","")); st.caption("Citations: " + ", ".join(plan.get("citations", [])))
import pandas as pd
drug_df = pd.read_csv("app/backend/data/drugs.csv")
flags = contraindication_flags(type("P",(object,),profile)(), drug_df)
if flags["flags"]:
    st.warning("Safety Flags:")
    for f in flags["flags"]: st.write(f"- {f['drug']}: {f['flag']}")
