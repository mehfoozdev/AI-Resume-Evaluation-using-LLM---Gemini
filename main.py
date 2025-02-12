# import json
# import streamlit as st
# import base64
# import os
# import io
# from PIL import Image
# import pdf2image
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()  

# # GOOGLE_API_KEY_EN = os.environ.get("GOOGLE_API_KEY")
# GOOGLE_API_KEY_EN = os.getenv("GOOGLE_API_KEY")

# # Load environment variables
# genai.configure(api_key=GOOGLE_API_KEY_EN)

# # You are an experienced (HR) Human Resource Manager. Your task is to review the provided resume against the job description. 
# # Please share your professional evaluation on whether the candidate's profile aligns with the role. 
# # Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
# # Provide improvement suggestions based on job descriptions.

# # Define the input prompt
# input_prompt = """
# You are an HR assistant. Evaluate the resume based on the job description.
# Job Description: {job_description}
# Resume: {resume}

# Provide a score from 1 to 10 and a short reason for your score.


# Additionally, extract the following details from the resume:
# 1. Name of the candidate
# 2. Highest degree obtained (return only short degree name, for instance "BSCS" 
# 3. Total years of experience
# 4. Gender (if mentioned) otherwise None

# Return the extracted details in the following JSON format:  #write only => JSON Output:
# {
#     "name": "Candidate Name",
#     "degree": "Highest Degree",
#     "experience": "Total Years of Experience",
#     "gender": "Gender"
# }
# """

# # Function to process all pages of the PDF
# def input_pdf_setup(uploaded_file):
#     images = pdf2image.convert_from_bytes(uploaded_file.read())
#     pdf_parts = []

#     for image in images:
#         img_byte_arr = io.BytesIO()  # Convert each page to bytes
#         image.save(img_byte_arr, format='JPEG')
#         img_byte_arr = img_byte_arr.getvalue()

#         pdf_parts.append({
#             "mime_type": "image/jpeg",
#             "data": base64.b64encode(img_byte_arr).decode()  # Encode to base64
#         })
    
#     return pdf_parts

# # Function to get Gemini AI response
# def get_gemini_response(job_desc, pdf_content, prompt):
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     response = model.generate_content([job_desc] + pdf_content + [prompt])  
#     # return response.text
#     # Extract JSON from the response
#     try:
#         # Find the JSON part in the response
#         json_start = response.text.find("{")
#         json_end = response.text.rfind("}") + 1
#         json_str = response.text[json_start:json_end]
        
#         # Parse JSON
#         extracted_data = json.loads(json_str)
#     except Exception as e:
#         st.error(f"Error parsing JSON: {e}")
#         extracted_data = {
#             "name": "Not found",
#             "degree": "Not found",
#             "experience": "Not found",
#             "gender": "Not found"
#         }
    
#     return response.text, extracted_data


# # Streamlit UI
# st.title("SmartCV Analyzer")

# # Upload PDF
# uploaded_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])

# # Job Description Input
# job_description = st.text_area("Enter Job Description", placeholder="e.g., Data Engineer role requiring SQL, Python, and Big Data experience")

# if st.button("Evaluate CV"):
#     if uploaded_file and job_description:
#         try:
#             st.info("Processing resume...⏳")
#             pdf_content = input_pdf_setup(uploaded_file) 
#             response, extracted_data = get_gemini_response(job_description, pdf_content, input_prompt) 

#             # Display extracted details in columns
#             st.subheader("Candidate Details:")
            
#             col1, col2, col3, col4 = st.columns(4)
#             with col1:
#                 st.markdown("**Name**")
#                 st.write(extracted_data["name"])
#             with col2:
#                 st.markdown("**Degree**")
#                 st.write(extracted_data["degree"])
#             with col3:
#                 st.markdown("**Total Experience**")
#                 st.write(extracted_data["experience"])
#             with col4:
#                 st.markdown("**Gender**")
#                 st.write(extracted_data["gender"])

#             # Display AI evaluation response
#             st.success("✅ Evaluation Complete!")
#             st.subheader("AI Evaluation Report : ")
#             st.write(response)
#             # st.write(response.split("JSON Output:")[0].strip())  

#         except Exception as e:
#             st.error(f"Error: {e}")
#     else:
#         st.warning("Please upload a PDF and enter a job description.")