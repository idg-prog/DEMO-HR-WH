

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
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="RecruitAI Pro  Automated CV Screening",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLE
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
# MOCK DATA  TALENT POOL
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

threshold = 75


def call_deepseek_api(resume_text, job_desc):
    """Score a CV against a job description using the DeepSeek API."""
    api_key = st.secrets.get("DEEPSEEK_API_KEY")
    if not api_key:
        st.error("⚠️ No DeepSeek API key found in Streamlit secrets (DEEPSEEK_API_KEY).")
        return None

    prompt = f"""You are an expert recruitment assistant. Analyze this candidate's CV against the job description below.

Extract candidate information AND score the match. Reply STRICTLY in valid JSON with no surrounding text, backticks, or markdown, using exactly these keys:

{{
  "name": "candidate full name or 'Not found'",
  "country": "candidate country/location or 'Not found'",
  "email": "candidate email or 'Not found'",
  "phone": "candidate phone number or 'Not found'",
  "education_level": "highest degree/education level found",
  "experience_years": integer (estimated total years of relevant experience),
  "score": integer between 0 and 100 (overall match score),
  "verdict": "short verdict, e.g. Highly Recommended / Consider / Not a strong match",
  "matched_skills": ["list", "of", "matched skills"],
  "missing_skills": ["list", "of", "missing skills"],
  "why": "2-4 sentences explaining the score, referencing specific skills, experience and education alignment"
}}

JOB DESCRIPTION:
{job_desc}

CANDIDATE CV:
{resume_text}
"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=800,
        )
        raw = resp.choices[0].message.content
        cleaned = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        data = json.loads(cleaned)
        data["engine"] = "Live AI — DeepSeek"
        return data
    except Exception as e:
        st.error(f"⚠️ DeepSeek API call failed: {e}")
        return None


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

# ============================================================
# CV SAMPLES (for demo without upload)
# ============================================================
SAMPLE_JOBS = {
    "Full Stack Developer (Remote)": """We are looking for a Full Stack Developer (M/F).
Required Skills: Python, JavaScript, React, FastAPI, SQL, Git, Docker.
Experience: 3 to 6 years minimum in web development.
Degree: Master's in Computer Science or equivalent.
Professional English required. Autonomy, teamwork, and ability to work in an agile environment.""",
    "Business Developer (Dubai)": """Business Developer position based in Dubai, UAE.
Required Skills: B2B prospecting, negotiation, CRM (Odoo/Salesforce), fluent English, Arabic is a plus.
Experience: 2 to 5 years in business development, ideally in the tech or services sector.
Degree: Master's from a Business School or equivalent.
Driving license preferred, availability for regional travel.""",
}

SAMPLE_RESUMES = {
    "Candidate A  Strong Dev Profile": """Youssef El Amrani
Casablanca, Morocco | youssef.elamrani@email.com
Computer Engineer, MSc (ENSIAS)

Experience:
- 4 years in Full Stack development (Python, FastAPI, React, PostgreSQL)
- Implementation of CI/CD pipelines with Docker and Git
- Agile experience (Scrum), working in an international team

Skills: Python, JavaScript, React, SQL, Docker, Git, FastAPI, REST APIs
Languages: French (Native), English (Professional), Arabic (Native)
""",
    "Candidate B  Junior Profile": """Sara Bennani
Rabat, Morocco | sara.bennani@email.com
BSc in Computer Science

Experience:
- 1-year internship in web development (HTML, CSS, JavaScript)
- Academic e-commerce site project using PHP

Skills: HTML, CSS, JavaScript, PHP, MySQL basics
Languages: French (Native), English (Intermediate)
""",
    "Candidate C  Business Dev Profile": """Karim Tazi
Dubai, UAE | karim.tazi@email.com
MBA, Business School

Experience:
- 5 years in B2B business development in the tech sector, GCC market
- CRM management (Salesforce), closing contracts > 100K USD
- Fluent English, native Arabic, professional network in Dubai/Abu Dhabi

Skills: Negotiation, B2B prospecting, CRM, closing, key account management
Languages: Arabic (Native), English (Fluent), French (Professional)
""",
}

STOPWORDS = set("""the a an and or of to for with in on is are will be we you your our
poste recherche recherchons requises requis minimum idéalement""".split())

SKILL_BANK = ["python", "javascript", "react", "sql", "docker", "git", "fastapi", "java", "php",
              "html", "css", "excel", "power bi", "sap", "odoo", "salesforce", "crm", "negotiation",
              "prospecting", "marketing", "accounting", "finance", "hr", "communication", "english",
              "arabic", "french", "agile", "scrum", "devops", "data", "mysql", "postgresql", "aws"]

# ============================================================
# LOCAL SCORING ENGINE (Fallback - 100% Free)
# ============================================================
def extract_years_experience(text):
    matches = re.findall(r"(\d+)\s*(?:ans|an|years?)", text.lower())
    return max([int(m) for m in matches], default=0)

def extract_skills(text):
    text_low = text.lower()
    return sorted({s for s in SKILL_BANK if s in text_low})

def tokenize(text):
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2]

def score_resume_local(resume_text, job_desc):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_desc))
    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)

    skill_score = (len(matched) / len(job_skills) * 100) if job_skills else 50

    resume_years = extract_years_experience(resume_text)
    job_years_req = extract_years_experience(job_desc) or 2
    exp_score = min(100, (resume_years / job_years_req) * 100) if job_years_req else 70

    job_tokens = set(tokenize(job_desc))
    resume_tokens = set(tokenize(resume_text))
    overlap = job_tokens & resume_tokens
    context_score = (len(overlap) / len(job_tokens) * 100) if job_tokens else 50

    final_score = round(0.55 * skill_score + 0.25 * exp_score + 0.20 * context_score)
    final_score = max(5, min(98, final_score))

    if final_score >= 75:
        verdict = "Highly Recommended"
    elif final_score >= 50:
        verdict = "Consider"
    else:
        verdict = "Not a strong match"

    why = (
        f"The candidate matches {len(matched)} out of {len(job_skills) if job_skills else ''} key skills searched "
        f"({', '.join(matched) if matched else 'no direct matches detected'}). "
        f"Detected experience: approximately {resume_years} year(s), compared to {job_years_req} year(s) required. "
        + (f"Missing skills to clarify in interview: {', '.join(missing)}." if missing else
           "No key skills missing.")
    )

    return {
        "score": final_score,
        "verdict": verdict,
        "matched_skills": matched,
        "missing_skills": missing,
        "years_detected": resume_years,
        "why": why,
        "engine": "Local Engine (Rules + Keyword Match)  Free, no API call",
    }

def try_ai_scoring(resume_text, job_desc, provider, api_key):
    """Attempt scoring via a real LLM API if a key is provided."""
    prompt = f"""You are an expert recruitment assistant. Analyze this CV against this job offer.
Reply STRICTLY in JSON format, without surrounding text, with the keys:
score (integer 0-100), verdict (short sentence), matched_skills (list), missing_skills (list), why (2-3 sentences explaining the score).

JOB OFFER:
{job_desc}

CANDIDATE CV:
{resume_text}
"""
    try:
        if provider == "Claude (Anthropic)":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text
        elif provider == "OpenAI (GPT)":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.choices[0].message.content
        else:  # Gemini
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            raw = model.generate_content(prompt).text

        cleaned = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()
        data = json.loads(cleaned)
        data["engine"] = f"Live AI  {provider}"
        data["years_detected"] = extract_years_experience(resume_text)
        return data
    except Exception as e:
        st.warning(f"⚠️ Real API call unavailable ({e}). Falling back to the local demo engine.")
        return None

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

# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown("## 🎯 RecruitAI Pro")
st.sidebar.caption("Sales Demo  Automated CV Screening")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Solution Overview",
        "🏗️ Technical Architecture",
        "🗂️ Talent Pool & Dashboard",
        "💰 Cost & Timeline",
    ],
)
if st.sidebar.button("🧠 Try AI Scoring FREE", use_container_width=True):
    page = "🧠 AI Scoring Demo"
# Optional: API Settings for demo purposes

st.sidebar.markdown("---")
st.sidebar.caption("Presented by **Anas** · AI Automation Engineer\nContact: anaslachhab666@gmail.com \nWhatsapp: +212654615222")

# ============================================================
# PAGE 1  OVERVIEW
# ============================================================
if page == "🏠 Solution Overview":
    st.markdown("""
    <div class="hero">
        <h1>🎯 RecruitAI Pro</h1>
        <p>Complete CV sorting automation using Artificial Intelligence <br>from email reception 
        to interview scheduling, without manual intervention.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in zip(
        [c1, c2, c3, c4],
        ["-80%", "24/7", "< 30 sec", "100%"],
        ["Manual Sorting Time", "Automatic Processing", "Per CV Analyzed", "Candidate Traceability"]
    ):
        col.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("### How it works")
    steps = [
        ("1️⃣ Email / Career Site Connection", "Connects to Gmail or Outlook via API (OAuth) and the agency career site via its API."),
        ("2️⃣ Automatic Extraction", "Every new CV received (PDF/DOCX) is detected and its content is automatically extracted."),
        ("3️⃣ AI Analysis (Claude / GPT / Gemini)", "The CV is compared to the job description: relevance score, strengths, weaknesses, and detailed justification."),
        ("4️⃣ Database Recording (Talent Pool)", "Structured information (degree, experience, location, skills) is saved automatically."),
        ("5️⃣ Real-time HR Dashboard", "Recruiters visualize, filter, and sort all scored candidates without manually opening a single file."),
        ("6️⃣ Automated Scheduling", "If the score exceeds the defined threshold, a Calendly link is automatically sent to the candidate for an interview."),
    ]
    for title, desc in steps:
        st.markdown(f'<div class="step-box"><b>{title}</b><br><span style="color:#b8b8d1">{desc}</span></div>', unsafe_allow_html=True)

    st.markdown("### Why this solution?")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("""
        <div class="card">
        <h3>😩 Without Automation</h3>
        <ul>
        <li>Recruiter reads 100+ CVs/week manually</li>
        <li>Human bias, fatigue, inconsistent judgment</li>
        <li>Qualified candidates lost in the pile</li>
        <li>No reusable structured database</li>
        <li>Response time to candidates takes several days</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with colB:
        st.markdown("""
        <div class="card">
        <h3>🚀 With RecruitAI Pro</h3>
        <ul>
        <li>Sorting hundreds of CVs in minutes</li>
        <li>Objective, consistent score justified by AI</li>
        <li>Talent pool exploitable for future roles</li>
        <li>Interviews proposed automatically</li>
        <li>Recruiters focus on interviews, not sorting</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# PAGE 2  ARCHITECTURE
# ============================================================
elif page == "🏗️ Technical Architecture":
    st.markdown("## 🏗️ Technical Architecture")
    st.caption("Overview of the automation pipeline  from CV reception to scheduling.")

    dot = """
    digraph G {
        rankdir=LR;
        bgcolor="transparent";
        node [fontname="Helvetica" fontsize=11 style="filled,rounded" shape=box color="#3d3d5c" fontcolor="white"];
        edge [color="#8e44ad" fontcolor="#b8b8d1" fontname="Helvetica" fontsize=9];

        Gmail [label="📧 Gmail / Outlook API\\n(OAuth)" fillcolor="#2d1b4e"];
        Site [label="🌐 Career Site\\n(API if available)" fillcolor="#2d1b4e"];
        Parse [label="📄 Text Extraction\\nPDF / DOCX" fillcolor="#1b3a4e"];
        LLM [label="🧠 AI Engine\\nClaude / GPT / Gemini" fillcolor="#4e1b3a"];
        Score [label="📊 Scoring + Justification\\n(0-100)" fillcolor="#4e1b3a"];
        DB [label="🗄️ Database\\nStructured Talent Pool" fillcolor="#1b4e2d"];
        Dash [label="📈 HR Dashboard\\n(Real-time)" fillcolor="#1b4e2d"];
        Calendly [label="📅 Calendly\\nAuto-Invite if Score OK" fillcolor="#4e3a1b"];
        Reject [label="✉️ Auto Response\\nIf score is low" fillcolor="#4e3a1b"];

        Gmail -> Parse;
        Site -> Parse;
        Parse -> LLM;
        LLM -> Score;
        Score -> DB;
        DB -> Dash;
        Score -> Calendly [label="score ≥ threshold"];
        Score -> Reject [label="score < threshold"];
        Dash -> Calendly [label="manual HR validation" style=dashed];
    }
    """
    st.graphviz_chart(dot, use_container_width=True)

    st.markdown("### Component Details")
    tabs = st.tabs(["🔌 Email Connection", "🧠 AI Engine", "🗄️ Database", "📈 Dashboard", "📅 Scheduling"])

    with tabs[0]:
        st.markdown("""
        - **Gmail API** or **Microsoft Graph API (Outlook)** connected via OAuth2 (read-only access to incoming applications).
        - Automatic detection of new emails containing CV attachments (filtered by subject keywords or dedicated folders).
        - Optional: Webhook from the career site (e.g., application form → n8n webhook).
        """)
    with tabs[1]:
        st.markdown("""
        - Choice of provider based on budget: **Claude (Anthropic)**, **GPT (OpenAI)**, or **Gemini (Google)**.
        - Structured Prompt: CV + Job Desc → JSON (score, strengths, weaknesses, justification).
        - Orchestrated architecture with **n8n** (no-code/low-code workflow) + **Python (FastAPI)** for business logic.
        """)
    with tabs[2]:
        st.markdown("""
        - Structured Database (PostgreSQL / Airtable / Google Sheets depending on needs).
        - Automatically extracted fields: name, city, degree, years of experience, skills, score, status.
        - Serves as a **reusable Talent Pool** for future similar positions (search by filters).
        """)
    with tabs[3]:
        st.markdown("""
        - Dashboard using **Streamlit / Power BI** connected directly to the database.
        - Filters by position, city, score, status  pipeline view for HR tracking.
        - Secure web access, usable by the entire recruitment team.
        """)
    with tabs[4]:
        st.markdown("""
        - **Calendly API** integration: Interview link sent automatically via email if score ≥ threshold defined by the agency.
        - Personalized automatic response email sent to candidates not retained.
        - Recruiter maintains control: manual validation possible before sending if preferred.
        """)

# ============================================================
# PAGE 3  DEMO SCORING
# ============================================================
# ============================================================
# PAGE 3 — DEMO SCORING
# ============================================================
elif page == "🧠 AI Scoring Demo":
    st.markdown("## 🧠 Interactive Demo — AI CV Scoring (DeepSeek)")
    st.caption("Upload a candidate's CV (PDF or DOCX) and write the job description manually to run a live DeepSeek analysis.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Job Description")
        job_desc = st.text_area(
            "Write the job description",
            height=280,
            placeholder="Paste or write the job description here (required skills, experience, degree, languages, etc.)...",
        )

    with col2:
        st.markdown("#### 📄 Candidate CV")
        uploaded = st.file_uploader("Upload CV (PDF or DOCX only)", type=["pdf", "docx"])
        resume_text = ""
        if uploaded:
            resume_text = extract_text_from_upload(uploaded)
            with st.expander("📃 Extracted CV Text (preview)"):
                st.text_area("Extracted Text", value=resume_text, height=200, disabled=True)


    if st.button("🚀 Launch AI Analysis", type="primary", use_container_width=True):
        if not job_desc.strip():
            st.error("Please write a job description.")
        elif not uploaded:
            st.error("Please upload a CV in PDF or DOCX format.")
        elif not resume_text.strip():
            st.error("Could not extract any text from the uploaded CV.")
        else:
            with st.spinner("Analyzing with DeepSeek..."):
                result = call_deepseek_api(resume_text, job_desc)

            if result is None:
                st.stop()

            st.markdown("---")

            r1, r2 = st.columns([1, 2])
            with r1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result.get("score", 0),
                    title={"text": "Relevance Score / 100"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#8e44ad"},
                        "steps": [
                            {"range": [0, 50], "color": "#4e1b1b"},
                            {"range": [50, 75], "color": "#4e3a1b"},
                            {"range": [75, 100], "color": "#1b4e2d"},
                        ],
                        "threshold": {"line": {"color": "white", "width": 3}, "value": threshold},
                    },
                ))
                fig.update_layout(height=280, margin=dict(t=40, b=10), paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig, use_container_width=True)

                score = result.get("score", 0)
                pill_class = "pill-green" if score >= 75 else "pill-orange" if score >= 50 else "pill-red"
                st.markdown(f'<span class="pill {pill_class}">{result.get("verdict", "")}</span>', unsafe_allow_html=True)
                st.caption(f"🔧 {result.get('engine', 'DeepSeek')}")

            with r2:
                st.markdown("#### 🪪 Candidate Information")
                info_cols = st.columns(2)
                with info_cols[0]:
                    st.markdown(f"**👤 Name:** {result.get('name', 'Not found')}")
                    st.markdown(f"**🌍 Country:** {result.get('country', 'Not found')}")
                    st.markdown(f"**📧 Email:** {result.get('email', 'Not found')}")
                with info_cols[1]:
                    st.markdown(f"**📞 Phone:** {result.get('phone', 'Not found')}")
                    st.markdown(f"**🎓 Education Level:** {result.get('education_level', 'Not found')}")
                    st.markdown(f"**💼 Experience:** {result.get('experience_years', 'Not found')} year(s)")

                st.markdown("#### 💬 AI Justification")
                st.info(result.get("why", "No explanation provided."))

                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown("**✅ Matching Skills**")
                    if result.get("matched_skills"):
                        for s in result["matched_skills"]:
                            st.markdown(f"- {s}")
                    else:
                        st.caption("None detected")
                with cc2:
                    st.markdown("**⚠️ Missing Skills**")
                    if result.get("missing_skills"):
                        for s in result["missing_skills"]:
                            st.markdown(f"- {s}")
                    else:
                        st.caption("None")

                st.markdown("#### 📌 Automatic Action Triggered")
                if score >= threshold:
                    st.success("✅ Score above threshold → **Calendly link automatically sent** to candidate + HR notification.")
                else:
                    st.warning("❌ Score below threshold → candidate **archived in Talent Pool** + auto-rejection email sent.")
# ============================================================
# PAGE 4  TALENT POOL
# ============================================================
elif page == "🗂️ Talent Pool & Dashboard":
    st.markdown("## 🗂️ Talent Pool & HR Dashboard")
    df = load_candidates()

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="metric-card"><div class="val">{len(df)}</div><div class="lbl">Total Candidates</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="metric-card"><div class="val">{(df["AI Score"]>=75).sum()}</div><div class="lbl">Qualified (Score > 75)</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="metric-card"><div class="val">{(df["Status"]=="Interview Scheduled").sum()}</div><div class="lbl">Interviews Set</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="metric-card"><div class="val">{round(df["AI Score"].mean())}%</div><div class="lbl">Avg AI Score</div></div>', unsafe_allow_html=True)

    st.markdown("### All Candidates")
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


        
# ============================================================
# PAGE 5  SCHEDULING
# ============================================================

# ============================================================
# PAGE 6  PRICING & TIMELINE
# ============================================================
elif page == "💰 Cost & Timeline":
    st.markdown("## 💰 Implementation Cost & Delivery Timeline")

    st.markdown("### 📦 Packages")
    p1, p2, p3 = st.columns(3)
    plans = [
        ("Starter", "$500", "Gmail OR Outlook connection, AI scoring, simple talent pool (Google Sheets/Airtable), basic Streamlit dashboard.", "2 weeks"),
        ("Pro", "$1,000", "Gmail + Outlook + career site, PostgreSQL database, advanced dashboard, auto-Calendly integration, auto-response emails.", "3 to 4 weeks"),
        ("Enterprise", "On Quote", "Multi-agency, multi-position, existing ATS/CRM integration (Odoo, etc.), custom dashboards, priority support.", "5 to 8 weeks"),
    ]
    for col, (name, price, desc, delay) in zip([p1, p2, p3], plans):
        col.markdown(f"""
        <div class="card">
        <h3>{name}</h3>
        <div style="font-size:1.6rem; font-weight:700; color:#8e44ad;">{price}</div>
        <p style="color:#9a9ab0; font-size:0.85rem;">One-time Setup</p>
        <p>{desc}</p>
        <span class="pill pill-blue">⏱ {delay}</span>
        </div>
        """, unsafe_allow_html=True)

    st.caption("💡 Indicative rates to be adjusted based on the target market and actual client complexity.")


st.markdown('<div class="footer-note">RecruitAI Pro  Sales demo generated with Streamlit · Not connected to real live data</div>', unsafe_allow_html=True)
