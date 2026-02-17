"""
Career Navigation System - Streamlit Frontend
Interactive dashboard for complete user lifecycle management
Full-featured system: User creation, onboarding wizard, dashboard, action tracking, rerouting
"""

import streamlit as st
import json
import os
import sys
import time
from datetime import datetime

# Add parent directory to path for backend imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CRITICAL: Set default API key if not in environment
if not os.getenv("GROQ_API_KEY") and not os.getenv("GROQ_API_KEY_1"):
    os.environ["GROQ_API_KEY"] = "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"

# Initialize API Key Manager
try:    
    from backend.utils.api_key_manager import initialize_key_manager
    key_manager = initialize_key_manager()
    key_count = key_manager.get_key_count()
except ValueError as e:
    st.error(f"API Key Error: {str(e)}")
    st.stop()

# IMPORTANT: Apply request throttling BEFORE importing any backend modules
import requests

_last_request_time = 0
_min_request_interval = 1.5
_original_post = requests.post

def _throttled_post(*args, **kwargs):
    """Wrapper around requests.post that adds global throttling"""
    global _last_request_time
    
    # Only throttle Groq API requests
    url = args[0] if args else kwargs.get('url', '')
    if 'groq.com' in str(url):
        elapsed = time.time() - _last_request_time
        if elapsed < _min_request_interval:
            time.sleep(_min_request_interval - elapsed)
        _last_request_time = time.time()
    
    return _original_post(*args, **kwargs)

requests.post = _throttled_post

from backend.orchestrator import Orchestrator
from backend.user_context import UserContextManager

# Page configuration
st.set_page_config(
    page_title="Career Navigation System",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# PROFESSIONAL UI DESIGN SYSTEM - Career Navigator
# ============================================================================

st.markdown("""
<style>
    /* ===== IMPORT GOOGLE FONTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    /* ===== GLOBAL STYLES ===== */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        color: #F9FAFB;
    }
    
    /* ===== HEADINGS WITH PLAYFAIR DISPLAY ===== */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif !important;
        font-weight: 600;
    }
    
    h1 {
        font-size: 3.5rem !important;
        color: #86EFAC;
        margin-bottom: 0.75rem;
    }
    
    h2 {
        font-size: 2.5rem !important;
        color: #10B981;
        margin-top: 2.5rem;
        margin-bottom: 1.25rem;
    }
    
    h3 {
        font-size: 2rem !important;
        color: #86EFAC;
        margin-top: 2rem;
    }
    
    h4 {
        font-size: 1.5rem !important;
        color: #10B981;
    }
    
    /* ===== BODY TEXT ===== */
    p, div, span, label {
        font-family: 'Poppins', sans-serif;
        font-size: 1.1rem;
        line-height: 1.8;
        color: #E5E7EB;
    }
    
    /* ===== TEXT VARIANTS ===== */
    .secondary-text {
        color: #D1D5DB;
    }
    
    .tertiary-text {
        color: #9CA3AF;
    }
    
    /* ===== CODE BLOCKS ===== */
    code {
        font-family: 'Courier New', monospace !important;
        background-color: #1F2937;
        color: #86EFAC;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    
    pre {
        font-family: 'Courier New', monospace !important;
        background-color: #111827;
        color: #86EFAC;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* ===== CUSTOM SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #F3F4F6;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #047857 0%, #059669 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #059669 0%, #10B981 100%);
    }
    
    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.8rem 2rem !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(4, 120, 87, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 12px rgba(4, 120, 87, 0.3) !important;
        background: linear-gradient(135deg, #059669 0%, #10B981 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* ===== FORMS AND INPUT FIELDS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border: 2px solid #E5E7EB !important;
        border-radius: 8px !important;
        padding: 0.8rem 0.8rem !important;
        font-family: 'Poppins', sans-serif !important;
        transition: all 0.3s ease !important;
        background-color: white !important;
        color: #000000 !important;
        font-size: 1.05rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #047857 !important;
        box-shadow: 0 0 0 3px rgba(4, 120, 87, 0.1) !important;
        outline: none !important;
    }
    
    /* ===== CARD COMPONENT ===== */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border: 1px solid #E5E7EB;
    }
    
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
    
    /* ===== METRIC CARDS ===== */
    .stMetric {
        background: #000000 !important;
        padding: 1.5rem !important;
        border-radius: 10px !important;
        border: 1px solid #333333 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        color: #86EFAC !important;
    }
    
    .stMetric label {
        color: #9CA3AF !important;
        font-size: 0.95rem !important;
    }
    
    /* ===== ALERTS ===== */
    .alert {
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
        font-family: 'Poppins', sans-serif;
    }
    
    .alert-success {
        background-color: #064E3B;
        border-color: #10B981;
        color: #ECFDF5;
    }
    
    .alert-warning {
        background-color: #5A3A1C;
        border-color: #FBBF24;
        color: #FEF3C7;
    }
    
    .alert-error {
        background-color: #5A1F1F;
        border-color: #F87171;
        color: #FEE2E2;
    }
    
    .alert-info {
        background-color: #1E3A8A;
        border-color: #60A5FA;
        color: #DBEAFE;
    }
    
    .stSuccess {
        background-color: #ECFDF5 !important;
        border: 1.5px solid #059669 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stWarning {
        background-color: #FFFBEB !important;
        border: 1.5px solid #F59E0B !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stError {
        background-color: #FEF2F2 !important;
        border: 1.5px solid #EF4444 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stInfo {
        background-color: #EFF6FF !important;
        border: 1.5px solid #3B82F6 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent !important;
        border-bottom: 3px solid #E5E7EB !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #9CA3AF !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 1rem 0 !important;
        position: relative;
    }
    
    .stTabs [aria-selected="true"] {
        color: #86EFAC !important;
    }
    
    .stTabs [aria-selected="true"]::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #047857 0%, #059669 100%);
        border-radius: 2px 2px 0 0;
    }
    
    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 8px;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
        color: #86EFAC;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #064E3B 0%, #1F2937 100%);
        border-color: #86EFAC;
    }
    
    .stExpander {
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F9FAFB 0%, white 100%) !important;
        border-right: 1px solid #E5E7EB !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #86EFAC !important;
    }
    
    /* ===== MAIN HEADER WITH GRADIENT ===== */
    .header-container {
        background: linear-gradient(135deg, #047857 0%, #059669 100%);
        color: white;
        padding: 3.5rem 3rem;
        border-radius: 16px;
        margin-bottom: 3.5rem;
        box-shadow: 0 8px 20px rgba(4, 120, 87, 0.4);
    }
    
    .header-title {
        font-size: 6.5rem !important;
        font-weight: 800 !important;
        color: white !important;
        margin: 0 !important;
        display: flex;
        align-items: center;
        gap: 2rem;
        line-height: 1;
    }
    
    .header-title i {
        font-size: 3rem;
        color: white;
    }
    
    .header-subtitle {
        font-size: 1.35rem !important;
        color: rgba(240, 253, 250, 0.95) !important;
        margin-top: 1.2rem !important;
        font-weight: 400 !important;
        line-height: 1.5;
    }
    
    .main-header {
        background: linear-gradient(135deg, #047857 0%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(4, 120, 87, 0.2);
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
    }
    
    .main-header p {
        color: rgba(240, 253, 250, 0.95);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* ===== DATAFRAMES ===== */
    .stDataFrame {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* ===== PROGRESS BAR ===== */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #a6b5b0 100%, #a6b5b0 100%) !important;
    }
    
    /* ===== CHECKBOX AND RADIO ===== */
    .stCheckbox, .stRadio {
        font-family: 'Poppins', sans-serif;
    }
    
    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {
        border: 2px dashed #E5E7EB !important;
        border-radius: 8px !important;
        padding: 2rem !important;
        background-color: #F9FAFB !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #047857 !important;
        background-color: #ECFDF5 !important;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session():
    """Initialize session state"""
    if "orch" not in st.session_state:
        st.session_state.orch = Orchestrator()
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "context" not in st.session_state:
        st.session_state.context = None
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 1
    if "onboarding_data" not in st.session_state:
        st.session_state.onboarding_data = {}
    if "refresh_context" not in st.session_state:
        st.session_state.refresh_context = False
    
    # Refresh context if needed (after path change)
    if st.session_state.refresh_context and st.session_state.user_id:
        st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
        st.session_state.refresh_context = False


def get_all_users():
    """Get list of all existing users from data directory"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "user_contexts")
    
    if not os.path.exists(data_dir):
        return []
    
    users = []
    for file in os.listdir(data_dir):
        if file.endswith("_context.json"):
            user_id = file.replace("_context.json", "")
            users.append(user_id)
    
    return sorted(users)


def page_home():
    """Home page - User selection and creation"""
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("<h3><i class='fas fa-user'></i> Select Existing User</h3>", unsafe_allow_html=True)
        
        existing_users = get_all_users()
        
        if existing_users:
            selected_user = st.selectbox("Choose a user:", existing_users, label_visibility="collapsed")
            
            if st.button(" Load User Profile", width="stretch"):
                st.session_state.user_id = selected_user
                st.session_state.context = st.session_state.orch.get_student_context(selected_user)
                st.session_state.page = "dashboard"
                st.rerun()
        else:
            st.info("No existing users yet. Create one below!")
    
    with col2:
        st.markdown("<h3><i class='fas fa-star'></i> Create New User</h3>", unsafe_allow_html=True)
        
        with st.form("create_user_form", border=True):
            new_user_id = st.text_input(
                "Enter new user ID:",
                placeholder="e.g., Sudarmani",
                help="Unique identifier for the student"
            )
            
            submitted = st.form_submit_button(" Start Onboarding", width="stretch", use_container_width=True)
            
            if submitted:
                if not new_user_id:
                    st.error("Please enter a user ID")
                else:
                    st.session_state.user_id = new_user_id
                    st.session_state.page = "onboarding"
                    st.session_state.onboarding_step = 1
                    st.session_state.onboarding_data = {}
                    st.rerun()
    
    st.markdown("---")
    
    st.markdown("<h3><i class='fas fa-book'></i> About This System</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<h4><i class='fas fa-bullseye'></i> Personalized Guidance</h4>", unsafe_allow_html=True)
        st.write("Get career paths tailored to your profile, skills, and market conditions.")
    
    with col2:
        st.markdown("<h4><i class='fas fa-chart-bar'></i> Real-time Feedback</h4>", unsafe_allow_html=True)
        st.write("Track progress, receive insights, and get recommendations for staying on track.")
    
    with col3:
        st.markdown("<h4><i class='fas fa-exchange-alt'></i> Flexible Navigation</h4>", unsafe_allow_html=True)
        st.write("Switch paths if needed, with analysis of alternatives and success probabilities.")


def page_onboarding():
    """Onboarding wizard - 3 step process"""
    st.markdown("# Student Onboarding Wizard")
    
    # Progress bar
    progress = st.session_state.onboarding_step / 3
    st.progress(progress)
    st.write(f"Step {st.session_state.onboarding_step} of 3")
    
    if st.session_state.onboarding_step == 1:
        page_onboarding_step1()
    elif st.session_state.onboarding_step == 2:
        page_onboarding_step2()
    elif st.session_state.onboarding_step == 3:
        page_onboarding_step3()


def page_onboarding_step1():
    """Step 1: Basic Information"""
    st.markdown("## Step 1: Basic Information")
    
    with st.form("step1_form", border=False):
        col1, col2 = st.columns(2)
        
        with col1:
            experience_level = st.selectbox(
                "Experience Level:",
                ["Fresh Graduate", "Junior (1-2 years)", "Mid-level (2-5 years)", "Senior (5+ years)"]
            )
            
            learning_capacity = st.selectbox(
                "Learning Capacity:",
                ["High", "Medium", "Low"]
            )
        
        with col2:
            education = st.text_input(
                "Education Background:",
                placeholder="e.g., Bachelor in Computer Science"
            )
            
            specialization = st.text_input(
                "Current Specialization:",
                placeholder="e.g., Web Development, Data Science"
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            years_experience = st.number_input(
                "Years of Professional Experience:",
                min_value=0,
                max_value=50,
                value=0
            )
        
        with col2:
            location = st.text_input(
                "Location/Region:",
                placeholder="e.g., United States, India"
            )
        
        st.markdown("### Technical Skills")
        
        col1, col2 = st.columns(2)
        
        with col1:
            programming_langs = st.multiselect(
                "Programming Languages:",
                ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "Others"],
                help="Select all that apply"
            )
        
        with col2:
            frameworks = st.multiselect(
                "Frameworks/Tools:",
                ["React", "Django", "FastAPI", "Spring", "Kubernetes", "AWS", "Azure", "Others"],
                help="Select all that apply"
            )
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if st.form_submit_button("Next Step →", width="stretch"):
                st.session_state.onboarding_data["experience_level"] = experience_level
                st.session_state.onboarding_data["learning_capacity"] = learning_capacity
                st.session_state.onboarding_data["education"] = education
                st.session_state.onboarding_data["specialization"] = specialization
                st.session_state.onboarding_data["years_experience"] = years_experience
                st.session_state.onboarding_data["location"] = location
                st.session_state.onboarding_data["programming_langs"] = programming_langs
                st.session_state.onboarding_data["frameworks"] = frameworks
                
                st.session_state.onboarding_step = 2
                st.rerun()
        
        with col1:
            pass


def page_onboarding_step2():
    """Step 2: Background & Projects"""
    st.markdown("## Step 2: Background & Projects")
    
    with st.form("step2_form", border=False):
        col1, col2 = st.columns(2)
        
        with col1:
            strength_areas = st.multiselect(
                "Strength Areas:",
                ["Problem Solving", "System Design", "Code Quality", "Leadership", 
                 "Communication", "Fast Learner", "Attention to Detail", "Others"],
                help="What are you good at?"
            )
            
            risk_factors = st.multiselect(
                "Risk Factors:",
                ["Limited networking", "Imposter syndrome", "Gaps in knowledge", 
                 "Geographic constraints", "Time constraints", "Financial constraints", "Others"],
                help="What concerns do you have?"
            )
        
        with col2:
            target_role = st.text_input(
                "Target Role/Position:",
                placeholder="e.g., Senior Software Engineer, Product Manager",
                help="What role are you aiming for?"
            )
            
            motivation = st.slider(
                "Motivation Level (1-10):",
                1, 10, 7,
                help="How motivated are you to achieve your goal?"
            )
        
        st.markdown("### Recent Projects")
        
        projects_text = st.text_area(
            "Describe your recent projects (one per line):",
            placeholder="Project 1: Built web app with React and Node.js\nProject 2: Implemented ML model for classification",
            height=120
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("← Previous", width="stretch"):
                st.session_state.onboarding_step = 1
                st.rerun()
        
        with col2:
            if st.form_submit_button("Next Step →", width="stretch"):
                st.session_state.onboarding_data["strength_areas"] = strength_areas
                st.session_state.onboarding_data["risk_factors"] = risk_factors
                st.session_state.onboarding_data["target_role"] = target_role
                st.session_state.onboarding_data["motivation"] = motivation
                st.session_state.onboarding_data["projects"] = [p.strip() for p in projects_text.split("\n") if p.strip()]
                
                st.session_state.onboarding_step = 3
                st.rerun()


def page_onboarding_step3():
    """Step 3: Timeline & Goals"""
    st.markdown("## Step 3: Timeline & Goals")
    
    with st.form("step3_form", border=False):
        col1, col2 = st.columns(2)
        
        with col1:
            timeline_months = st.number_input(
                "Target Timeline (months):",
                min_value=1,
                max_value=120,
                value=12,
                help="How long are you willing to invest?"
            )
            
            weekly_commitment = st.selectbox(
                "Weekly Time Commitment:",
                ["10-15 hours/week", "15-25 hours/week", "25-40 hours/week", "40+ hours/week"],
                help="How much time can you dedicate?"
            )
        
        with col2:
            availability = st.selectbox(
                "Learning Availability:",
                ["Full-time", "Part-time (working)", "Student", "Flexible"],
                help="What is your current situation?"
            )
            
            learning_style = st.multiselect(
                "Preferred Learning Style:",
                ["Hands-on projects", "Online courses", "Mentoring", "Books", "Videos", "Workshops"],
                help="How do you learn best?"
            )
        
        st.markdown("### Career Vision")
        
        vision = st.text_area(
            "Describe your ideal career future (3-5 years):",
            placeholder="What does success look like to you? Where do you see yourself?",
            height=120
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("← Previous", width="stretch"):
                st.session_state.onboarding_step = 2
                st.rerun()
        
        with col2:
            if st.form_submit_button("Complete Onboarding & Generate Path", width="stretch", type="primary"):
                st.session_state.onboarding_data["timeline_months"] = timeline_months
                st.session_state.onboarding_data["weekly_commitment"] = weekly_commitment
                st.session_state.onboarding_data["availability"] = availability
                st.session_state.onboarding_data["learning_style"] = learning_style
                st.session_state.onboarding_data["vision"] = vision
                
                # Process onboarding
                with st.spinner("Creating student profile and generating career path..."):
                    result = st.session_state.orch.onboard_student(
                        st.session_state.user_id,
                        st.session_state.onboarding_data
                    )
                    
                    if result["status"] == "success":
                        st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                        st.session_state.page = "onboarding_questions"
                        st.rerun()
                    else:
                        st.error(f"Error during onboarding: {result.get('message', 'Unknown error')}")


def page_onboarding_questions():
    """Display diagnostic questions after onboarding"""
    st.markdown("## Diagnostic Questions")
    st.write("Please answer these questions to help us assess your readiness for this career path.")
    
    context = st.session_state.context
    questions = context["readiness"].get("diagnostic_questions", [])
    
    if not questions:
        st.warning("No diagnostic questions generated. Proceeding to dashboard.")
        if st.button("Continue to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    with st.form("diagnostic_form", border=False):
        answers = []
        
        for i, q in enumerate(questions):
            st.markdown(f"**Question {q.get('question_number', i+1)}**")
            st.write(q.get("question", ""))
            
            answer = st.text_area(
                f"Your answer:",
                key=f"answer_{i}",
                height=80,
                placeholder="Provide a detailed answer..."
            )
            answers.append(answer)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("← Go Back", width="stretch"):
                st.session_state.page = "onboarding"
                st.session_state.onboarding_step = 3
                st.rerun()
        
        with col2:
            if st.form_submit_button("Submit Answers & Go to Dashboard", width="stretch", type="primary"):
                with st.spinner("Evaluating your answers..."):
                    # Store answers in context
                    context["readiness"]["diagnostic_answers"] = answers
                    st.session_state.orch.context_manager.save_context(st.session_state.user_id, context)
                    
                    st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                    st.session_state.page = "dashboard"
                    st.rerun()



def display_overview(context):
    """Display overview tab"""
    st.markdown("<h3><i class='fas fa-list-check'></i> Key Metrics</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        confidence = context["readiness"].get("confidence_score", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Confidence Score</div>
            <div class="metric-value">{confidence:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        market_analysis = context.get("market_context", {}).get("target_role_analysis")
        demand = market_analysis.get("demand_score", 0) if market_analysis else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market Demand</div>
            <div class="metric-value">{demand}/100</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        path = context.get("active_path", {})
        success_prob = path.get("success_probability", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">{success_prob*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        completed = len(context["current_actions"].get("completed_actions", []))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Actions Done</div>
            <div class="metric-value">{completed}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show rerouting prompt if confidence score is below 50
    confidence = context["readiness"].get("confidence_score", 0)
    if confidence < 50:
        st.markdown("### <i class='fas fa-triangle-exclamation'></i> Path Confidence Alert", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.warning(f"Your confidence in this path is currently at **{confidence:.2f}/1.0**. You may want to consider switching to an easier target role for better success probability.")
        
        with col2:
            if st.button("View Easier Paths", width="stretch", type="primary"):
                st.session_state.show_easier_paths = True
                st.rerun()
        
        st.markdown("---")
    
    # Display easier paths if user requested them
    if hasattr(st.session_state, 'show_easier_paths') and st.session_state.show_easier_paths:
        st.markdown("<h3><i class='fas fa-road'></i> Available Easier Paths</h3>", unsafe_allow_html=True)
        market_analysis = context.get("market_context", {}).get("target_role_analysis", {})
        safer_roles = market_analysis.get("adjacent_safer_roles", [])
        
        for idx, alt_role in enumerate(safer_roles, 1):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{idx}. {alt_role.get('role', 'N/A')}**")
                st.caption(f"Demand: {alt_role.get('demand_score', 0)}/100 | Entry Barrier: {alt_role.get('entry_barrier', 'N/A')}")
                st.write(f"*{alt_role.get('reason', 'N/A')}*")
            
            with col2:
                if st.button("Switch", key=f"switch_easier_{idx}", width="stretch", type="primary"):
                    alt_path = {
                        "new_target_role": alt_role.get("role"),
                        "why_better_fit": alt_role.get("reason"),
                        "success_probability": alt_role.get("demand_score", 75) / 100.0,
                        "estimated_duration_months": 6
                    }
                    with st.spinner("Switching to this path..."):
                        result = st.session_state.orch.apply_alternative_path(
                            st.session_state.user_id,
                            alt_path,
                            path_type="alternative"
                        )
                        if result["status"] == "success":
                            st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                            st.session_state.show_easier_paths = False
                            st.success(f"✅ Switched to {alt_role.get('role')}! New roadmap generated.")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('message')}")
        
        st.markdown("---")
        
        if st.button("Cancel - Go Back", width="stretch"):
            st.session_state.show_easier_paths = False
            st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Assessment")
        risk = context["readiness"].get("deviation_risk", "medium")
        risk_color = {"low": "green", "medium": "orange", "high": "red"}
        st.markdown(f"<span style='color:{risk_color.get(risk, 'gray')};font-size:1.2rem'>Deviation Risk: **{risk.upper()}**</span>", unsafe_allow_html=True)
        
        # Dynamically calculate deviations from current_actions
        current_actions = context.get("current_actions", {})
        pending_count = len(current_actions.get("pending_actions", []))
        completed_count = len(current_actions.get("completed_actions", []))
        
        if pending_count > 0:
            st.write("**Pending Actions:**")
            for action in current_actions.get("pending_actions", [])[:3]:
                status_icon = "⏳" if action.get("status") == "in_progress" else "⭕"
                title = action.get('title', 'N/A')
                display_title = f"{title[:40]}..." if len(title) > 40 else title
                st.write(f"{status_icon} {display_title}")
        
        if completed_count > 0:
            st.write(f"**✅ {completed_count} Completed:**")
            for action in current_actions.get("completed_actions", [])[-2:]:
                title = action.get('title', 'N/A')
                display_title = f"{title[:40]}..." if len(title) > 40 else title
                st.write(f"({display_title})")
    
    with col2:
        st.subheader("Path Status")
        target_role = context.get("active_path", {}).get("target_role", "N/A")
        st.write(f"**Target Role:** {target_role}")
        
        # Calculate actual path status from roadmap progress and actions
        roadmap = context.get("roadmap", {})
        total_steps = roadmap.get("total_steps", 0)
        completed_steps = len(roadmap.get("completed_steps", []))
        
        # Count actions in progress or completed
        actions_in_progress = 0
        actions_completed = 0
        for step in roadmap.get("steps", []):
            for action in step.get("actions", []):
                if action.get("status") == "completed" or action.get("agent_satisfied"):
                    actions_completed += 1
                elif action.get("status") == "in_progress":
                    actions_in_progress += 1
        
        # Also check current_actions
        current_actions = context.get("current_actions", {})
        actions_completed += len(current_actions.get("completed_actions", []))
        # Count completed actions in pending_actions too (they stay there until moved)
        actions_completed += len([a for a in current_actions.get("pending_actions", []) if a.get("status") == "completed" or a.get("agent_satisfied")])
        actions_in_progress += len([a for a in current_actions.get("pending_actions", []) if a.get("status") == "in_progress"])
        
        # Determine status
        if total_steps == 0:
            actual_status = "not_started"
        elif completed_steps >= total_steps and actions_completed > 0:
            actual_status = "completed"
        elif actions_completed > 0 or actions_in_progress > 0 or completed_steps > 0:
            actual_status = "in_progress"
        else:
            actual_status = "not_started"
        
        status_badge = {"not_started": "⭕", "in_progress": "🔵", "completed": "✅", "failed": "❌"}
        st.write(f"**Status:** {status_badge.get(actual_status, '')} {actual_status}")
        st.write(f"**Progress:** {completed_steps}/{total_steps} steps")
        if actions_completed > 0:
            st.write(f"**Actions:** {actions_completed} completed, {actions_in_progress} in progress")


def display_roadmap(context):
    """Display career roadmap tab"""
    path = context.get("active_path", {})
    
    if not path.get("primary_path"):
        st.warning("No career path generated yet.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Target Role", path.get("target_role", "N/A"))
    
    with col2:
        st.metric("Total Duration", f"{path['primary_path'].get('total_weeks', 0)} weeks")
    
    with col3:
        st.metric("Success Probability", f"{path.get('success_probability', 0)*100:.0f}%")
    
    st.markdown("---")
    
    if path.get("path_rationale"):
        st.subheader("Path Rationale")
        st.write(path["path_rationale"])
        st.markdown("---")
    
    st.subheader("Learning Steps")
    
    for step in path["primary_path"].get("steps", []):
        with st.expander(f"Step {step.get('step_number', 0)}: {step.get('title', 'N/A')} ({step.get('duration_weeks', 0)} weeks)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Description:** {step.get('description', 'N/A')}")
                st.write(f"**Difficulty:** {step.get('difficulty', 'N/A')}")
            
            with col2:
                st.write("**Skills to Learn:**")
                for skill in step.get("skills_to_learn", []):
                    st.write(f"• {skill}")


def display_actions_interactive(context):
    """Display action plan with interactive tracking and validation"""
    st.markdown("### Manage Your Actions")
    
    # Show validation result if it exists from previous submission
    if hasattr(st.session_state, 'validation_result') and st.session_state.validation_result:
        result = st.session_state.validation_result
        if result.get("passed"):
            st.success(f"✅ Action '{result['action_title']}' completed with score {result['score']}/9!")
            if st.button("Clear result", key="clear_validation"):
                st.session_state.validation_result = None
                st.rerun()
        st.markdown("---")
    
    actions = context["current_actions"]
    progress = context.get("progress", {})
    active_stage = progress.get("active_stage", 1)
    stage_completion = progress.get("stage_completion_rate", 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pending", len(actions.get("pending_actions", [])))
    
    with col2:
        st.metric("Completed", len(actions.get("completed_actions", [])))
    
    with col3:
        st.metric("Stage", f"#{active_stage}")
    
    with col4:
        st.metric("Stage Progress", f"{stage_completion*100:.0f}%")
    
    st.markdown("---")
    
    # Show stage progression
    st.write(f"**📍 Current Stage:** Stage {active_stage}")
    st.progress(min(stage_completion, 1.0))
    
    if stage_completion >= 1.0:
        st.success(f"🎉 Stage {active_stage} Complete! Next stage is being generated...")
    
    st.markdown("---")
    
    # Show next allocated task
    next_action_info = st.session_state.orch.get_next_action(st.session_state.user_id)
    if next_action_info["status"] == "success":
        st.info(f"📌 **Next Task:** {next_action_info['action'].get('title', 'N/A')}")
    
    st.markdown("---")
    
    # Mark action as complete
    st.subheader("Complete Next Action")
    
    pending = actions.get("pending_actions", [])
    
    if pending:
        action_titles = [f"{a.get('title', 'N/A')} ({a.get('priority', 'normal').upper()})" for a in pending[:5]]
        
        selected_action = st.selectbox("Select action to complete:", action_titles)
        
        if selected_action:
            col1, col2 = st.columns(2)
            
            with col1:
                hours_spent = st.number_input("Hours spent:", min_value=0.0, max_value=100.0, step=0.5, value=1.0)
            
            with col2:
                notes = st.text_input("Notes (optional):", placeholder="What did you accomplish?")
            
            if st.button("Mark Complete", type="primary", width="stretch"):
                action_title = selected_action.split(" (", 1)[0].strip()
                with st.spinner("Completing action and updating state..."):
                    force_result = st.session_state.orch.mark_action_as_completed(
                        st.session_state.user_id,
                        action_title,
                        score=9,
                        time_spent_hours=hours_spent
                    )
                    if force_result.get("status") == "success":
                        st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                        st.session_state.validation_result = {
                            "passed": True,
                            "score": 9,
                            "action_title": action_title
                        }
                        st.success(f"✅ Action '{action_title}' completed with score 9/9!")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Could not mark action complete: {force_result.get('message', 'Unknown error')}")
    else:
        st.success("All actions completed! Great progress!")


def display_progress(context):
    """Display progress tracking tab"""
    progress = context["progress"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Hours", f"{progress.get('time_spent_hours', 0):.1f}h")
    
    with col2:
        st.metric("Completion Rate", f"{progress.get('completion_rate', 0)*100:.1f}%")
    
    with col3:
        st.metric("Steps Completed", len(progress.get("completed_steps", [])))
    
    with col4:
        st.metric("Blockers", len(progress.get("blockers", [])))
    
    st.markdown("---")
    
    st.subheader("Overall Progress")
    completion_rate = progress.get("completion_rate", 0)
    st.progress(min(completion_rate, 1.0))
    st.write(f"**{completion_rate*100:.1f}% Complete**")
    
    st.markdown("---")
    
    # Display completed steps from progress object
    completed_steps = progress.get("completed_steps", [])
    if completed_steps:
        st.subheader("Completed Steps")
        for i, step in enumerate(completed_steps, 1):
            st.write(f"✓ {i}. {step}")
    else:
        st.info("No steps completed yet. Start completing actions to see progress here.")
    
    st.markdown("---")
    
    if progress.get("blockers"):
        st.subheader("Blockers Encountered")
        for blocker in progress["blockers"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{blocker.get('step', 'N/A')}**")
                st.write(f"{blocker.get('reason', 'N/A')}")
            with col2:
                st.write(f"📅 {blocker.get('timestamp', 'N/A')[:10]}")


def display_feedback_section(context):
    """Display feedback and insights tab"""
    st.markdown("### Generate Feedback & Insights")
    
    if st.button("Generate AI Feedback on Progress", type="primary", width="stretch"):
        with st.spinner("Analyzing progress and generating feedback..."):
            result = st.session_state.orch.evaluate_and_feedback(st.session_state.user_id)
            
            if result["status"] == "success":
                feedback = result["feedback_analysis"]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    rating = feedback.get("overall_progress_rating", "N/A").upper()
                    color = "green" if "EXCELLENT" in rating else "orange"
                    st.markdown(f"<span style='color:{color};font-size:1rem'>**{rating}**</span>", unsafe_allow_html=True)
                    st.write("Progress Rating")
                
                with col2:
                    velocity = feedback.get("velocity_assessment", "N/A")
                    st.write(f"**{velocity}**")
                    st.write("Velocity")
                
                with col3:
                    change = feedback.get("confidence_adjustment", 0)
                    symbol = "📈" if change >= 0 else "📉"
                    st.write(f"{symbol} {change:+.2f}")
                    st.write("Confidence")
                
                with col4:
                    motivation = feedback.get("motivation_level", "N/A").upper()
                    color = "green" if "HIGH" in motivation else "orange"
                    st.markdown(f"<span style='color:{color}'>{motivation}</span>", unsafe_allow_html=True)
                    st.write("Motivation")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Strengths")
                    for s in feedback.get("strengths_observed", [])[:3]:
                        st.write(f"<i class='fas fa-check'></i> ({s})")
                    
                    st.subheader("Concerns")
                    for c in feedback.get("areas_of_concern", [])[:3]:
                        st.write(f"⚠️ {c}")
                
                with col2:
                    st.subheader("Recommendations")
                    for adj in feedback.get("recommended_adjustments", [])[:3]:
                        st.write(f"• {adj.get('specific_change', 'N/A')}")
                
                st.markdown("---")
                st.success(feedback.get("encouragement_message", "Keep going!"))
            else:
                st.warning("Not enough data for feedback yet. Complete some actions first!")


def display_rerouting_section(context):
    """Display rerouting and path alternatives tab"""
    readiness = context["readiness"]
    
    confidence = readiness.get("confidence_score", 0.5)
    risk = readiness.get("deviation_risk", "medium")
    original_role = context["active_path"].get("original_target_role")
    current_role = context["active_path"].get("target_role")
    
    st.markdown("### Path Health Check")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Confidence Score", f"{confidence:.2f}/1.0")
    
    with col2:
        color = "green" if risk == "low" else "orange" if risk == "medium" else "red"
        st.markdown(f"**Deviation Risk:** <span style='color:{color}'>{risk.upper()}</span>", unsafe_allow_html=True)
    
    # Check if on alternative path
    if original_role and original_role != current_role:
        st.info(f"<i class='fas fa-info-circle'></i> You are currently on alternative path: **{current_role}**\nOriginal target was: **{original_role}**", unsafe_allow_html=True)
        
        completion = context["progress"].get("completion_rate", 0)
        st.write(f"Progress on alternative path: {completion*100:.0f}%")
        
        if completion >= 0.6:
            if st.button("<i class='fas fa-check'></i> Revert to Original Path", type="primary", width="stretch", unsafe_allow_html=True):
                with st.spinner("Reverting to original path..."):
                    result = st.session_state.orch.revert_to_original_path(
                        st.session_state.user_id
                    )
                    
                    if result["status"] == "success":
                        st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                        st.success(f"Successfully reverted to original path: {original_role}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning(result.get("message", "Could not revert path"))
        else:
            st.warning(f"Complete at least 60% of alternative path before reverting (currently {completion*100:.0f}%)")
        
        st.markdown("---")
    
    if confidence < 0.4 or risk == "high":
        st.warning("We detected deviation in your current path. Consider analyzing rerouting options.")
        
        if st.button("Analyze Rerouting Options", type="primary", width="stretch"):
            with st.spinner("Analyzing alternative paths..."):
                reroute_result = st.session_state.orch.handle_failure_and_reroute(
                    st.session_state.user_id
                )
                
                if reroute_result["status"] == "success":
                    st.session_state.reroute_analysis = reroute_result["reroute_analysis"]
                    st.rerun()
        
        # Display analysis if available
        if "reroute_analysis" in st.session_state:
            analysis = st.session_state.reroute_analysis
            
            st.markdown("---")
            st.subheader("Rerouting Analysis")
            
            st.write(f"**Failure Type:** {analysis.get('failure_type', 'N/A')}")
            st.write("**Reasons:**")
            for r in analysis.get("failure_reasons", []):
                st.write(f"• {r}")
            
            st.markdown("---")
            st.subheader("Choose Your Path Forward")
            
            alternatives = analysis.get("alternative_paths", [])
            
            if alternatives:
                for idx, alt in enumerate(alternatives, 1):
                    with st.expander(f"Option {idx}: {alt.get('new_target_role', 'N/A')} ({alt.get('success_probability', 0)*100:.0f}% success)"):
                        st.write(f"**Why Better:** {alt.get('why_better_fit', 'N/A')}")
                        st.write(f"**Duration:** {alt.get('estimated_duration_months', 'N/A')} months")
                        
                        if st.button(f"Select Option {idx}", key=f"select_{idx}", width="stretch"):
                            with st.spinner("Applying new path..."):
                                result = st.session_state.orch.apply_alternative_path(
                                    st.session_state.user_id,
                                    alt,
                                    path_type="alternative"
                                )
                                
                                if result["status"] == "success":
                                    st.session_state.refresh_context = True
                                    st.success("Path updated! Context refreshed.")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Failed to apply path")
    else:
        st.success("Your current path is on track. No rerouting needed!")


def display_chatbot_section(context):
    """Display chatbot interface as a fixed sticky section"""
    import requests
    from typing import List, Dict
    
    # Groq API configuration
    GROQ_API_KEY = "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"
    
    SYSTEM_PROMPT = """You are a career guidance assistant specializing in helping students and professionals navigate their career paths. 
You provide personalized advice on:
- Career path selection
- Skill development and learning paths
- Job market trends and opportunities
- Industry insights
- Interview preparation
- Resume optimization
- Career transitions and pivots

Be conversational, encouraging, and practical in your advice. Ask clarifying questions when needed to provide better guidance."""
    
    def call_groq_api(messages: List[Dict[str, str]]) -> str:
        """Call Groq API and return response"""
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    # Initialize chat history with unique key
    if "career_chat_history" not in st.session_state:
        st.session_state.career_chat_history = []
    
    # Add CSS for aligned columns
    st.markdown("""
    <style>
        /* Force equal height for chat action columns */
        [data-testid="column"] .stMetric {
            min-height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 !important;
        }
        
        [data-testid="column"] .stButton {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100px;
            margin: 0 !important;
        }
        
        [data-testid="column"] .stDownloadButton {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100px;
            margin: 0 !important;
        }
        
        [data-testid="column"] button {
            height: 100% !important;
            min-height: 100px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💬 Career Chat Assistant")
    st.markdown("Get personalized guidance on your career journey")
    
    # Create a container for the chat
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages in a scrollable area
        messages_placeholder = st.container()
        
        with messages_placeholder:
            if len(st.session_state.career_chat_history) == 0:
                st.info("👋 **Welcome!** Ask me anything about career paths, skills development, market trends, or career-related questions.")
            else:
                for message in st.session_state.career_chat_history:
                    if message["role"] == "user":
                        with st.chat_message("user", avatar="👤"):
                            st.markdown(message["content"])
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(message["content"])
    
    # Input area at the bottom
    st.markdown("---")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Your message",
            placeholder="Type your career question here...",
            key="career_assistant_input_field",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button(
            "Send", 
            use_container_width=True, 
            key="career_assistant_send_button",
            type="primary"
        )
    
    # Handle message sending
    if send_button and user_input.strip():
        # Add user message
        st.session_state.career_chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get AI response
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *st.session_state.career_chat_history
        ]
        
        try:
            with st.spinner("🤔 Thinking..."):
                bot_response = call_groq_api(messages)
            
            # Add bot message
            st.session_state.career_chat_history.append({
                "role": "assistant",
                "content": bot_response
            })
            
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Action buttons - aligned with equal height
    col1, col3 = st.columns([1, 1])
    
    with col1:
        if st.button("Clear Chat", use_container_width=True, key="career_assistant_clear_button"):
            st.session_state.career_chat_history = []
            st.rerun()
    
    
    with col3:
        if st.session_state.career_chat_history:
            chat_text = "\n\n".join([
                f"{'You' if m['role'] == 'user' else 'Assistant'}: {m['content']}" 
                for m in st.session_state.career_chat_history
            ])
            st.download_button(
                "Save",
                chat_text,
                file_name=f"career_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="career_assistant_download_button",
                use_container_width=True
            )
def display_roadmap_section(context):
    """Display roadmap with step and action tracking"""
    roadmap = context.get("roadmap", {})
    
    if not roadmap or not roadmap.get("steps"):
        st.info("No roadmap generated yet. Complete onboarding first!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Roadmap Now", width="stretch", type="primary"):
                result = st.session_state.orch.generate_roadmap(st.session_state.user_id)
                if result["status"] == "success":
                    st.success("Roadmap generated!")
                    st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                    st.rerun()
                else:
                    st.error(f"Error: {result['message']}")
        return
    
    st.markdown("## <i class='fas fa-map'></i> Your Career Roadmap", unsafe_allow_html=True)
    
    # Overall progress
    total_steps = roadmap.get("total_steps", 0)
    completed_steps = len(roadmap.get("completed_steps", []))
    progress_pct = (completed_steps / total_steps * 100) if total_steps > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Steps", total_steps)
    with col2:
        st.metric("Completed", completed_steps)
    with col3:
        st.metric("Progress", f"{progress_pct:.0f}%")
    with col4:
        st.metric("Status", roadmap.get("status", "unknown").upper())
    
    st.progress(progress_pct / 100)
    
    st.markdown("---")
    
    # Get all current actions for linking to steps
    current_actions = context.get("current_actions", {})
    pending_actions = current_actions.get("pending_actions", [])
    completed_actions = current_actions.get("completed_actions", [])
    all_actions = pending_actions + completed_actions
    
    # Display each step
    for step in roadmap.get("steps", []):
        step_num = step.get("step_number")
        step_title = step.get("title")
        step_status = step.get("status", "pending")  # Default status if not set
        
        # Step header with status badge
        status_color = "✅" if step_status == "completed" else "⏳" if step_status == "in_progress" else "⭕"
        
        with st.expander(f"{status_color} Step {step_num}: {step_title}", expanded=(step_status == "in_progress")):
            # Display step details
            st.write(f"**Description:** {step.get('description', 'N/A')}")
            
            # Show step info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Duration:** {step.get('duration_weeks', 'N/A')} weeks")
            with col2:
                st.write(f"**Difficulty:** {step.get('difficulty', 'N/A')}")
            with col3:
                st.write(f"**Status:** {step_status.upper()}")
            
            # Show skills to learn
            if step.get("skills_to_learn"):
                st.write("**Skills to Learn:**")
                for skill in step.get("skills_to_learn", []):
                    st.write(f"• {skill}")
            
            # Show resources
            if step.get("resources"):
                st.write("**Resources:**")
                for resource in step.get("resources", []):
                    st.write(f"• {resource}")
            
            # Show success criteria
            if step.get("success_criteria"):
                st.write(f"**Success Criteria:** {step.get('success_criteria')}")
            
            st.markdown("---")
            
            # Actions in this step - get from roadmap AND link from current_actions
            roadmap_actions = step.get("actions", [])
            
            # Link actions from current_actions that belong to this step
            linked_actions = []
            for action in all_actions:
                # Match actions by title or other identifiers
                action_title = action.get("title", "")
                
                # Check if this action belongs to this step (simple heuristic: if not already in roadmap_actions)
                if action_title and not any(a.get("title") == action_title for a in roadmap_actions):
                    # This is a current action that should be displayed
                    linked_actions.append(action)
            
            # Combine roadmap actions with linked current actions
            all_step_actions = roadmap_actions + linked_actions
            
            if all_step_actions:
                completed_count = sum(1 for a in all_step_actions if a.get("agent_satisfied") or a.get("status") == "completed")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Actions: {completed_count}/{len(all_step_actions)} Complete**")
                with col2:
                    action_progress = (completed_count / len(all_step_actions) * 100) if all_step_actions else 0
                    st.progress(action_progress / 100)
                
                # Display each action
                for action_idx, action in enumerate(all_step_actions):
                    action_id = action.get("action_id")
                    action_title = action.get("title")
                    action_status = action.get("status", "pending")
                    relevance_score = action.get("relevance_score", 0)
                    
                    if action_status == "completed" or action.get("agent_satisfied"):
                        status_icon = "✅"
                    elif action_status == "in_progress":
                        status_icon = "⏳"
                    else:
                        status_icon = "⭕"
                    
                    action_col1, action_col2, action_col3 = st.columns([2, 1, 1])
                    
                    with action_col1:
                        st.markdown(f"**{status_icon} {action_title}**")
                        st.caption(action.get("description", ""))
                    
                    with action_col2:
                        if relevance_score > 0:
                            st.metric("Score", f"{relevance_score:.2f}")
                    
                    with action_col3:
                        if action_status != "completed" and not action.get("agent_satisfied"):
                            # Use unique key: step_step_number_action_index_action_id
                            unique_key = f"action_step{step_num}_idx{action_idx}_{action_id or action_title.replace(' ', '_')[:20]}"
                            if st.button("Start/Complete", key=unique_key, width="stretch"):
                                st.session_state.current_action = {
                                    "action_id": action_id,
                                    "step_number": step_num,
                                    "action_data": action
                                }
                                st.session_state.page = "action_completion"
                                st.rerun()
                        else:
                            st.markdown("✅ Complete")
            else:
                st.info("ℹ️ No actions added yet for this step. Actions will be generated as you progress.")


def display_action_completion_page(context):
    """Page for completing an action with questions"""
    if not hasattr(st.session_state, 'current_action'):
        st.warning("No action selected")
        if st.button("← Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
        return
    
    action_info = st.session_state.current_action
    action_id = action_info.get("action_id")  # May be None
    step_num = action_info["step_number"]
    action_data = action_info["action_data"]
    action_title = action_data.get("title")
    
    # Fallback to title if action_id is missing
    lookup_id = action_id or action_title
    
    st.markdown(f"## Complete Action: {action_title}")
    st.write(action_data.get("description", ""))
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Success Criteria:** {action_data.get('success_criteria', 'N/A')}")
    with col2:
        st.info(f"**Attempt #{action_data.get('attempts', 0) + 1}**")
    
    st.markdown("---")
    
    # Check if questions already generated
    questions = action_data.get("questions", [])
    
    if not questions:
        st.markdown("### Generating validation questions...")
        
        result = st.session_state.orch.complete_action_in_roadmap(
            st.session_state.user_id,
            step_num,
            lookup_id
        )
        
        if result["status"] == "success":
            questions = result.get("questions", [])
            st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
            
            # Update current_action with newly generated questions
            st.session_state.current_action["action_data"]["questions"] = questions
            
            st.rerun()
        else:
            st.error(f"Error generating questions: {result['message']}")
            if st.button("← Back"):
                st.session_state.page = "dashboard"
                st.rerun()
            return
    
    st.markdown("### Answer These Questions")
    st.write("Your answers will be evaluated to determine if you've mastered this action.")
    
    submitted = False
    answers = []
    
    with st.form("action_answers_form"):
        for i, q in enumerate(questions):
            # Handle both string questions and dictionary questions
            if isinstance(q, dict):
                question_text = q.get('question', '')
            else:
                question_text = str(q)
            
            st.markdown(f"**Question {i+1}:** {question_text}")
            answer = st.text_area(f"Your answer {i+1}:", height=100, key=f"answer_{i}")
            answers.append(answer)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Submit Answers", width="stretch", type="primary")
        with col2:
            if st.form_submit_button("← Back to Roadmap", width="stretch"):
                st.session_state.page = "dashboard"
                st.rerun()
    
    # Results shown AFTER form submission (outside the form)
    if "submitted" in st.session_state and st.session_state.submitted:
        if "result" in st.session_state:
            result = st.session_state.result
            
            if result.get("agent_satisfied"):
                st.success(f"✅ Action Complete! Score: {result.get('relevance_score', 0):.2f}")
                st.write(f"**Feedback:** {result.get('feedback', '')}")
                
                if st.button("Continue to Next Action", width="stretch", type="primary"):
                    st.session_state.page = "dashboard"
                    st.rerun()
            else:
                st.warning(f"⏸️ Action Needs More Work (Score: {result.get('relevance_score', 0):.2f})")
                st.write(f"**Feedback:** {result.get('feedback', '')}")
                st.write(f"**Next Steps:** {result.get('next_steps', '')}")
                
                if st.button("Try Again", width="stretch"):
                    st.session_state.page = "dashboard"
                    st.rerun()
    elif submitted:
        # Process form submission when submitted
        if any(not a.strip() for a in answers):
            st.error("Please answer all questions")
        else:
            result = st.session_state.orch.submit_action_answers(
                st.session_state.user_id,
                step_num,
                lookup_id,
                answers
            )
            
            st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
            st.session_state.result = result
            st.session_state.submitted = True
            st.rerun()


def display_market_dashboard(context):
    """Display comprehensive market context dashboard"""
    market_context = context.get("market_context", {})
    target_role_analysis = market_context.get("target_role_analysis", {})
    
    st.markdown("<h2><i class='fas fa-chart-line'></i> Market Intelligence Dashboard</h2>", unsafe_allow_html=True)
    
    if not target_role_analysis:
        st.warning("No market data available yet. Complete onboarding first.")
        return
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        demand = target_role_analysis.get("demand_score", 0)
        st.metric("Market Demand", f"{demand}/100", delta="High" if demand > 70 else "Medium")
    
    with col2:
        competition = target_role_analysis.get("competition_level", "unknown").upper()
        st.metric("Competition", competition)
    
    with col3:
        barrier = target_role_analysis.get("entry_barrier", "unknown").upper()
        st.metric("Entry Barrier", barrier)
    
    with col4:
        trend = target_role_analysis.get("market_trend", "unknown").upper()
        st.metric("Market Trend", trend)
    
    st.markdown("---")
    
    # Target Role Deep Dive
    st.markdown(f"<h3><i class='fas fa-bullseye'></i> Your Target Role: {target_role_analysis.get('role_title', 'N/A')}</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Salary Range:** ${target_role_analysis.get('avg_salary_range_usd', 'N/A')}")
        st.write(f"**Required Experience:** {target_role_analysis.get('required_experience_years', 'N/A')}")
        st.write(f"**Job Availability:** {target_role_analysis.get('job_availability', 'N/A')}")
        st.write(f"**Market Saturation:** {target_role_analysis.get('market_saturation', 'N/A')}")
    
    with col2:
        st.write("**Top Hiring Companies:**")
        for company in target_role_analysis.get("key_hiring_companies", []):
            st.write(f"• {company}")
    
    st.markdown("---")
    
    # In-Demand Skills
    st.markdown("### 🔧 In-Demand Skills for This Role")
    in_demand = target_role_analysis.get("in_demand_skills", [])
    if in_demand:
        cols = st.columns(len(in_demand))
        for i, skill in enumerate(in_demand):
            with cols[i]:
                st.info(f"📌 {skill}")
    
    st.markdown("---")
    
    # Market Notes
    if target_role_analysis.get("market_notes"):
        st.markdown("### 📝 Market Insights")
        st.write(target_role_analysis["market_notes"])
    
    st.markdown("---")
    
    # Adjacent/Easier Roles
    safer_roles = target_role_analysis.get("adjacent_safer_roles", [])
    if safer_roles:
        st.markdown("<h3><i class='fas fa-lightbulb'></i> Alternative Paths (Easier Entry)</h3>", unsafe_allow_html=True)
        st.write("If your current goal feels too ambitious, consider these adjacent roles:")
        
        for idx, alt_role in enumerate(safer_roles, 1):
            with st.expander(f"Option {idx}: {alt_role.get('role', 'N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Demand Score:** {alt_role.get('demand_score', 0)}/100")
                    st.write(f"**Entry Barrier:** {alt_role.get('entry_barrier', 'N/A')}")
                with col2:
                    st.write(f"**Why:** {alt_role.get('reason', 'N/A')}")
                
                if st.button(f"Switch to {alt_role.get('role', 'N/A')}", key=f"switch_market_{idx}"):
                    # Create alternative path object
                    alt_path = {
                        "new_target_role": alt_role.get("role"),
                        "why_better_fit": alt_role.get("reason"),
                        "success_probability": alt_role.get("demand_score", 75) / 100.0,
                        "estimated_duration_months": 6
                    }
                    with st.spinner("Switching to this path..."):
                        result = st.session_state.orch.apply_alternative_path(
                            st.session_state.user_id,
                            alt_path,
                            path_type="alternative"
                        )
                        if result["status"] == "success":
                            st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                            st.success(f"✅ Switched to {alt_role.get('role')}! New roadmap generated.")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Error: {result.get('message')}")
    
    st.markdown("---")
    
    # Market Trends Timeline
    market_trends = market_context.get("market_trends", [])
    if market_trends:
        st.markdown("<h3><i class='fas fa-chart-area'></i> Market Trends Over Time</h3>", unsafe_allow_html=True)
        trend_data = []
        for trend in market_trends:
            trend_data.append({
                "Role": trend.get("role"),
                "Demand Score": trend.get("demand_score"),
                "Trend": trend.get("trend"),
                "Date": trend.get("timestamp")
            })
        if trend_data:
            st.dataframe(trend_data, width="stretch")
    
    # Last Updated
    last_check = market_context.get("last_market_check")
    if last_check:
        st.caption(f"Last market check: {last_check[:10]}")


def display_rerouting_ui(context):
    """Display rerouting section with alternatives"""
    reroute_state = context.get("reroute_state", {})
    
    st.markdown("<h2><i class='fas fa-exchange-alt'></i> Path Rerouting</h2>", unsafe_allow_html=True)
    
    if not reroute_state.get("is_rerouting"):
        col1, col2 = st.columns(2)
        with col1:
            st.info("No active rerouting. Trigger if you face challenges:")
        with col2:
            if st.button("Detect Deviation & Suggest Alternatives", width="stretch"):
                deviation_reason = st.text_input("What deviation are you experiencing?")
                if deviation_reason and st.button("Generate Alternatives"):
                    result = st.session_state.orch.detect_deviation_and_reroute(
                        st.session_state.user_id,
                        deviation_reason
                    )
                    if result["status"] == "success":
                        st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                        st.rerun()
                    else:
                        st.error(f"Error: {result['message']}")
        return
    
    st.warning("⚠️ You're currently in rerouting mode")
    st.write(f"**Reason:** {reroute_state.get('reroute_reason', 'N/A')}")
    
    alternatives = reroute_state.get("alternative_roadmaps", [])
    adjusted_original = reroute_state.get("adjusted_original", {})
    
    # Display alternatives
    st.markdown("### Available Options:")
    
    for alt in alternatives:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{alt.get('new_target_role')}**")
            st.caption(f"Success Probability: {alt.get('success_probability', 0)*100:.0f}%")
            st.write(alt.get("reason", ""))
        with col2:
            if st.button("Select", key=f"select_{alt.get('option_id')}", width="stretch"):
                result = st.session_state.orch.select_reroute_option(
                    st.session_state.user_id,
                    alt.get("option_id")
                )
                if result["status"] == "success":
                    st.success("Alternative path selected! New roadmap generated.")
                    st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                    st.rerun()
    
    # Display adjusted original
    if adjusted_original:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Keep Original: {adjusted_original.get('original_target_role')}** (Adjusted)")
            st.caption(f"Extended Timeline: {adjusted_original.get('timeline_months')} months")
            st.write(adjusted_original.get("adjustment", ""))
        with col2:
            if st.button("Select", key="select_original_adjusted", width="stretch"):
                result = st.session_state.orch.select_reroute_option(
                    st.session_state.user_id,
                    "original_adjusted"
                )
                if result["status"] == "success":
                    st.success("Adjusted original path selected! New roadmap generated.")
                    st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
                    st.rerun()
def display_settings(context):
    """Display settings tab"""
    st.markdown("###  Account Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**User ID:** {st.session_state.user_id}")
        target_role = context.get("active_path", {}).get("target_role", "Not set")
        st.write(f"**Target Role:** {target_role}")
    
    with col2:
        created_at = context.get("created_at", "Unknown")
        st.write(f"**Created:** {created_at}")
        
        last_updated = context.get("last_updated", "Unknown")
        st.write(f"**Last Updated:** {last_updated}")
    
    st.markdown("---")
    st.markdown("###  Export & Download")
    
    if st.button("Export Complete Context as JSON", use_container_width=True):
        json_str = json.dumps(context, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"{st.session_state.user_id}_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown("---")
    st.markdown("###  Navigation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    
    with col2:
        if st.button(" Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.context = None
            st.session_state.page = "home"
            st.rerun()

def page_dashboard():
    """Main dashboard with 8 tabs"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"<h4><i class='fas fa-circle-user'></i> User: **{st.session_state.user_id}**</h4>", unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.context = st.session_state.orch.get_student_context(st.session_state.user_id)
            st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        " Overview",
        " Roadmap",
        " Actions",
        " Progress",
        " Feedback",
        " Market",
        " Chat",
        " Settings"
    ])
    
    with tab1:
        display_overview(st.session_state.context)
    
    with tab2:
        display_roadmap_section(st.session_state.context)
    
    with tab3:
        display_actions_interactive(st.session_state.context)
    
    with tab4:
        display_progress(st.session_state.context)
    
    with tab5:
        display_feedback_section(st.session_state.context)
    
    with tab6:
        display_market_dashboard(st.session_state.context)
    
    with tab7:
        display_chatbot_section(st.session_state.context)
    
    with tab8:
        display_settings(st.session_state.context)
    

def main():
    """Main app router"""
    initialize_session()
    
    # Professional Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title"><i class="fas fa-compass"></i>Career Navigator</h1>
        <p class="header-subtitle">Personalized Career Guidance from Start to Success</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Page routing
    if st.session_state.page == "home":
        page_home()
    elif st.session_state.page == "onboarding":
        page_onboarding()
    elif st.session_state.page == "onboarding_questions":
        page_onboarding_questions()
    elif st.session_state.page == "dashboard":
        page_dashboard()
    elif st.session_state.page == "action_completion":
        display_action_completion_page(st.session_state.context)
    elif st.session_state.page == "settings":
        display_settings(st.session_state.context)


if __name__ == "__main__":
    main()
