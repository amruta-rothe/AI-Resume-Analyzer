import streamlit as st
import PyPDF2
import io
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄")
st.title("📄 AI Resume Analyzer Offline")
st.write("Upload your resume and check job match score.")

uploaded_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
job_description = st.text_area("Enter Job Description Here")
analyze = st.button("Analyze Resume")

def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text(file):
    if file.type == "application/pdf":
        return extract_pdf_text(io.BytesIO(file.read()))
    else:
        return file.read().decode("utf-8")

def calculate_similarity(resume_text, job_text):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([resume_text, job_text])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return round(similarity[0][0] * 100, 2)

def find_missing_skills(resume_text, job_text):
    resume_words = set(resume_text.lower().split())
    job_words = set(job_text.lower().split())
    missing = job_words - resume_words
    return list(missing)[:10]  # show top 10

if analyze and uploaded_file and job_description:
    resume_text = extract_text(uploaded_file)

    if not resume_text.strip():
        st.error("Resume is empty.")
    else:
        score = calculate_similarity(resume_text, job_description)
        missing_skills = find_missing_skills(resume_text, job_description)

        st.subheader("📊 Match Score")
        st.write(f"Your resume matches **{score}%** with the job description.")

        st.subheader("⚠ Missing Keywords (Top 10)")
        st.write(missing_skills)

        if score > 70:
            st.success("Good match! You are suitable for this role.")
        elif score > 40:
            st.warning("Moderate match. Improve missing skills.")
        else:
            st.error("Low match. Consider upgrading your skills.")
