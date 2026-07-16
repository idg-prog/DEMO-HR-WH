"""
RecruitAI Pro — AI CV Screening Automation Demo
Developed for Sales Demonstration (Recruitment Agencies / HR)
Author: Anas — AI Automation Engineer
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import json
import random

# ============================================================
# 🌐 MULTILINGUAL SYSTEM
# ============================================================
if 'lang' not in st.session_state:
    st.session_state.lang = "Français"

def toggle_lang():
    if st.session_state.lang_selector == "English":
        st.session_state.lang = "English"
    else:
        st.session_state.lang = "Français"

# Translation Dictionary
T = {
    "Français": {
        "title": "RecruitAI Pro — Screening CV Automatisé",
        "nav_1": "🏠 Aperçu de la solution",
        "nav_2": "🏗️ Architecture technique",
        "nav_3": "🧠 Démo — Scoring IA",
        "nav_4": "🗂️ CVthèque & Dashboard",
        "nav_5": "📅 Prise de RDV automatique",
        "nav_6": "💰 Coût & Délais",
        "hero_sub": "Automatisation complète du tri des CV par IA — de la réception de l'email jusqu'à l'entretien.",
        "m1_val": "-80%", "m1_lbl": "Temps de tri manuel",
        "m2_val": "24/7", "m2_lbl": "Traitement automatique",
        "m3_val": "< 30s", "m3_lbl": "Par CV analysé",
        "m4_val": "100%", "m4_lbl": "Traçabilité candidats",
        "how_it_works": "Comment ça fonctionne",
        "step1_t": "1️⃣ Connexion boîte mail", "step1_d": "Connexion à Gmail/Outlook via API (OAuth) pour détecter les nouveaux CV.",
        "step2_t": "2️⃣ Extraction auto", "step2_d": "Le texte est extrait des PDF/DOCX dès réception.",
        "step3_t": "3️⃣ Analyse IA", "step3_d": "Comparaison intelligente avec la fiche de poste (Score & Justification).",
        "step4_t": "4️⃣ CVthèque", "step4_d": "Données structurées sauvegardées automatiquement en base de données.",
        "step5_t": "5️⃣ Dashboard RH", "step5_d": "Visualisation et filtrage des meilleurs profils en temps réel.",
        "step6_t": "6️⃣ RDV Automatique", "step6_d": "Envoi automatique d'un lien Calendly si le score est élevé.",
        "why_title": "Pourquoi cette solution ?",
        "bad_side": "😩 Sans automatisation",
        "good_side": "🚀 Avec RecruitAI Pro",
        "job_desc_label": "📋 Fiche de poste",
        "cv_label": "📄 CV du candidat",
        "btn_analyze": "🚀 Lancer l'analyse IA",
        "score_label": "Score de pertinence",
        "verdict_label": "Verdict IA",
        "matched_skills": "✅ Compétences trouvées",
        "missing_skills": "⚠️ Compétences manquantes",
        "action_triggered": "📌 Action automatique déclenchée",
        "pricing_starter": "Starter",
        "pricing_pro": "Pro",
        "pricing_ent": "Enterprise",
        "setup_fee": "Frais de mise en place unique",
        "duration": "Délai",
        "source_label": "Source du CV",
        "example": "Exemple",
        "upload": "Uploader un fichier",
        "threshold": "Seuil de recommandation auto",
        "total_cand": "Candidats total",
        "avg_score": "Score moyen",
        "hired": "Embauchés",
        "interviews": "Entretiens",
    },
    "English": {
        "title": "RecruitAI Pro — Automated CV Screening",
        "nav_1": "🏠 Solution Overview",
        "nav_2": "🏗️ Technical Architecture",
        "nav_3": "🧠 AI Scoring Demo",
        "nav_4": "🗂️ Talent Pool & Dashboard",
        "nav_5": "📅 Auto-Scheduling",
        "nav_6": "💰 Pricing & Timeline",
        "hero_sub": "End-to-end AI resume screening — from email reception to interview scheduling.",
        "m1_val": "-80%", "m1_lbl": "Manual sorting time",
        "m2_val": "24/7", "m2_lbl": "Automatic processing",
        "m3_val": "< 30s", "m3_lbl": "Per analyzed CV",
        "m4_val": "100%", "m4_lbl": "Candidate traceability",
        "how_it_works": "How it works",
        "step1_t": "1️⃣ Mailbox Connection", "step1_d": "Connection to Gmail/Outlook via API (OAuth) to detect new resumes.",
        "step2_t": "2️⃣ Auto Extraction", "step2_d": "Text is extracted from PDF/DOCX instantly upon receipt.",
        "step3_t": "3️⃣ AI Analysis", "step3_d": "Smart comparison with the job description (Score & Logic).",
        "step4_t": "4️⃣ Talent Pool", "step4_d": "Structured data automatically saved in the database.",
        "step5_t": "5️⃣ HR Dashboard", "step5_d": "Visualize and filter top talent in real-time.",
        "step6_t": "6️⃣ Auto-Scheduling", "step6_d": "Auto-send Calendly link if the score meets the threshold.",
        "why_title": "Why this solution?",
        "bad_side": "😩 Without Automation",
        "good_side": "🚀 With RecruitAI Pro",
        "job_desc_label": "📋 Job Description",
        "cv_label": "📄 Candidate Resume",
        "btn_analyze": "🚀 Run AI Analysis",
        "score_label": "Relevancy Score",
        "verdict_label": "AI Verdict",
        "matched_skills": "✅ Matched Skills",
        "missing_skills": "⚠️ Missing Skills",
        "action_triggered": "📌 Automatic action triggered",
        "pricing_starter": "Starter",
        "pricing_pro": "Pro",
        "pricing_ent": "Enterprise",
        "setup_fee": "One-time setup fee",
        "duration": "Duration",
        "source_label": "Resume Source",
        "example": "Example",
        "upload": "Upload a file",
        "threshold": "Auto-recommendation threshold",
        "total_cand": "Total Candidates",
        "avg_score": "Average Score",
        "hired": "Hired",
        "interviews": "Interviews",
    }
}

L = T[st.session_state.lang]

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title=L["title"],
    page_icon="🎯",
    layout="wide",
)

# ============================================================
# STYLE (CSS)
# ============================================================
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .hero {
        background: linear-gradient(135deg, #1a1c29 0%, #2d1b4e 100%);
        border: 1px solid #3d3d5c; border-radius: 16px;
        padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    }
    .card {
        background: #161824; border: 1px solid #2a2d40;
        border-radius: 14px; padding: 1.4rem 1.6rem; margin-bottom: 1rem;
    }
    .pill {
        display: inline-block; padding: 0.25rem 0.8rem; border-radius: 999px;
        font-size: 0.8rem; font-weight: 600; margin-right: 0.4rem;
    }
    .pill-green { background: rgba(46, 204, 113, 0.15); color: #2ecc71; border: 1px solid #2ecc71; }
    .pill-orange { background: rgba(243, 156, 18, 0.15); color: #f39c12; border: 1px solid #f39c12; }
    .pill-red { background: rgba(231, 76, 60, 0.15); color: #e74c3c; border: 1px solid #e74c3c; }
    .pill-blue { background: rgba(52, 152, 219, 0.15); color: #3498db; border: 1px solid #3498db; }
    .metric-card {
        background: #161824; border: 1px solid #2a2d40; border-radius: 14px;
        padding: 1.1rem 1.3rem; text-align: center;
    }
    .metric-card .val { font-size: 1.8rem; font-weight: 700; color: #fff; }
    .metric-card .lbl { color: #9a9ab0; font-size: 0.85rem; }
    .step-box {
        background: #161824; border-left: 4px solid #8e44ad;
        padding: 1rem; margin-bottom: 0.7rem; border-radius: 0 10px 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MOCK DATA GENERATOR
# ============================================================
@st.cache_data
def load_mock_data(lang, n=24):
    random.seed(42)
    if lang == "English":
        CITIES = ["Dubai", "Abu Dhabi", "New York", "London", "Singapore", "Casablanca"]
        POSTES = ["Full Stack Developer", "Business Developer", "HR Manager", "Data Analyst", "DevOps Engineer"]
        DIPLOMES = ["Master's Degree", "Bachelor's Degree", "PhD", "MBA"]
        STATUTS = ["New", "Shortlisted", "Interviewing", "Rejected", "Hired"]
        PRENOMS = ["James", "Emma", "Liam", "Olivia", "Noah", "Sophia", "Youssef", "Layla"]
    else:
        CITIES = ["Casablanca", "Rabat", "Marrakech", "Tanger", "Dubai", "Paris"]
        POSTES = ["Développeur Full Stack", "Business Developer", "Chargé RH", "Data Analyst", "Ingénieur DevOps"]
        DIPLOMES = ["Bac+5 Ingénieur", "Master Finance", "Bac+3 Licence Pro", "MBA"]
        STATUTS = ["Nouveau", "Présélectionné", "Entretien", "Rejeté", "Embauché"]
        PRENOMS = ["Youssef", "Salma", "Amine", "Sara", "Karim", "Nour", "Omar", "Imane"]
    
    NOMS = ["Smith", "El Amrani", "Bennani", "Johnson", "Alaoui", "Williams"]
    
    rows = []
    for i in range(n):
        score = random.randint(30, 98)
        rows.append({
            "ID": f"CAND-{1000+i}",
            "Nom": f"{random.choice(PRENOMS)} {random.choice(NOMS)}",
            "Poste": random.choice(POSTES),
            "Ville": random.choice(CITIES),
            "Score IA": score,
            "Statut": random.choice(STATUTS),
            "Email": f"candidate{i}@example.com",
            "Exp (ans)": random.randint(1, 15)
        })
    return pd.DataFrame(rows)

# ============================================================
# SAMPLE DATA FOR DEMO
# ============================================================
SAMPLES = {
    "Français": {
        "jobs": {
            "Développeur Full Stack": "Expertise en Python, React, FastAPI. Minimum 3 ans d'expérience.",
            "Business Developer": "Prospection B2B, CRM Salesforce, Anglais courant exigé."
        },
        "resumes": {
            "Profil A (Fort)": "Youssef. 5 ans d'exp en Python et React. Anglais courant.",
            "Profil B (Junior)": "Sara. 1 an d'exp en HTML/CSS. Débutante en Python."
        }
    },
    "English": {
        "jobs": {
            "Full Stack Developer": "Expertise in Python, React, FastAPI. Minimum 3 years experience.",
            "Business Developer": "B2B Sales, CRM Salesforce, Fluent English required."
        },
        "resumes": {
            "Profile A (Strong)": "James. 5 years exp in Python and React. Fluent English.",
            "Profile B (Junior)": "Emma. 1 year exp in HTML/CSS. Python beginner."
        }
    }
}

# ============================================================
# SCORING ENGINE (LOCAL FALLBACK)
# ============================================================
def score_local(resume, job, lang):
    score = random.randint(40, 95) if len(resume) > 10 else 10
    verdict = "Fortement recommandé" if score > 75 else "À considérer" if score > 50 else "Peu adapté"
    if lang == "English":
        verdict = "Highly Recommended" if score > 75 else "To Consider" if score > 50 else "Not Suitable"
    
    return {
        "score": score,
        "verdict": verdict,
        "matched": ["Python", "React", "English"] if score > 50 else ["Communication"],
        "missing": ["Docker", "FastAPI"] if score < 80 else [],
        "why": "Matching criteria based on skills and experience." if lang == "English" else "Correspondance basée sur les compétences et l'expérience."
    }

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.radio("🌐 Language / Langue", ["Français", "English"], key="lang_selector", on_change=toggle_lang, horizontal=True)
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", [L["nav_1"], L["nav_2"], L["nav_3"], L["nav_4"], L["nav_5"], L["nav_6"]])
st.sidebar.markdown("---")
st.sidebar.caption("By Anas Lachhab\nAI Automation Engineer\n+212 654 615 222")

# ============================================================
# PAGE 1: OVERVIEW
# ============================================================
if page == L["nav_1"]:
    st.markdown(f"""<div class="hero"><h1>{L['title']}</h1><p>{L['hero_sub']}</p></div>""", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in zip([c1, c2, c3, c4], [L['m1_val'], L['m2_val'], L['m3_val'], L['m4_val']], [L['m1_lbl'], L['m2_lbl'], L['m3_lbl'], L['m4_lbl']]):
        col.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown(f"### {L['how_it_works']}")
    for t, d in zip([L[f"step{i}_t"] for i in range(1,7)], [L[f"step{i}_d"] for i in range(1,7)]):
        st.markdown(f'<div class="step-box"><b>{t}</b><br><span style="color:#b8b8d1">{d}</span></div>', unsafe_allow_html=True)

# ============================================================
# PAGE 2: ARCHITECTURE
# ============================================================
elif page == L["nav_2"]:
    st.markdown(f"## {L['nav_2']}")
    labels = {
        "Français": ["Email/Site", "Extraction Texte", "Moteur IA", "Scoring", "Base de données", "Dashboard"],
        "English": ["Email/Web", "Text Extraction", "AI Engine", "Scoring", "Database", "Dashboard"]
    }
    cur = labels[st.session_state.lang]
    dot = f"""
    digraph G {{
        rankdir=LR; bgcolor="transparent";
        node [fontname="Helvetica" shape=box style=filled color="#3d3d5c" fontcolor=white];
        A [label="{cur[0]}"] ; B [label="{cur[1]}"] ; C [label="{cur[2]}"] ;
        D [label="{cur[3]}"] ; E [label="{cur[4]}"] ; F [label="{cur[5]}"];
        A -> B -> C -> D -> E -> F;
    }}
    """
    st.graphviz_chart(dot)

# ============================================================
# PAGE 3: DEMO
# ============================================================
elif page == L["nav_3"]:
    st.markdown(f"## {L['nav_3']}")
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.selectbox(L["job_desc_label"], list(SAMPLES[st.session_state.lang]["jobs"].keys()))
        job_text = st.text_area("Content", SAMPLES[st.session_state.lang]["jobs"][job_title], height=150)
    with col2:
        cv_title = st.selectbox(L["cv_label"], list(SAMPLES[st.session_state.lang]["resumes"].keys()))
        cv_text = st.text_area("CV Content", SAMPLES[st.session_state.lang]["resumes"][cv_title], height=150)
    
    threshold = st.slider(L["threshold"], 0, 100, 70)
    
    if st.button(L["btn_analyze"], type="primary"):
        res = score_local(cv_text, job_text, st.session_state.lang)
        st.markdown("---")
        r1, r2 = st.columns([1, 2])
        with r1:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=res["score"], title={'text': L["score_label"]},
                gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#8e44ad"}}))
            fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**{L['verdict_label']}:** {res['verdict']}")
        with r2:
            st.info(res["why"])
            st.write(f"**{L['matched_skills']}** : {', '.join(res['matched'])}")
            st.write(f"**{L['missing_skills']}** : {', '.join(res['missing'])}")
            if res["score"] >= threshold:
                st.success(f"✅ {L['action_triggered']}: Calendly Link Sent.")
            else:
                st.warning(f"❌ {L['action_triggered']}: Archived in Pool.")

# ============================================================
# PAGE 4: DASHBOARD
# ============================================================
elif page == L["nav_4"]:
    st.markdown(f"## {L['nav_4']}")
    df = load_mock_data(st.session_state.lang)
    
    k1, k2, k3 = st.columns(3)
    k1.metric(L["total_cand"], len(df))
    k2.metric(L["avg_score"], f"{round(df['Score IA'].mean())}%")
    k3.metric(L["interviews"], f"{len(df[df['Score IA']>70])}")
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    fig = px.histogram(df, x="Score IA", title="Distribution", color_discrete_sequence=["#8e44ad"])
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 5: SCHEDULING
# ============================================================
elif page == L["nav_5"]:
    st.markdown(f"## {L['nav_5']}")
    df = load_mock_data(st.session_state.lang)
    qualified = df[df["Score IA"] >= 75]
    
    for _, row in qualified.head(5).iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{row['Nom']}** - {row['Poste']}")
            c2.markdown(f'<span class="pill pill-green">{row["Score IA"]}%</span>', unsafe_allow_html=True)
            if c3.button("Invite", key=row['ID']):
                st.toast(f"Email sent to {row['Nom']}")
            st.markdown("---")

# ============================================================
# PAGE 6: PRICING
# ============================================================
elif page == L["nav_6"]:
    st.markdown(f"## {L['nav_6']}")
    p1, p2, p3 = st.columns(3)
    plans = [
        (L["pricing_starter"], "500$", "2 weeks"),
        (L["pricing_pro"], "1200$", "4 weeks"),
        (L["pricing_ent"], "Custom", "8 weeks"),
    ]
    for col, (name, price, delay) in zip([p1, p2, p3], plans):
        col.markdown(f"""
        <div class="card">
            <h3>{name}</h3>
            <h2 style="color:#8e44ad">{price}</h2>
            <p>{L['setup_fee']}</p>
            <p><b>{L['duration']}:</b> {delay}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div style="text-align:center; color:#666; margin-top:50px">RecruitAI Pro Demo © 2024</div>', unsafe_allow_html=True)
