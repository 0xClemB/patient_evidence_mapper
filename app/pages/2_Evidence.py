import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.engine import find_evidence, contraindication_flags
from backend.ai import summarize_guideline, summarize_trial, generate_patient_plan

st.title("2) Evidence")

profile = st.session_state.get("patient_profile")
if not profile:
    st.warning("⚠️ No patient profile found. Please complete the **Patient Profile** page first.")
    st.stop()

# Create patient object from profile dict
patient_obj = type("PatientProfile", (object,), profile)()

st.markdown(f"""
**Patient:** {profile['age']} year old {profile['sex']} with {profile['disease']}  
**Disease Activity:** {profile['disease_activity']}  
**Prior Treatments:** {', '.join(profile['prior_treatments']) if profile['prior_treatments'] else 'None'}
""")

with st.spinner("Finding relevant evidence..."):
    e = find_evidence(patient_obj)

gl, tr, dr = e["guidelines"], e["trials"], e["drugs"]

# Guidelines Section
st.subheader("📋 Clinical Guidelines (ranked by relevance)")
if gl:
    gl_df = pd.DataFrame(gl)[["id","source","recommendation","line_of_therapy","score"]]
    st.dataframe(gl_df, use_container_width=True)
    
    # Show reasoning for top guideline
    if gl:
        with st.expander(f"Why {gl[0]['id']} ranked highest"):
            st.write("**Reasoning:**")
            for reason in gl[0].get('reasons', []):
                st.write(f"• {reason}")
else:
    st.info("No matching guidelines found for this patient profile.")

# Trials Section
st.subheader("🔬 Key Clinical Trials (ranked by relevance)")
if tr:
    tr_df = pd.DataFrame(tr)[["id","title","intervention","comparator","primary_outcome","result_summary","year","score"]]
    st.dataframe(tr_df, use_container_width=True)
    
    # Show reasoning for top trial
    if tr:
        with st.expander(f"Why {tr[0]['id']} ranked highest"):
            st.write("**Reasoning:**")
            for reason in tr[0].get('reasons', []):
                st.write(f"• {reason}")
else:
    st.info("No matching trials found for this patient profile.")

# Drugs Section
st.subheader("💊 Suggested Medications (from trials)")
if dr:
    dr_df = pd.DataFrame(dr)[["name","moa","indications","black_box","monitoring","source_trial"]]
    st.dataframe(dr_df, use_container_width=True)
else:
    st.info("No specific drug recommendations available.")

# Safety Flags
st.markdown("---")
st.subheader("⚠️ Safety Assessment")
try:
    drug_df = pd.read_csv("backend/data/drugs.csv")
    flags = contraindication_flags(patient_obj, drug_df)
except FileNotFoundError:
    drug_df = pd.read_csv("app/backend/data/drugs.csv")
    flags = contraindication_flags(patient_obj, drug_df)

if flags["flags"]:
    st.error("**Critical Safety Flags Identified:**")
    for f in flags["flags"]:
        st.write(f"🚨 **{f['drug']}**: {f['flag']}")
else:
    st.success("✅ No major safety contraindications identified with current recommendations.")

# AI Summaries
st.markdown("---")
st.subheader("🤖 AI-Generated Summaries")

col1, col2 = st.columns(2)

with col1:
    st.write("**Guideline Summaries:**")
    if gl:
        for summary in [summarize_guideline(x) for x in gl]:
            st.write(f"• {summary['summary']}")
    else:
        st.write("No guidelines to summarize.")

with col2:
    st.write("**Trial Summaries:**")
    if tr:
        for summary in [summarize_trial(x) for x in tr]:
            st.write(f"• {summary['summary']}")
    else:
        st.write("No trials to summarize.")

# Care Plan
st.markdown("---")
st.subheader("📝 Proposed Care Plan")
plan = generate_patient_plan(profile, gl, tr, dr)

st.info(plan.get("plan_summary", "No specific recommendations available."))

if plan.get("citations"):
    st.caption(f"**Evidence citations:** {', '.join(plan.get('citations', []))}")

# Store evidence for evidence pack
st.session_state["evidence_results"] = e
