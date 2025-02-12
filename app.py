import json
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
import fitz  
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()  

GOOGLE_API_KEY_EN = os.getenv("GOOGLE_API_KEY")


# Define the function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
    doc = fitz.open(temp_file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# Define the prompt template
prompt_template = """
You are an HR assistant. Evaluate the resume based on the job description.
Job Description: {job_description}
Resume: {resume}

Provide a score from 1 to 10 and a short reason for your score.

Additionally, extract the following details from the resume:
1. Name of the candidate
2. Highest degree obtained (write only degree name, for instance "BSCS" 
3. Total years of experience
4. Key technical skills (return only 1-3 key technical skill names, in short, clean text)

Return the extracted details in the following JSON format:  #write only => JSON Output:
{{ 
    "name": "Candidate Name",
    "degree": "Highest Degree",
    "experience": "Total Years of Experience",
    "technical_skills": "Technical Skills"
}}
"""

prompt = PromptTemplate(input_variables=["job_description", "resume"], template=prompt_template)

# Initialize the Gemini model
llm_model = ChatGoogleGenerativeAI(model="gemini-pro",
                             verbose=True,
                             temperature=0.0,
                             google_api_key=GOOGLE_API_KEY_EN)

# Create the chain using RunnablePassthrough and RunnableSequence
chain = (
    {"job_description": RunnablePassthrough(), "resume": RunnablePassthrough()}
    | prompt
    | llm_model
)

# Function to evaluate resume using the new chain
def get_gemini_response(job_description, resume):
    response = chain.invoke({"job_description": job_description, "resume": resume})
    try:
        json_start = response.content.find("{")
        json_end = response.content.rfind("}") + 1
        json_str = response.content[json_start:json_end]
        extracted_data = json.loads(json_str)

    except Exception as e:
        st.error(f"Error parsing JSON: {e}")
        extracted_data = {
            "name": "Not found",
            "degree": "Not found",
            "experience": "Not found",
            "technical_skills": "Not found"
        }
    
    return response.content, extracted_data



# Streamlit UI
st.title("SmartCV Analyzer")

# Upload PDF
uploaded_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])

# Job Description Input
job_description = st.text_area("Enter Job Description", placeholder="e.g.: Backend Developer role requiring Python, Django and SQL experience")

if st.button("Evaluate CV"):
    if uploaded_file and job_description:
        try:

            st.info("Processing resume... ⏳ ")
            resume_text = extract_text_from_pdf(uploaded_file) 
            response, extracted_data = get_gemini_response(job_description, resume_text) 

            # Display extracted details in columns
            st.success("✅ Evaluation Complete!")
            st.subheader("Candidate Details:")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                with st.container():
                    st.markdown("**Name of Candidate**")
                    st.write(extracted_data["name"])
            with col2:
                with st.container():
                    st.markdown("**Highest Degree**")
                    st.write(extracted_data["degree"])
            with col3:
                with st.container():
                    st.markdown("**Total Experience**")
                    st.write(extracted_data["experience"])
            with col4:
                with st.container():
                    st.markdown("**Technical Skills**")
                    st.write(extracted_data["technical_skills"]) 

            # Display AI evaluation response
            st.subheader("AI Evaluation Response : ")
            st.write(response.split("**JSON Output:**")[0].strip()) 

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.write("Please upload a resume and provide a job description to get started.")    