import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄")
st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and get AI-powered feedback.")

# Get OpenRouter API key
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("API key not found. Please check your .env file.")
    st.stop()

# File upload
uploaded_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter target job role (optional)")
analyze = st.button("Analyze Resume")

# Extract PDF text
def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Extract file text
def extract_text(file):
    if file.type == "application/pdf":
        return extract_pdf_text(io.BytesIO(file.read()))
    else:
        return file.read().decode("utf-8")

# When analyze button clicked
if analyze and uploaded_file:
    try:
        resume_text = extract_text(uploaded_file)

        if not resume_text.strip():
            st.error("Resume is empty.")
            st.stop()

        prompt = f"""
You are an expert HR professional.

Analyze this resume and provide:

1. Strengths
2. Weaknesses
3. Skills feedback
4. Suggestions for improvement
5. Suitability for {job_role if job_role else "general job roles"}

Resume:
{resume_text}
"""

        # OpenRouter client
        client = OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "AI Resume Analyzer Project"
            }
        )

        with st.spinner("Analyzing resume..."):
            response = client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct:", 
                messages=[
                    {"role": "system", "content": "You are a professional resume reviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )

        st.subheader("📊 Resume Analysis")
        st.write(response.choices[0].message.content)

    except Exception as e:
        st.error(f"Error: {str(e)}")