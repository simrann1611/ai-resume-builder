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
# 1. PREMIUM CUSTOM STYLING (THE DESIGN OVERHAUL)
# ---------------------------------------------------------------------------

def apply_custom_theme():
    """Injects high-end UI design styles into the standard Streamlit interface."""
    st.markdown("""
        <style>
        /* Base page background adjustments */
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            color: #f8fafc;
        }
        
        /* Main Header Customization */
        h1 {
            background: linear-gradient(to right, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Inter', sans-serif;
            font-weight: 800 !important;
            letter-spacing: -0.5px;
        }
        
        /* Modern Cards for upload and input sections */
        div[data-testid="stVerticalBlock"] > div {
            background-color: rgba(30, 41, 59, 0.4);
            border-radius: 16px;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Stunning Gradient Action Button */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #2563eb 0%, #4f46e5 100%) !important;
            color: white !important;
            border: none !important;
            padding: 14px 28px !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        div.stButton > button:first-child:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
            background: linear-gradient(90deg, #1d4ed8 0%, #4338ca 100%) !important;
        }
        
        /* Clean Custom look for Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #0b0f19 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Custom UI highlights for metrics and tags */
        .report-metric-box {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid #38bdf8;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. CORE APPLICATION LOGIC
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
        st.error(f"Error parsing PDF file: {e}")
        return ""

def generate_optimized_resume_data(api_key, resume_text, job_description):
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        You are an elite Tech Recruiter and expert ATS optimization engine. 
        Analyze the following [CURRENT RESUME] against the [TARGET JOB DESCRIPTION].
        
        CRITICAL TASK: You must perform two operations:
        1. Create a detailed, beautiful ATS metric evaluation report.
        2. Rewrite their entire resume into a high-scoring, perfectly tailored version.
        
        When rewriting the experience section, use the strict Google X-Y-Z Formula: 
        "Accomplished [X] as measured by [Y], by doing [Z]". Use metrics, percentages, and hard keywords where logical.

        Format your entire response using the exact layout tags below:
        
        ---REPORT_START---
        # 📈 ATS PERFORMANCE REPORT
        
        ### 🎯 Match Rating Dynamic Score
        [Provide a definitive score like "85%" with a highly descriptive, professional 2-sentence justification]
        
        ### 🔍 High-Priority Missing Keywords & Skills
        - [List core missing hard technical skills or domain terminology]
        
        ### 🛠️ Strategic Gaps & Structural Adjustments
        - [Explain structural or qualitative gaps compared to the role demands]
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
# 3. EXPORT COMPILERS
# ---------------------------------------------------------------------------

def generate_docx(resume_text):
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
# 4. USER INTERFACE DESIGN (THE CREATIVE LAYOUT)
# ---------------------------------------------------------------------------

st.set_page_config(page_title="AI ATS Resume Architect", page_icon="⚡", layout="wide")

# Activate our custom designer themes
apply_custom_theme()

st.title("⚡ AI Resume ATS Architect Pro")
st.write("A professional-grade system scanner built to engineer high-ranking, corporate-aligned CV profiles.")

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🔑 Authentication")
    api_key_input = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("---")
    st.markdown("### 🌐 Core Engine Parameters")
    st.caption("Running: **Gemini 2.5 Flash**")
    st.caption("Formula Style: **Google X-Y-Z Matrix**")

# Side-by-side workspace split
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 1. Target Target Matrix")
    job_description = st.text_area(
        "Paste the Target Job Description here:", 
        height=280, 
        placeholder="Drop qualifications, required tool stacks, or everyday execution workflows here..."
    )

with col2:
    st.markdown("### 📄 2. Profile Source Upload")
    uploaded_file = st.file_uploader(
        "Upload current Candidate Resume (PDF only):", 
        type=["pdf"]
    )

st.markdown("<br>", unsafe_allow_html=True)

# Run Button triggers smooth visual processing
if st.button("Run Advanced ATS Analysis & Auto-Rewrite", use_container_width=True):
    if not api_key_input:
        st.warning("Please input your Gemini API Key in the left sidebar layout pane.")
    elif not job_description:
        st.warning("Please supply a targeted Job Description to compare against.")
    elif not uploaded_file:
        st.warning("Please upload a PDF version of your resume.")
    else:
        with st.spinner("Analyzing profile structures and implementing X-Y-Z mathematical rewrites..."):
            raw_resume_text = extract_text_from_pdf(uploaded_file)
            if raw_resume_text:
                full_ai_output = generate_optimized_resume_data(api_key_input, raw_resume_text, job_description)
                
                report_content = "Analysis initialization anomaly..."
                best_resume_content = "Re-draft calculation error..."
                
                if "---REPORT_START---" in full_ai_output and "---REPORT_END---" in full_ai_output:
                    report_content = full_ai_output.split("---REPORT_START---")[1].split("---REPORT_END---")[0].strip()
                if "---RESUME_START---" in full_ai_output and "---RESUME_END---" in full_ai_output:
                    best_resume_content = full_ai_output.split("---RESUME_START---")[1].split("---RESUME_END---")[0].strip()
                
                st.session_state['report_view'] = report_content
                st.session_state['resume_view'] = best_resume_content

# Display processed structures inside a beautifully structured dynamic tab layout
if 'report_view' in st.session_state and 'resume_view' in st.session_state:
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # Modern Tab selectors
    tab1, tab2 = st.tabs(["📊 Diagnostic Matrix Report", "✨ Engineered Perfect Resume Draft"])
    
    with tab1:
        st.markdown(f"<div class='report-metric-box'>{st.session_state['report_view']}</div>", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("### 🛠️ Live Blueprint Preview")
        st.caption("This interactive profile draft has been fully re-aligned with missing keywords and formatted using quantifiable achievement formulas.")
        st.text_area("Plain Text Snapshot:", value=st.session_state['resume_view'], height=350)
        
        st.markdown("### 📥 Clean Document Production Portals")
        dl_word, dl_pdf = st.columns(2)
        with dl_word:
            st.download_button(
                label="Download Finished Resume (.docx)",
                data=generate_docx(st.session_state['resume_view']),
                file_name="ATS_Engineered_Resume.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
        with dl_pdf:
            st.download_button(
                label="Download Finished Resume (.pdf)",
                data=generate_pdf(st.session_state['resume_view']),
                file_name="ATS_Engineered_Resume.pdf",
                mime="application/pdf",
                use_container_width=True
            )
