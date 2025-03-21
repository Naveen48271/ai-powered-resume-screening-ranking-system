import requests
import streamlit as st

st.title("📄 AI-Powered Resume Screening & Ranking")
st.write("Upload resumes and compare them with a job description.")

# Job Description Input
job_description = st.text_area("Enter Job Description", "")

# Resume Upload
uploaded_files = st.file_uploader("Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)

# Submit Button
if st.button("Rank Resumes"):
    if job_description and uploaded_files:
        files = [('resumes', (file.name, file, 'application/pdf')) for file in uploaded_files]
        
        try:
            response = requests.post("http://127.0.0.1:5000/rank", data={'job_description': job_description}, files=files)

            if response.status_code == 200:
                ranked_resumes = response.json().get("ranked_resumes", [])
                st.write("### 📌 Ranked Resumes:")
                for rank, (name, score) in enumerate(ranked_resumes, start=1):
                    st.write(f"{rank}. **{name}** - Score: {score:.2f}")
            else:
                st.error("Error ranking resumes!")
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Unable to connect to the backend. Is Flask running?")
    else:
        st.warning("Please enter a job description and upload resumes.")
