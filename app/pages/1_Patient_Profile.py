import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.engine import PatientProfile

st.title("1) Patient Profile")

st.markdown("""
Enter patient information to generate personalized evidence-based recommendations.
All data is synthetic for demonstration purposes only.
""")

with st.form(key="patient_form"):
    col1, col2, col3 = st.columns(3)
    age = col1.number_input("Age", min_value=16, max_value=100, value=54, help="Patient age in years")
    sex = col2.selectbox("Sex", ["female","male","other"])
    disease = col3.selectbox("Disease", ["rheumatoid arthritis","systemic lupus erythematosus"], 
                           help="Primary rheumatologic diagnosis")
    
    activity = st.selectbox("Disease activity", ["low","moderate","high"], index=1,
                          help="Current disease activity level")
    
    comorbid = st.multiselect("Comorbidities", 
                             ["heart failure","liver disease","renal impairment","VTE risk","CV risk factors","ILD"],
                             help="Select all relevant comorbidities")
    
    prior = st.multiselect("Prior treatments", 
                          ["methotrexate","csDMARD","TNF inhibitor","JAK inhibitor","hydroxychloroquine"],
                          help="Previous medications tried")
    
    col4, col5 = st.columns(2)
    preg = col4.checkbox("Pregnancy planning", help="Patient is planning pregnancy")
    smoke = col5.checkbox("Smoking", help="Current or recent smoking history")
    
    submitted = st.form_submit_button("Save profile")

if submitted:
    profile = PatientProfile(
        age=age, 
        sex=sex, 
        disease=disease, 
        disease_activity=activity, 
        comorbidities=comorbid, 
        prior_treatments=prior, 
        pregnancy_planning=preg, 
        smoking=smoke
    ).to_dict()
    st.session_state["patient_profile"] = profile
    st.success("✅ Profile saved successfully! Navigate to the **Evidence** page to see recommendations.")
    
    # Show summary of saved profile
    with st.expander("View saved profile"):
        st.json(profile)
else:
    st.info("📝 Fill out the patient information above and click 'Save profile' to continue.")

# Show current profile if exists
if "patient_profile" in st.session_state:
    st.markdown("---")
    st.subheader("Current Patient Profile")
    current_profile = st.session_state["patient_profile"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Age", current_profile["age"])
    col2.metric("Sex", current_profile["sex"].title())
    col3.metric("Disease", current_profile["disease"].title())
    
    if current_profile["comorbidities"]:
        st.write("**Comorbidities:**", ", ".join(current_profile["comorbidities"]))
    if current_profile["prior_treatments"]:
        st.write("**Prior treatments:**", ", ".join(current_profile["prior_treatments"]))
