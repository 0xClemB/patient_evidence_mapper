import streamlit as st
from app.backend.engine import PatientProfile

st.title("1) Patient Profile")
with st.form(key="patient_form"):
    col1, col2, col3 = st.columns(3)
    age = col1.number_input("Age", min_value=16, max_value=100, value=54)
    sex = col2.selectbox("Sex", ["female","male","other"])
    disease = col3.selectbox("Disease", ["rheumatoid arthritis","systemic lupus erythematosus"])
    activity = st.selectbox("Disease activity", ["low","moderate","high"], index=1)
    comorbid = st.multiselect("Comorbidities", ["heart failure","liver disease","renal impairment","VTE risk","CV risk factors","ILD"])
    prior = st.multiselect("Prior treatments", ["methotrexate","csDMARD","TNF inhibitor","JAK inhibitor","hydroxychloroquine"])
    preg = st.checkbox("Pregnancy planning")
    smoke = st.checkbox("Smoking")
    submitted = st.form_submit_button("Save profile")
if submitted:
    profile = PatientProfile(age=age, sex=sex, disease=disease, disease_activity=activity, comorbidities=comorbid, prior_treatments=prior, pregnancy_planning=preg, smoking=smoke).to_dict()
    st.session_state["patient_profile"] = profile
    st.success("Profile saved. Go to **Evidence** page.")
else:
    st.info("Fill the form and click Save.")
