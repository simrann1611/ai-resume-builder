import streamlit as st
from io import BytesIO
from pypdf import PdfReader

# Securely import Google GenAI
try:
    from google import genai
except ImportError:
    st.error("The 'google-genai' package is missing. Please run 'pip install google-genai' in your VS Code terminal.")

# Import Document generation tools
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ---------------------------------------------------------------------------
# CORE APPLICATION LOGIC (THE UPGRADED FORMULA & PROMPT)
# ---------------------------------------------------------------------------

def extract_text_from_pdf(uploaded_file):
    """Safely extracts text content from an uploaded resume PDF."""
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error parsing PDF file: {e}")
        return ""

def generate_optimized_resume_data(api_key, resume_text, job_description):
    """
    Connects to Gemini 2.5 Flash with an advanced corporate recruiter prompt.
    Uses the strict X-Y-Z impact formula to draft a brand new resume.
    """
    try:
        client = genai.Client(api_key=api_key)
        
        # This upgraded prompt forces a split output structure and applies strict writing formulas
        prompt = f"""
        You are an elite Tech Recruiter and expert ATS optimization engine. 
        Analyze the following [CURRENT RESUME] against the [TARGET JOB DESCRIPTION].
        
        CRITICAL TASK: You must perform two operations:
        1. Create an ATS metric evaluation report.
        2. Rewrite their entire resume into a high-scoring, perfectly tailored version.
        
        When rewriting the experience section, use the strict Google X-Y-Z Formula: 
        "Accomplished [X] as measured by [Y], by doing [Z]". Use metrics, percentages, and hard keywords where logical.

        Format your entire response using the exact layout tags below:
        
        ---REPORT_START---
        ### 🎯 ATS Match Rating
        [Provide a hard percentage score out of 100 based on keyword density and keyword alignment]
        
        ### 🔍 Critical Keywords & Skills Missing
        - [List core skills missing from the original text that are highly requested in the JD]
        
        ### 🛠️ Strategic Alignment Gaps
        - [Explain what content structural gaps exist between the candidate's current profile and the target role]
        ---REPORT_END---
        
        ---RESUME_START---
        # [CANDIDATE FULL NAME]
        [Contact Information Placeholder]
        
        ## 📝 PROFESSIONAL SUMMARY
        [Write a stellar, 3-4 sentence summary loaded with key terms from the job description]
        
        ## 🛠️ TECHNICAL SKILLS & COMPETENCIES
        [List relevant skills matching the JD precisely, organized cleanly by category]
        
        ## 💼 PROFESSIONAL EXPERIENCE
        [Rewrite their job history into high-impact bullet points using the action-oriented X-Y-Z format]
        
        ## 🎓 EDUCATION & CREDENTIALS
        [Clean presentation of academic history and certifications]
        ---RESUME_END---
        
        Target Job Description:
        {job_description}
        
        Current Resume:
        {resume_text}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Connection Error: {e}. Check your API Key configuration."

# ---------------------------------------------------------------------------
# OUTPUT EXPORT COMPILERS
# ---------------------------------------------------------------------------

def generate_docx(resume_text):
    """Compiles the rewritten resume text directly into a professional Word file."""
    doc = Document()
    for line in resume_text.split('\n'):
        line_clean = line.strip()
        if not line_clean:
            continue
        if line_clean.startswith('# '):
            doc.add_heading(line_clean.replace('# ', ''), level=0)
        elif line_clean.startswith('## '):
            doc.add_heading(line_clean.replace('## ', ''), level=1)
        elif line_clean.startswith('### '):
            doc.add_heading(line_clean.replace('### ', ''), level=2)
        elif line_clean.startswith(('- ', '* ')):
            doc.add_paragraph(line_clean[2:], style='List Bullet')
        else:
            doc.add_paragraph(line_clean)
            
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def generate_pdf(resume_text):
    """Compiles the rewritten resume text directly into a PDF template document."""
    bio = BytesIO()
    doc = SimpleDocTemplate(bio, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    for line in resume_text.split('\n'):
        line_clean = line.strip().replace('**', '').replace('*', '').replace('#', '').strip()
        if not line_clean:
            continue
        if 'PROFESSIONAL SUMMARY' in line or 'TECHNICAL SKILLS' in line or 'PROFESSIONAL EXPERIENCE' in line or 'EDUCATION' in line:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>{line_clean}</b>", styles['Heading2']))
            story.append(Spacer(1, 4))
        elif line.strip().startswith(('-', '*')):
            story.append(Paragraph(f"• {line_clean}", styles['Normal']))
        else:
            story.append(Paragraph(line_clean, styles['Normal']))
            
    doc.build(story)
    bio.seek(0)
    return bio

# ---------------------------------------------------------------------------
# MAIN USER INTERFACE DESIGN
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Next-Gen AI ATS Resume Engine", page_icon="🎯", layout="wide")

st.title("🚀 Smart AI Resume Optimizer & Rewriter")
st.write("Upload a draft resume to evaluate performance gaps and build a fully tailored, ready-to-export version.")

# Sidebar setup for security keys
api_key_input = st.sidebar.text_input("Enter Gemini API Key:", type="password")

# Grid layout split for inputs
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 1. Target Job Parameters")
    job_description = st.text_area("Paste the Target Job Description here:", height=250, placeholder="Requirements, duties...")

with col2:
    st.subheader("📄 2. Your Current Document")
    uploaded_file = st.file_uploader("Upload your current Resume/CV (PDF):", type=["pdf"])

st.markdown("---")

if st.button("Run ATS Screen & Auto-Rewrite", type="primary", use_container_width=True):
    if not api_key_input:
        st.warning("Please input your Gemini API Key in the left sidebar layout pane.")
    elif not job_description:
        st.warning("Please supply a targeted Job Description to compare against.")
    elif not uploaded_file:
        st.warning("Please upload a PDF version of your resume.")
    else:
        with st.spinner("Executing structural re-engineering and performance scoring..."):
            raw_resume_text = extract_text_from_pdf(uploaded_file)
            if raw_resume_text:
                full_ai_output = generate_optimized_resume_data(api_key_input, raw_resume_text, job_description)
                
                # Split the raw data into separate states for clean presentation
                report_content = "Analysis pending..."
                best_resume_content = "Generation pending..."
                
                if "---REPORT_START---" in full_ai_output and "---REPORT_END---" in full_ai_output:
                    report_content = full_ai_output.split("---REPORT_START---")[1].split("---REPORT_END---")[0].strip()
                if "---RESUME_START---" in full_ai_output and "---RESUME_END---" in full_ai_output:
                    best_resume_content = full_ai_output.split("---RESUME_START---")[1].split("---RESUME_END---")[0].strip()
                
                st.session_state['report_view'] = report_content
                st.session_state['resume_view'] = best_resume_content

# Display results in beautifully isolated UI Tabs if processing state is active
if 'report_view' in st.session_state and 'resume_view' in st.session_state:
    
    # Create two clear display tabs
    tab1, tab2 = st.tabs(["📊 ATS Score & Gap Report", "✨ Fully Rewritten Perfect Resume"])
    
    with tab1:
        st.markdown(st.session_state['report_view'])
        
    with tab2:
        st.markdown("### 🛠️ Tailored Resume Preview")
        st.info("The experience data below has been fully updated using the standard metrics-driven X-Y-Z impact format.")
        st.text_area("Copy Text Version:", value=st.session_state['resume_view'], height=400)
        
        st.markdown("### 📥 Download Clean Document Exports")
        dl_word, dl_pdf = st.columns(2)
        with dl_word:
            st.download_button(
                label="Download New Resume as Word (.docx)",
                data=generate_docx(st.session_state['resume_view']),
                file_name="Optimized_Target_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with dl_pdf:
            st.download_button(
                label="Download New Resume as PDF (.pdf)",
                data=generate_pdf(st.session_state['resume_view']),
                file_name="Optimized_Target_Resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )
