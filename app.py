import streamlit as st
import openai
import PyPDF2
from fpdf import FPDF
import io
import os
from dotenv import load_dotenv

load_dotenv()

class ResearchPaper:
    def __init__(self, file):
        self.file = file
        self.content = self.uploadPaper()

    def uploadPaper(self):
        st.write("Research paper uploaded.")
        reader = PyPDF2.PdfReader(self.file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text

    def generateSummary(self):
        if not self.content:
            return None
        st.write("Generating summary...")
        openai.api_key = os.getenv('api_key') 
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Give a detailed summary of the research paper in a point-wise format so it is easy to understand and interpret\n\n{self.content}"}
            ],
            max_tokens=500
        )
        return response['choices'][0]['message']['content']


# Function to create a PDF with the summarized text
def create_pdf(summary):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for line in summary.split('\n'):
        pdf.multi_cell(0, 10, line)
    
    pdf_buffer = io.BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit interface
st.title("Research Paper Summarizer1")
st.write("Upload a PDF document to summarize its content.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Instantiate the ResearchPaper class and process the file
    research_paper = ResearchPaper(uploaded_file)
    
    # Generate summary
    with st.spinner('Generating the summary...'):
        summary = research_paper.generateSummary()
    
    if summary:
        # Display the summarized content
        st.success("Summarization complete!")
        st.subheader("Summarized Content")
        st.text_area("Summary", summary, height=300)
        
        # Create and download the summarized PDF
        st.write("Download the summarized PDF below:")
        pdf_buffer = create_pdf(summary)
        st.download_button(
            label="Download Summarized PDF",
            data=pdf_buffer,
            file_name="summary_output.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Failed to generate a summary. The content might not have been extracted properly.")


