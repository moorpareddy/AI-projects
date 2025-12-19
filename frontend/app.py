"""
Streamlit Frontend - Interactive UI for Resume Analysis
Beautiful, user-friendly interface for uploading resumes and viewing analysis
"""
import streamlit as st
import requests
import json
import time
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer & Job Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .skill-tag {
        display: inline-block;
        background-color: #d4edda;
        color: #155724;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    .missing-skill-tag {
        display: inline-block;
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    .verdict-strong {
        color: #28a745;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .verdict-moderate {
        color: #ffc107;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .verdict-weak {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"


def check_api_health() -> bool:
    """Check if the backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def analyze_resume(resume_file, job_description: str) -> Optional[dict]:
    """
    Send resume and job description to API for analysis
    
    Args:
        resume_file: Uploaded resume file
        job_description: Job description text
        
    Returns:
        Analysis result dictionary or None if error
    """
    try:
        files = {"resume_file": ("resume.pdf", resume_file, "application/pdf")}
        data = {"job_description": job_description}
        
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            files=files,
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None


def display_match_score(score: float):
    """Display match score with progress bar and color coding"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎯 Overall Match Score")
        
        # Color based on score
        if score >= 75:
            color = "#28a745"  # Green
        elif score >= 50:
            color = "#ffc107"  # Yellow
        else:
            color = "#dc3545"  # Red
        
        # Progress bar
        st.markdown(f"""
            <div style="background-color: #e0e0e0; border-radius: 1rem; height: 2rem; overflow: hidden;">
                <div style="background-color: {color}; width: {score}%; height: 100%; 
                            display: flex; align-items: center; justify-content: center; 
                            color: white; font-weight: bold; font-size: 1.2rem;">
                    {score:.1f}%
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)


def display_scores_breakdown(scores: dict):
    """Display detailed score breakdown"""
    st.markdown("### 📊 Score Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Skills Match",
            f"{scores['skills_match_score']:.1f}%",
            help="How well your skills match the job requirements"
        )
    
    with col2:
        st.metric(
            "Experience Relevance",
            f"{scores['experience_relevance_score']:.1f}%",
            help="How well your experience matches the requirements"
        )
    
    with col3:
        st.metric(
            "Semantic Similarity",
            f"{scores['semantic_similarity_score']:.1f}%",
            help="AI-based contextual similarity between resume and job"
        )
    
    with col4:
        st.metric(
            "Resume Quality",
            f"{scores['resume_quality_score']:.1f}%",
            help="Overall quality and presentation of your resume"
        )


def display_skills_comparison(skills_comp: dict):
    """Display skills comparison"""
    st.markdown("### 🔍 Skills Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✅ Matching Skills**")
        if skills_comp['matching_skills']:
            for skill in skills_comp['matching_skills']:
                st.markdown(f'<span class="skill-tag">{skill}</span>', unsafe_allow_html=True)
        else:
            st.info("No matching skills found")
    
    with col2:
        st.markdown("**❌ Missing Required Skills**")
        if skills_comp['missing_required_skills']:
            for skill in skills_comp['missing_required_skills']:
                st.markdown(f'<span class="missing-skill-tag">{skill}</span>', unsafe_allow_html=True)
        else:
            st.success("You have all required skills!")
    
    if skills_comp.get('missing_preferred_skills'):
        st.markdown("**⚠️ Missing Preferred Skills**")
        for skill in skills_comp['missing_preferred_skills']:
            st.markdown(f'<span class="missing-skill-tag">{skill}</span>', unsafe_allow_html=True)


def display_improvements(suggestions: list):
    """Display improvement suggestions"""
    st.markdown("### 💡 Improvement Suggestions")
    
    # Group by priority
    high_priority = [s for s in suggestions if s['priority'] == 'high']
    medium_priority = [s for s in suggestions if s['priority'] == 'medium']
    low_priority = [s for s in suggestions if s['priority'] == 'low']
    
    if high_priority:
        st.markdown("**🔴 High Priority**")
        for suggestion in high_priority:
            with st.expander(f"[{suggestion['category'].upper()}] {suggestion['suggestion'][:80]}..."):
                st.write(f"**Suggestion:** {suggestion['suggestion']}")
                st.write(f"**Impact:** {suggestion['impact']}")
    
    if medium_priority:
        st.markdown("**🟡 Medium Priority**")
        for suggestion in medium_priority:
            with st.expander(f"[{suggestion['category'].upper()}] {suggestion['suggestion'][:80]}..."):
                st.write(f"**Suggestion:** {suggestion['suggestion']}")
                st.write(f"**Impact:** {suggestion['impact']}")
    
    if low_priority:
        st.markdown("**🟢 Low Priority**")
        for suggestion in low_priority:
            with st.expander(f"[{suggestion['category'].upper()}] {suggestion['suggestion'][:80]}..."):
                st.write(f"**Suggestion:** {suggestion['suggestion']}")
                st.write(f"**Impact:** {suggestion['impact']}")


def display_optimized_bullets(bullets: list):
    """Display optimized resume bullet points"""
    st.markdown("### ✨ Optimized Resume Bullets")
    
    if not bullets:
        st.info("No bullet points to optimize")
        return
    
    for i, bullet in enumerate(bullets, 1):
        with st.expander(f"Bullet Point {i}"):
            st.markdown("**📝 Original:**")
            st.write(bullet['original'])
            
            st.markdown("**✨ Optimized:**")
            st.success(bullet['optimized'])
            
            st.markdown("**💭 Why this is better:**")
            st.info(bullet['improvement_reason'])


def display_verdict(result: dict):
    """Display final verdict"""
    st.markdown("### 🎓 Final Verdict")
    
    verdict = result['final_verdict']
    
    # Style based on verdict
    if verdict == "Strong Match":
        verdict_class = "verdict-strong"
        icon = "🌟"
    elif verdict == "Moderate Match":
        verdict_class = "verdict-moderate"
        icon = "⭐"
    else:
        verdict_class = "verdict-weak"
        icon = "💫"
    
    st.markdown(f'<p class="{verdict_class}">{icon} {verdict}</p>', unsafe_allow_html=True)
    st.write(result['verdict_explanation'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💪 Key Strengths:**")
        for strength in result.get('key_strengths', []):
            st.write(f"- {strength}")
    
    with col2:
        st.markdown("**🎯 Areas to Improve:**")
        for weakness in result.get('key_weaknesses', []):
            st.write(f"- {weakness}")
    
    if result.get('ats_score'):
        st.markdown(f"**🤖 ATS Score:** {result['ats_score']:.1f}%")
        st.caption("Estimated score from Applicant Tracking Systems")


def main():
    """Main application"""
    
    # Header
    st.markdown('<p class="main-header">📄 Resume Analyzer & Job Matcher</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Resume Analysis with Match Scoring & Improvement Suggestions</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/200/resume.png", width=150)
        st.markdown("## About")
        st.info("""
        This tool uses advanced AI to:
        - 📊 Score your resume against job descriptions
        - 🔍 Identify matching & missing skills
        - 💡 Provide actionable improvement tips
        - ✨ Optimize your resume bullets
        - 🎯 Give hiring recommendations
        """)
        
        st.markdown("## How to Use")
        st.markdown("""
        1. Upload your resume (PDF)
        2. Paste the job description
        3. Click **Analyze Resume**
        4. Get instant feedback!
        """)
        
        # API Health Check
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Disconnected")
            st.warning("Please start the backend server: `python -m backend.main`")
    
    # Main Content
    tab1, tab2 = st.tabs(["📤 Analyze", "ℹ️ Info"])
    
    with tab1:
        # Check API health first
        if not check_api_health():
            st.error("⚠️ Backend API is not running. Please start the server first.")
            st.code("python -m backend.main", language="bash")
            return
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📄 Upload Resume")
            resume_file = st.file_uploader(
                "Choose your resume (PDF only)",
                type=['pdf'],
                help="Upload your resume in PDF format"
            )
        
        with col2:
            st.markdown("#### 📋 Job Description")
            job_description = st.text_area(
                "Paste the job description here",
                height=200,
                placeholder="""Example:
We are looking for a Senior Software Engineer with 5+ years of experience.

Required Skills:
- Python, Django, FastAPI
- PostgreSQL, Redis
- Docker, Kubernetes
- AWS

Responsibilities:
- Design and build scalable APIs
- Lead technical projects
- Mentor junior engineers
                """,
                help="Paste the complete job description"
            )
        
        # Analyze button
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("🚀 Analyze Resume", type="primary", use_container_width=True)
        
        if analyze_button:
            if not resume_file:
                st.warning("⚠️ Please upload a resume")
            elif not job_description or len(job_description.strip()) < 20:
                st.warning("⚠️ Please provide a job description (at least 20 characters)")
            else:
                with st.spinner("🔄 Analyzing your resume... This may take 30-60 seconds..."):
                    # Reset file pointer
                    resume_file.seek(0)
                    
                    # Call API
                    result = analyze_resume(resume_file, job_description)
                    
                    if result and result.get('success'):
                        st.success("✅ Analysis complete!")
                        
                        analysis = result['result']
                        
                        # Display results
                        st.markdown("---")
                        display_match_score(analysis['match_score'])
                        
                        st.markdown("---")
                        display_scores_breakdown(analysis['scores_breakdown'])
                        
                        st.markdown("---")
                        display_verdict(analysis)
                        
                        st.markdown("---")
                        display_skills_comparison(analysis['skills_comparison'])
                        
                        st.markdown("---")
                        display_improvements(analysis['improvement_suggestions'])
                        
                        st.markdown("---")
                        display_optimized_bullets(analysis['optimized_resume_bullets'])
                        
                        # Processing time
                        st.caption(f"⏱️ Processing time: {result.get('processing_time_seconds', 0):.2f} seconds")
                    else:
                        st.error("❌ Analysis failed. Please check the error message above.")
    
    with tab2:
        st.markdown("## 📖 How It Works")
        
        st.markdown("""
        ### Analysis Pipeline
        
        1. **PDF Parsing**: Extracts text from your resume
        2. **Information Extraction**: Uses LLM to identify skills, experience, education
        3. **Job Analysis**: Parses job requirements and qualifications
        4. **Semantic Matching**: Computes AI-based similarity between resume and job
        5. **Skills Comparison**: Matches your skills against requirements
        6. **Scoring**: Calculates weighted match score across multiple dimensions
        7. **Recommendations**: Generates personalized improvement suggestions
        8. **Optimization**: Provides enhanced resume bullet points
        
        ### Scoring Methodology
        
        Your overall match score is calculated as:
        - **40%** Skills Match
        - **30%** Experience Relevance
        - **20%** Semantic Similarity
        - **10%** Resume Quality
        
        ### Verdict Categories
        
        - **Strong Match** (75-100): Excellent fit, highly recommended
        - **Moderate Match** (50-74): Decent fit, some gaps to address
        - **Weak Match** (0-49): Significant gaps, may not be the best fit
        """)
        
        st.markdown("### 🔧 Tech Stack")
        st.markdown("""
        - **Backend**: FastAPI
        - **Frontend**: Streamlit
        - **AI**: OpenAI GPT-4 / Google Gemini
        - **Embeddings**: OpenAI / Sentence Transformers
        - **PDF Parsing**: pdfplumber, PyPDF2
        """)


if __name__ == "__main__":
    main()
