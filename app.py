import streamlit as st
from io import BytesIO
from pypdf import PdfReader

# Securely import Google GenAI
try:
    from google import genai
except ImportError:
    st.error("The 'google-genai' package is missing. Please run 'pip install google-genai' in your terminal.")

# Import Document generation tools
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ---------------------------------------------------------------------------
# 1. LUXURY GLASSMORPHISM STYLING ENGINE
# ---------------------------------------------------------------------------

def apply_premium_ui():
    """Injects high-end, modern dashboard design into Streamlit."""
    st.markdown("""
        <style>
        /* Modern Background & Global Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(135deg, #090d16 0%, #111827 100%);
            color: #f3f4f6;
            font-family: 'Inter', sans-serif;
        }
        
        /* Dashboard App Title */
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }
        
        /* Form Card Containers */
        div[data-testid="stVerticalBlock"] > div {
            background: rgba(17, 24, 39, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
        }
        
        /* Premium Action Button styling */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%) !important;
            color: #ffffff !important;
            border: none !important;
            padding: 16px 32px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            cursor: pointer !important;
            box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4) !important;
            transition: all 0.25s ease-in-out !important;
        }
        
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 25px rgba(14, 165, 233, 0.6) !important;
        }
        
        /* Dynamic Tab UI Fixes */
        .stTabs [data-baseweb="tab"] {
            color: #9ca3af !important;
            font-weight: 600 !important;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #38bdf8 !important;
            border-bottom-color: #38bdf8 !important;
        }
        
        /* Clean Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #070a12 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. CORE APPLICATION ENGINES
# ---------------------------------------------------------------------------

def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF data: {e}")
        return ""

def generate_optimized_resume_data(api_key, resume_text, job_description):
    try:
        client = genai.Client(api_key=api_key)
        
        # Explicit instructions to create a standard structured resume block
        prompt = f"""
        You are an elite Executive Tech Recruiter. Analyze this [CURRENT RESUME] against the [TARGET JOB DESCRIPTION].
        
        Perform two actions:
        1. Compile a crisp ATS feedback summary report.
        2. Format and rewrite their details into a beautifully structured, elegant, professional resume layout.

        CRITICAL WRITING RULE: For the Experience section, translate all achievements using the Google X-Y-Z Formula: 
        "Accomplished [X] as measured by [Y], by doing [Z]". Use metrics, percentages, and performance indicators.

        You must separate your output using the specific tags below:
        
        ---REPORT_START---
        ### 📊 ATS Score Analysis
        **Match Rating:** [Provide a hard percentage out of 100%]
        
        ### 🔍 High-Priority Keywords Missing
        - [Provide core missing skills]
        
        ### 🛠️ Strategic Structural Gaps
        - [Provide advice on formatting or role gaps]
        ---REPORT_END---
        
        ---RESUME_START---
        ========================================================================
        [CANDIDATE FULL NAME]
        [City, State | Phone Number | Email Address | LinkedIn URL]
        ========================================================================

        PROFESSIONAL SUMMARY
        ------------------------------------------------------------------------
        [Write a modern, elegant 3-sentence summary tailored to this target position]

        CORE TECHNICAL EXPERTISE
        ------------------------------------------------------------------------
        - [Skill Category 1]: Skill A, Skill B, Skill C
        - [Skill Category 2]: Skill D, Skill E, Skill F

        PROFESSIONAL EXPERIENCE
        ------------------------------------------------------------------------
        [Company Name] | [Job Title]
        [Employment Dates (e.g., Month Year – Present)]
        - Worked in a high-impact team to achieve [X], evaluated by [Y], through implementing [Z].
        - Re-engineered core performance architectures resulting in [X]% improvement by doing [Z].

        EDUCATION & CERTIFICATIONS
        ------------------------------------------------------------------------
        [Degree Title] | [University Name] (Graduation Year)
        - Relevant Coursework or Academic Distinctions
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
        return f"AI Connection Error: {e}."

# ---------------------------------------------------------------------------
# 3. CLEAN DOCUMENT EXPORT DRIVERS
# ---------------------------------------------------------------------------

def generate_docx(resume_text):
    doc = Document()
    for line in resume_text.split('\n'):
        line_clean = line.strip()
        if not line_clean:
            continue
        if line_clean.startswith('====') or line_clean.startswith('----'):
            continue
        if line_clean in ['PROFESSIONAL SUMMARY', 'CORE TECHNICAL EXPERTISE', 'PROFESSIONAL EXPERIENCE', 'EDUCATION & CERTIFICATIONS']:
            doc.add_heading(line_clean, level=1)
        elif line_clean.startswith('- '):
            doc.add_paragraph(line_clean[2:], style='List Bullet')
        else:
            doc.add_paragraph(line_clean)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def generate_pdf(resume_text):
    bio = BytesIO()
    doc = SimpleDocTemplate(bio, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for line in resume_text.split('\n'):
        line_clean = line.strip().replace('====', '').replace('----', '').strip()
        if not line_clean:
            continue
        if line_clean in ['PROFESSIONAL SUMMARY', 'CORE TECHNICAL EXPERTISE', 'PROFESSIONAL EXPERIENCE', 'EDUCATION & CERTIFICATIONS']:
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"<b>{line_clean}</b>", styles['Heading2']))
            story.append(Spacer(1, 4))
        elif line.strip().startswith('-'):
            story.append(Paragraph(f"• {line_clean[1:].strip()}", styles['Normal']))
        else:
            story.append(Paragraph(line_clean, styles['Normal']))
    doc.build(story)
    bio.seek(0)
    return bio

# ---------------------------------------------------------------------------
# 4. INTERFACE ARCHITECTURE
# ---------------------------------------------------------------------------

st.set_page_config(page_title="AI Resume Architect Pro", page_icon="💼", layout="wide")
apply_premium_ui()

st.markdown("<div class='main-title'>💼 AI Resume ATS Architect Pro</div>", unsafe_allow_html=True)
st.write("Constructing structured, recruiter-ready resumes engineered for Applicant Tracking Systems.")

with st.sidebar:
    st.markdown("### 🔑 Secure Credentials")
    api_key_input = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("---")
    st.caption("Engine: Gemini-2.5-Flash")
    st.caption("Standard: Google X-Y-Z Metric Alignment")

# Layout Panels
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 Step 1: Target Position Parameters")
    job_description = st.text_area(
        "Paste the Job Description here:", 
        height=260, 
        placeholder="Paste target core responsibilities, tool stacks, or engineering demands..."
    )

with col2:
    st.markdown("### 📄 Step 2: Source File Upload")
    uploaded_file = st.file_uploader(
        "Upload Current Resume (PDF Layout):", 
        type=["pdf"]
    )

st.markdown("<br>", unsafe_allow_html=True)

if st.button("Optimize Profile Layout & Metrics", use_container_width=True):
    if not api_key_input:
        st.warning("Please insert your API Key in the left configuration sidebar.")
    elif not job_description:
        st.warning("Please paste a job description context profile.")
    elif not uploaded_file:
        st.warning("Please provide a source PDF file template.")
    else:
        with st.spinner("Processing deep analysis matrices and re-building text profiles..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            if raw_text:
                ai_output = generate_optimized_resume_data(api_key_input, raw_text, job_description)
                
                report_data = "Error processing data layers..."
                resume_data = "Error running structural optimization drafts..."
                
                if "---REPORT_START---" in ai_output and "---REPORT_END---" in ai_output:
                    report_data = ai_output.split("---REPORT_START---")[1].split("---REPORT_END---")[0].strip()
                if "---RESUME_START---" in ai_output and "---RESUME_END---" in ai_output:
                    resume_data = ai_output.split("---RESUME_START---")[1].split("---RESUME_END---")[0].strip()
                
                st.session_state['report_view'] = report_data
                st.session_state['resume_view'] = resume_data

# Formatted Output Display
if 'report_view' in st.session_state and 'resume_view' in st.session_state:
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 ATS Benchmark Report", "✨ Engineered Professional Resume"])
    
    with tab1:
        st.markdown(st.session_state['report_view'])
        
    with tab2:
        st.markdown("### 📄 Optimized Document Preview")
        st.caption("This layout displays your structured, newly rewritten content blocks ready for corporate submission.")
        
        # Display the text box in a neat resume-looking container
        st.text_area("Live Text Structure:", value=st.session_state['resume_view'], height=450)
        
        st.markdown("### 📥 Save Premium Document Files")
        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                label="Download as Polished Word Document (.docx)",
                data=generate_docx(st.session_state['resume_view']),
                file_name="ATS_Optimized_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with d2:
            st.download_button(
                label="Download as Standard PDF (.pdf)",
                data=generate_pdf(st.session_state['resume_view']),
                file_name="ATS_Optimized_Resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )
