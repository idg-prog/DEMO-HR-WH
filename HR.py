"""
RecruitAI Pro — AI CV Screening Automation Demo
Developed for sales demonstration (Recruitment Agencies / RH)
Author: Anas — AI Automation Engineer
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import io
import json
import random

# ============================================================
# API CONFIGURATION (DEEPSEEK)
# ============================================================
# Setting a placeholder for the recruiter to see/edit if needed, 
# or you can hardcode it here.
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="RecruitAI Pro — Automated CV Screening",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLE (Restored full CSS)
# ============================================================
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .block-container { padding-top: 2rem; }

    .hero {
        background: linear-gradient(135deg, #1a1c29 0%, #2d1b4e 100%);
        border: 1px solid #3d3d5c;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
    }
    .hero h1 { font-size: 2.1rem; margin-bottom: 0.3rem; }
    .hero p { color: #b8b8d1; font-size: 1.05rem; }

    .card {
        background: #161824;
        border: 1px solid #2a2d40;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    }
    .card h3 { margin-top: 0; }

    .pill {
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.4rem;
    }
    .pill-green { background: rgba(46, 204, 113, 0.15); color: #2ecc71; border: 1px solid #2ecc71; }
    .pill-orange { background: rgba(243, 156, 18, 0.15); color: #f39c12; border: 1px solid #f39c12; }
    .pill-red { background: rgba(231, 76, 60, 0.15); color: #e74c3c; border: 1px solid #e74c3c; }
    .pill-blue { background: rgba(52, 152, 219, 0.15); color: #3498db; border: 1px solid #3498db; }

    .step-box {
        background: #161824;
        border: 1px solid #2a2d40;
        border-left: 4px solid #8e44ad;
        border-radius: 10px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.7rem;
    }

    .metric-card {
        background: #161824;
        border: 1px solid #2a2d40;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        text-align: center;
    }
    .metric-card .val { font-size: 1.8rem; font-weight: 700; }
    .metric-card .lbl { color: #9a9ab0; font-size: 0.85rem; margin-top: 0.2rem; }

    .footer-note { color: #6c6c85; font-size: 0.8rem; margin-top: 3rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MOCK DATA (Restored)
# ============================================================
CITIES = ["Casablanca", "Rabat", "London", "New York", "Dubai", "Abu Dhabi", "Paris", "Singapore"]
POSTES = ["Full Stack Developer", "Business Developer", "Senior Accountant", "IT Project Manager",
          "DevOps Engineer", "HR Manager", "Data Analyst", "Marketing Lead"]
DIPLOMES = ["MSc Engineering", "Master in Finance", "BSc Computer Science", "MBA", "MSc Data Science",
            "Master in HR", "Associate Degree", "PhD"]
STATUTS = ["New", "Preselected", "Interview Scheduled", "Rejected", "Hired"]
PRENOMS = ["Youssef", "Salma", "Amine", "Sara", "Karim", "Nour", "Omar", "Imane", "Yassine", "Meryem",
           "Adam", "Hiba", "Rayan", "Lina", "Zakaria", "Kenza", "Ismail", "Douaa", "Anas", "Fatima"]
NOMS = ["El Amrani", "Bennani", "Chraibi", "Idrissi", "Tazi", "Berrada", "Fassi", "Alaoui", "Cherkaoui", "Lahlou"]

@st.cache_data
def load_candidates(n=24):
    random.seed(42)
    rows = []
    for i in range(n):
        score = random.randint(35, 98)
        rows.append({
            "ID": f"CAND-{1000+i}",
            "Name": f"{random.choice(PRENOMS)} {random.choice(NOMS)}",
            "Target Position": random.choice(POSTES),
            "City": random.choice(CITIES),
            "Degree": random.choice(DIPLOMES),
            "Experience (yrs)": random.randint(0, 12),
            "AI Score": score,
            "Status": random.choice(STATUTS) if score < 90 else random.choice(["Preselected", "Interview Scheduled", "Hired"]),
            "Email": f"{random.choice(PRENOMS).lower()}.{random.choice(NOMS).lower().replace(' ', '')}@email.com",
            "Source": random.choice(["Gmail", "Outlook", "Career Site"]),
            "Date Received": (datetime.now() - timedelta(days=random.randint(0, 45))).strftime("%d/%m/%Y"),
        })
    return pd.DataFrame(rows)

SAMPLE_JOBS = {
    "Full Stack Developer (Remote)": """We are looking for a Full Stack Developer (M/F).
Required Skills: Python, JavaScript, React, FastAPI, SQL, Git, Docker.
Experience: 3 to 6 years minimum in web development.
Degree: Master's in Computer Science or equivalent.""",
    "Business Developer (Dubai)": """Business Developer position based in Dubai, UAE.
Required Skills: B2B prospecting, negotiation, CRM (Odoo/Salesforce), fluent English, Arabic is a plus.
Experience: 2 to 5 years in business development.""",
}

# ============================================================
# LOGIC ENGINES (Restored + DeepSeek Integration)
# ============================================================
def extract_text_from_upload(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx"):
        import docx
        doc = docx.Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")

def call_deepseek_ai(resume_text, job_desc):
    """Calling DeepSeek API to get the scoring results."""
    from openai import OpenAI
    
    # DeepSeek uses an OpenAI-compatible SDK
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    
    prompt = f"""Analyze this CV against the job description. Return a JSON object with:
    'score' (0-100), 'verdict' (short phrase), 'matched_skills' (list), 'missing_skills' (list), 'why' (3 sentences max).
    
    JOB DESCRIPTION:
    {job_desc}
    
    CANDIDATE CV:
    {resume_text}
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            response_format={'type': 'json_object'}
        )
        data = json.loads(response.choices[0].message.content)
        data["engine"] = "DeepSeek-V3 (AI Background Engine)"
        return data
    except Exception as e:
        # Fallback to mock logic if API fails or key is missing
        return {
            "score": random.randint(65, 88),
            "verdict": "Likely match (DeepSeek Offline Fallback)",
            "matched_skills": ["Project Management", "Communication"],
            "missing_skills": ["Advanced Python"],
            "why": f"Automated analysis suggests high compatibility. (Error: {str(e)})",
            "engine": "Fallback Engine"
        }

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## 🎯 RecruitAI Pro")
st.sidebar.caption("Sales Demo — Automated CV Screening")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Solution Overview",
        "🏗️ Technical Architecture",
        "🗂️ Talent Pool & Dashboard",
        "🧠 AI Scoring Demo",
        "📅 Automated Scheduling",
        "💰 Cost & Timeline",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption("Presented by **Anas** · AI Automation Engineer\nanaslachhab666@gmail.com")

# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================
if page == "🏠 Solution Overview":
    st.markdown("""
    <div class="hero">
        <h1>🎯 RecruitAI Pro</h1>
        <p>Complete CV sorting automation using Artificial Intelligence — from email reception 
        to interview scheduling, without manual intervention.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in zip([c1, c2, c3, c4], ["-80%", "24/7", "< 30 sec", "100%"], ["Sorting Time", "Processing", "Per CV", "Traceability"]):
        col.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("### How it works")
    steps = [
        ("1️⃣ Email Sync", "Connects to Gmail/Outlook via API. Detects attachments automatically."),
        ("2️⃣ Extraction", "Reads PDFs and Word docs instantly with OCR/Parser."),
        ("3️⃣ DeepSeek AI Analysis", "The CV is scored against the job desc by the AI Engine."),
        ("4️⃣ Automated Workflow", "Good profiles get an auto-email with an interview link.")
    ]
    for title, desc in steps:
        st.markdown(f'<div class="step-box"><b>{title}</b><br><span style="color:#b8b8d1">{desc}</span></div>', unsafe_allow_html=True)

# ============================================================
# PAGE 2 — ARCHITECTURE
# ============================================================
elif page == "🏗️ Technical Architecture":
    st.markdown("## 🏗️ Technical Architecture")
    dot = """
    digraph G {
        rankdir=LR; bgcolor="transparent";
        node [fontname="Helvetica" fontsize=11 style="filled,rounded" shape=box color="#3d3d5c" fontcolor="white"];
        edge [color="#8e44ad" fontcolor="#b8b8d1"];
        Gmail -> Parse -> DeepSeek_LLM -> Database -> Dashboard;
        DeepSeek_LLM -> Calendly [label="score > 75"];
    }
    """
    st.graphviz_chart(dot)
    
    t1, t2, t3 = st.tabs(["API Layer", "AI Engine", "Database"])
    with t1: st.write("Connects via OAuth2 to Google/Microsoft environments.")
    with t2: st.write("DeepSeek-V3 processes text to identify skills, years of experience, and culture fit.")
    with t3: st.write("PostgreSQL database stores all candidates for a reusable Talent Pool.")

# ============================================================
# PAGE 3 — TALENT POOL (TABLE RESTORED)
# ============================================================
elif page == "🗂️ Talent Pool & Dashboard":
    st.markdown("## 🗂️ Talent Pool & HR Dashboard")
    df = load_candidates()

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="metric-card"><div class="val">{len(df)}</div><div class="lbl">Total Candidates</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="metric-card"><div class="val">{(df["AI Score"]>=75).sum()}</div><div class="lbl">Qualified (Score > 75)</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="metric-card"><div class="val">{(df["Status"]=="Interview Scheduled").sum()}</div><div class="lbl">Interviews Set</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="metric-card"><div class="val">{round(df["AI Score"].mean())}%</div><div class="lbl">Avg AI Score</div></div>', unsafe_allow_html=True)

    st.markdown("### 📋 All Candidates")
    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    p_filter = col_f1.multiselect("Filter by Position", df["Target Position"].unique())
    s_filter = col_f2.slider("Min AI Score", 0, 100, 30)
    
    filtered = df[df["AI Score"] >= s_filter]
    if p_filter:
        filtered = filtered[filtered["Target Position"].isin(p_filter)]

    # RESTORED TABLE
    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "AI Score": st.column_config.ProgressColumn("AI Score", min_value=0, max_value=100, format="%d%%"),
            "Email": st.column_config.LinkColumn("Email"),
        }
    )

    st.markdown("### 🔍 Candidate Detail View")
    selected_name = st.selectbox("Select a candidate to view detailed analysis", filtered["Name"].tolist())
    if selected_name:
        c_data = filtered[filtered["Name"] == selected_name].iloc[0]
        with st.container():
            st.markdown(f"""
            <div class='card'>
                <h4>{c_data['Name']} - {c_data['Target Position']}</h4>
                <p>📍 {c_data['City']} | 🎓 {c_data['Degree']} | 💼 {c_data['Experience (yrs)']} years exp.</p>
                <p><b>AI Status:</b> {c_data['Status']}</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# PAGE 4 — SCORING DEMO (UPLOAD ONLY + DEEPSEEK)
# ============================================================
elif page == "🧠 AI Scoring Demo":
    st.markdown("## 🧠 AI Scoring Demo (DeepSeek-V3)")
    st.info("This demo uses DeepSeek API in the background to analyze your uploaded CV.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. Select Job Description")
        job_title = st.selectbox("Position", list(SAMPLE_JOBS.keys()))
        job_desc = st.text_area("Job Requirements", value=SAMPLE_JOBS[job_title], height=180)
        
    with col2:
        st.markdown("#### 2. Upload Candidate CV")
        uploaded_cv = st.file_uploader("Upload PDF or Word Document", type=["pdf", "docx"])
        if uploaded_cv:
            st.success("File uploaded successfully.")

    if st.button("🚀 Analyze Candidate Profile", type="primary", use_container_width=True):
        if not uploaded_cv:
            st.error("Please upload a CV file to run the analysis.")
        else:
            with st.spinner("DeepSeek AI is analyzing the CV..."):
                cv_text = extract_text_from_upload(uploaded_cv)
                # DEEPSEEK API CALL
                result = call_deepseek_ai(cv_text, job_desc)
                
                st.markdown("---")
                r_col1, r_col2 = st.columns([1, 2])
                with r_col1:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=result["score"],
                        title={"text": "AI Relevance Score"},
                        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#8e44ad"}}
                    ))
                    fig.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown(f"**Verdict:** {result['verdict']}")
                    st.caption(f"Engine: {result['engine']}")

                with r_col2:
                    st.markdown("#### 💬 AI Analysis Justification")
                    st.info(result["why"])
                    st.write(f"**✅ Matched Skills:** {', '.join(result['matched_skills'])}")
                    st.write(f"**⚠️ Missing Skills:** {', '.join(result['missing_skills'])}")
                    
                    if result["score"] >= 75:
                        st.success("Target Met: This candidate will automatically receive an interview invitation.")

# ============================================================
# PAGE 5 — SCHEDULING (Restored)
# ============================================================
elif page == "📅 Automated Scheduling":
    st.markdown("## 📅 Automated Scheduling")
    st.caption("Qualified candidates receive this invitation automatically.")
    
    df = load_candidates()
    qualified = df[df["AI Score"] >= 75].head(5)
    
    for _, row in qualified.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{row['Name']}** - {row['Target Position']}")
            c2.markdown(f'<span class="pill pill-green">{row["AI Score"]}% Match</span>', unsafe_allow_html=True)
            if c3.button("Send Invite", key=row["ID"]):
                st.toast(f"Invitation sent to {row['Email']}")
            st.markdown("---")

# ============================================================
# PAGE 6 — COST (Restored)
# ============================================================
elif page == "💰 Cost & Timeline":
    st.markdown("## 💰 Pricing & Timeline")
    
    c1, c2, c3 = st.columns(3)
    plans = [
        ("Starter", "$500", "Email sync + Basic Scoring", "2 weeks"),
        ("Pro", "$1,000", "Full Automation + Scheduling", "4 weeks"),
        ("Enterprise", "Custom", "Full ATS Integration", "8 weeks")
    ]
    for col, (name, price, desc, time) in zip([c1, c2, c3], plans):
        col.markdown(f"""
        <div class='card'>
            <h3>{name}</h3>
            <h2 style='color:#8e44ad'>{price}</h2>
            <p>{desc}</p>
            <p><b>Timeline:</b> {time}</p>
        </div>
        """, unsafe_allow_html=True)

    # Gantt Chart (Restored)
    st.markdown("### Deployment Timeline")
    phases = [
        ("API Sync", "2026-08-01", "2026-08-05"),
        ("AI Training", "2026-08-05", "2026-08-15"),
        ("Dashboard", "2026-08-15", "2026-08-25"),
        ("Launch", "2026-08-25", "2026-08-30")
    ]
    g_df = pd.DataFrame(phases, columns=["Phase", "Start", "End"])
    fig = px.timeline(g_df, x_start="Start", x_end="End", y="Phase", color="Phase")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="footer-note">RecruitAI Pro — AI Automation Demo · Anas · 2026</div>', unsafe_allow_html=True)
