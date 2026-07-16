import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import json
import random

# ============================================================
# 1. GESTION DE LA LANGUE (ÉCRAN D'ACCUEIL)
# ============================================================
if 'lang' not in st.session_state:
    st.set_page_config(page_title="RecruitAI Pro", page_icon="🎯", layout="centered")
    
    st.markdown("""
        <style>
        .lang-container { text-align: center; margin-top: 15%; padding: 3rem; background: #161824; border: 1px solid #3d3d5c; border-radius: 20px; }
        .title { color: white; font-size: 2rem; margin-bottom: 2rem; font-family: sans-serif; }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="lang-container">', unsafe_allow_html=True)
        st.markdown('<div class="title">Choose your language / Choisissez votre langue</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button("🇫🇷 Français", use_container_width=True):
            st.session_state.lang = "FR"
            st.rerun()
        if col2.button("🇺🇸 English", use_container_width=True):
            st.session_state.lang = "EN"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # Arrête l'exécution ici tant que la langue n'est pas choisie

# ============================================================
# 2. DICTIONNAIRE DE TRADUCTION COMPLET
# ============================================================
T = {
    "FR": {
        "nav_1": "🏠 Aperçu de la solution", "nav_2": "🏗️ Architecture technique", "nav_3": "🧠 Démo — Scoring IA",
        "nav_4": "🗂️ CVthèque & Dashboard", "nav_5": "📅 Prise de RDV automatique", "nav_6": "💰 Coût & Délais",
        "hero_title": "RecruitAI Pro — Screening CV Automatisé",
        "hero_desc": "Automatisation complète du tri des CV par Intelligence Artificielle — de la réception de l'email jusqu'à la proposition d'entretien, sans intervention manuelle.",
        "m1_l": "Temps de tri manuel", "m2_l": "Traitement automatique", "m3_l": "Par CV analysé", "m4_l": "Traçabilité candidats",
        "how_title": "Comment ça fonctionne",
        "step1_t": "1️⃣ Connexion boîte mail / site carrière", "step1_d": "Connexion à Gmail ou Outlook via API (OAuth), et/ou au site carrière.",
        "step2_t": "2️⃣ Extraction automatique", "step2_d": "Chaque nouveau CV reçu (PDF/DOCX) est détecté et son contenu extrait.",
        "step3_t": "3️⃣ Analyse IA (Claude / GPT / Gemini)", "step3_d": "Le CV est comparé à la fiche de poste : score, points forts, points faibles.",
        "step4_t": "4️⃣ Enregistrement en base (CVthèque)", "step4_d": "Informations structurées sauvegardées automatiquement.",
        "step5_t": "5️⃣ Dashboard RH en temps réel", "step5_d": "Le recruteur visualise, filtre et trie sans ouvrir un seul CV.",
        "step6_t": "6️⃣ Prise de RDV automatique", "step6_d": "Lien Calendly envoyé si le score dépasse le seuil.",
        "why_title": "Pourquoi cette solution ?",
        "bad_title": "😩 Sans automatisation", "good_title": "🚀 Avec RecruitAI Pro",
        "bad_list": ["Tri manuel de 100+ CV", "Biais humain et fatigue", "Perte de bons candidats", "Aucune base structurée", "Délais de réponse longs"],
        "good_list": ["Tri massif en minutes", "Score objectif et justifié", "CVthèque exploitable", "RDV auto pour les tops", "Focus sur l'humain"],
        "arch_title": "Pipeline d'automatisation",
        "job_label": "📋 Fiche de poste", "cv_label": "📄 CV du candidat", "analyze_btn": "🚀 Lancer l'analyse IA",
        "score_indicator": "Score de pertinence", "verdict_label": "Verdict IA", "matched_label": "✅ Compétences trouvées",
        "missing_label": "⚠️ Compétences manquantes", "action_label": "📌 Action automatique déclenchée",
        "stat_total": "Candidats total", "stat_top": "Score ≥ 75", "stat_prog": "Entretiens", "stat_hired": "Embauchés", "stat_avg": "Score moyen",
        "pricing_title": "💰 Coût de mise en place & délais de livraison", "pricing_setup": "Setup unique", "pricing_delay": "Délai",
        "dev_by": "Développé par Anas", "change_lang": "Changer de langue"
    },
    "EN": {
        "nav_1": "🏠 Solution Overview", "nav_2": "🏗️ Technical Architecture", "nav_3": "🧠 AI Scoring Demo",
        "nav_4": "🗂️ Talent Pool & Dashboard", "nav_5": "📅 Auto-Scheduling", "nav_6": "💰 Pricing & Timeline",
        "hero_title": "RecruitAI Pro — Automated CV Screening",
        "hero_desc": "Full end-to-end AI resume screening — from email reception to interview scheduling, without manual intervention.",
        "m1_l": "Manual sorting time", "m2_l": "Auto-processing", "m3_l": "Per analyzed CV", "m4_l": "Full Traceability",
        "how_title": "How it works",
        "step1_t": "1️⃣ Email / Career Site Connection", "step1_d": "Direct connection to Gmail/Outlook via API (OAuth) or career site hooks.",
        "step2_t": "2️⃣ Automatic Extraction", "step2_d": "Every new CV (PDF/DOCX) is detected and content is instantly extracted.",
        "step3_t": "3️⃣ AI Analysis (Claude / GPT / Gemini)", "step3_d": "CV is matched against the job description: score, pros, cons.",
        "step4_t": "4️⃣ Database Archiving (Talent Pool)", "step4_d": "Structured candidate information is automatically saved.",
        "step5_t": "5️⃣ Real-time HR Dashboard", "step5_d": "Filter and rank candidates without opening a single file.",
        "step6_t": "6️⃣ Auto-Scheduling", "step6_d": "Calendly link sent automatically if the score meets the threshold.",
        "why_title": "Why this solution?",
        "bad_title": "😩 Without Automation", "good_title": "🚀 With RecruitAI Pro",
        "bad_list": ["Manual 100+ CV sorting", "Human bias and fatigue", "Top talent lost in piles", "No structured database", "Slow response times"],
        "good_list": ["Massive sorting in minutes", "Objective AI-backed score", "Reusable talent pool", "Auto-booking for top tiers", "Focus on humans"],
        "arch_title": "Automation Pipeline",
        "job_label": "📋 Job Description", "cv_label": "📄 Candidate Resume", "analyze_btn": "🚀 Launch AI Analysis",
        "score_indicator": "Relevancy Score", "verdict_label": "AI Verdict", "matched_label": "✅ Matched Skills",
        "missing_label": "⚠️ Missing Skills", "action_label": "📌 Automatic Action Triggered",
        "stat_total": "Total Candidates", "stat_top": "Score ≥ 75", "stat_prog": "Scheduled", "stat_hired": "Hired", "stat_avg": "Avg Score",
        "pricing_title": "💰 Setup Cost & Delivery Timelines", "pricing_setup": "One-time setup", "pricing_delay": "Duration",
        "dev_by": "Developed by Anas", "change_lang": "Change Language"
    }
}

L = T[st.session_state.lang]

# ============================================================
# 3. PAGE CONFIG & STYLES (AS PER ORIGINAL)
# ============================================================
st.set_page_config(page_title=L["hero_title"], page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .hero { background: linear-gradient(135deg, #1a1c29 0%, #2d1b4e 100%); border: 1px solid #3d3d5c; border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem; }
    .hero h1 { font-size: 2.1rem; margin-bottom: 0.3rem; }
    .hero p { color: #b8b8d1; font-size: 1.05rem; }
    .card { background: #161824; border: 1px solid #2a2d40; border-radius: 14px; padding: 1.4rem 1.6rem; margin-bottom: 1rem; }
    .pill { display: inline-block; padding: 0.25rem 0.8rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; margin-right: 0.4rem; }
    .pill-green { background: rgba(46, 204, 113, 0.15); color: #2ecc71; border: 1px solid #2ecc71; }
    .pill-orange { background: rgba(243, 156, 18, 0.15); color: #f39c12; border: 1px solid #f39c12; }
    .pill-red { background: rgba(231, 76, 60, 0.15); color: #e74c3c; border: 1px solid #e74c3c; }
    .pill-blue { background: rgba(52, 152, 219, 0.15); color: #3498db; border: 1px solid #3498db; }
    .step-box { background: #161824; border-left: 4px solid #8e44ad; border-radius: 10px; padding: 1rem 1.3rem; margin-bottom: 0.7rem; }
    .metric-card { background: #161824; border: 1px solid #2a2d40; border-radius: 14px; padding: 1.1rem 1.3rem; text-align: center; }
    .metric-card .val { font-size: 1.8rem; font-weight: 700; }
    .metric-card .lbl { color: #9a9ab0; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. MOCK DATA & SAMPLES (MAPPED TO LANG)
# ============================================================
@st.cache_data
def load_candidates(lang, n=24):
    random.seed(42)
    rows = []
    cities = ["Casablanca", "Dubai", "Rabat", "Abu Dhabi"] if lang == "FR" else ["London", "Dubai", "New York", "Singapore"]
    postes = ["Développeur Full Stack", "Business Developer", "HR Manager", "Data Scientist"]
    statuts = ["Nouveau", "Présélectionné", "Entretien", "Rejeté"] if lang == "FR" else ["New", "Shortlisted", "Interview", "Rejected"]
    
    for i in range(n):
        score = random.randint(35, 98)
        rows.append({
            "ID": f"CAND-{1000+i}",
            "Nom": f"Candidate {i}",
            "Poste visé": random.choice(postes),
            "Ville": random.choice(cities),
            "Score IA": score,
            "Statut": random.choice(statuts),
            "Date": (datetime.now() - timedelta(days=random.randint(0, 45))).strftime("%d/%m/%Y"),
        })
    return pd.DataFrame(rows)

SAMPLE_JOBS = {
    "FR": {"Dev": "Expert Python, React, SQL. 3-5 ans d'expérience.", "Sales": "Vente B2B, CRM Salesforce, Anglais courant."},
    "EN": {"Dev": "Expert Python, React, SQL. 3-5 years experience.", "Sales": "B2B Sales, CRM Salesforce, Fluent English."}
}

# ============================================================
# 5. SIDEBAR NAVIGATION
# ============================================================
st.sidebar.markdown(f"## 🎯 {L['hero_title']}")
page = st.sidebar.radio("Navigation", [L["nav_1"], L["nav_2"], L["nav_3"], L["nav_4"], L["nav_5"], L["nav_6"]])

st.sidebar.markdown("---")
if st.sidebar.button(f"🔄 {L['change_lang']}"):
    del st.session_state.lang
    st.rerun()

st.sidebar.caption(f"{L['dev_by']} — AI Automation Engineer\n+212654615222")

# ============================================================
# PAGE 1 — APERÇU
# ============================================================
if page == L["nav_1"]:
    st.markdown(f'<div class="hero"><h1>{L["hero_title"]}</h1><p>{L["hero_desc"]}</p></div>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    vals = ["-80%", "24/7", "< 30s", "100%"]
    lbls = [L["m1_l"], L["m2_l"], L["m3_l"], L["m4_l"]]
    for col, v, lb in zip([c1, c2, c3, c4], vals, lbls):
        col.markdown(f'<div class="metric-card"><div class="val">{v}</div><div class="lbl">{lb}</div></div>', unsafe_allow_html=True)

    st.markdown(f"### {L['how_title']}")
    for i in range(1, 7):
        st.markdown(f'<div class="step-box"><b>{L[f"step{i}_t"]}</b><br><span style="color:#b8b8d1">{L[f"step{i}_d"]}</span></div>', unsafe_allow_html=True)

    colA, colB = st.columns(2)
    with colA:
        st.markdown(f'<div class="card"><h3>{L["bad_title"]}</h3><ul>' + "".join([f"<li>{item}</li>" for item in L["bad_list"]]) + '</ul></div>', unsafe_allow_html=True)
    with colB:
        st.markdown(f'<div class="card"><h3>{L["good_title"]}</h3><ul>' + "".join([f"<li>{item}</li>" for item in L["good_list"]]) + '</ul></div>', unsafe_allow_html=True)

# ============================================================
# PAGE 2 — ARCHITECTURE
# ============================================================
elif page == L["nav_2"]:
    st.markdown(f"## {L['nav_2']}")
    # Diagram simplified version for space, using the original flow
    dot = f"""
    digraph G {{
        rankdir=LR; bgcolor="transparent";
        node [fontname="Helvetica" shape=box style=filled color="#3d3d5c" fontcolor=white];
        edge [color="#8e44ad"];
        In [label="Gmail/Outlook/Web"] ; IA [label="AI Analysis (LLM)"] ; DB [label="Database"] ; Sch [label="Auto-Scheduling"];
        In -> IA -> DB; IA -> Sch [label="Score > 75"];
    }}
    """
    st.graphviz_chart(dot)

# ============================================================
# PAGE 3 — DEMO SCORING
# ============================================================
elif page == L["nav_3"]:
    st.markdown(f"## {L['nav_3']}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {L['job_label']}")
        job_txt = st.text_area("JD", SAMPLE_JOBS[st.session_state.lang]["Dev"], height=200)
    with col2:
        st.markdown(f"#### {L['cv_label']}")
        cv_txt = st.text_area("CV", "John Doe, Python expert, 4 years experience...", height=200)
    
    threshold = st.slider(L["threshold"], 0, 100, 70)
    if st.button(L["analyze_btn"], type="primary"):
        with st.spinner("Analyzing..."):
            score = random.randint(40, 98)
            st.markdown("---")
            r1, r2 = st.columns([1, 2])
            with r1:
                fig = go.Figure(go.Indicator(mode="gauge+number", value=score, title={'text': L["score_indicator"]}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#8e44ad"}}))
                fig.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig, use_container_width=True)
            with r2:
                st.markdown(f"#### {L['verdict_label']}")
                st.info("The candidate matches key technical requirements but lacks specific experience in FastAPI." if st.session_state.lang=="EN" else "Le candidat correspond aux attentes techniques mais manque d'expérience sur FastAPI.")
                st.write(f"**{L['matched_label']}**: Python, SQL, React")
                st.write(f"**{L['missing_label']}**: FastAPI, Docker")
                if score >= threshold:
                    st.success(L["action_label"] + ": Scheduling link sent!")

# ============================================================
# PAGE 4 — CVTHÈQUE
# ============================================================
elif page == L["nav_4"]:
    st.markdown(f"## {L['nav_4']}")
    df = load_candidates(st.session_state.lang)
    
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="metric-card"><div class="val">{len(df)}</div><div class="lbl">{L["stat_total"]}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="metric-card"><div class="val">{(df["Score IA"]>=75).sum()}</div><div class="lbl">{L["stat_top"]}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="metric-card"><div class="val">{round(df["Score IA"].mean())}</div><div class="lbl">{L["stat_avg"]}</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="metric-card"><div class="val">{(df["Statut"]=="Entretien").sum()}</div><div class="lbl">{L["stat_prog"]}</div></div>', unsafe_allow_html=True)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    fig = px.histogram(df, x="Score IA", nbins=15, title="Score Distribution", color_discrete_sequence=["#8e44ad"])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 5 — SCHEDULING
# ============================================================
elif page == L["nav_5"]:
    st.markdown(f"## {L['nav_5']}")
    df = load_candidates(st.session_state.lang)
    qualified = df[df["Score IA"] >= 75].sort_values("Score IA", ascending=False)
    
    for _, cand in qualified.head(5).iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{cand['Nom']}** — {cand['Poste visé']}")
            c2.markdown(f'<span class="pill pill-green">{cand["Score IA"]}/100</span>', unsafe_allow_html=True)
            if c3.button("Send Invite", key=cand['ID']):
                st.toast(f"Invite sent to {cand['Nom']}")
            st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)

# ============================================================
# PAGE 6 — PRICING & TIMELINE
# ============================================================
elif page == L["nav_6"]:
    st.markdown(f"## {L['pricing_title']}")
    p1, p2, p3 = st.columns(3)
    plans = [
        ("Starter", "500 $", "2 weeks"),
        ("Pro", "1000 $", "4 weeks"),
        ("Enterprise", "Quote", "8 weeks"),
    ]
    for col, (name, price, delay) in zip([p1, p2, p3], plans):
        col.markdown(f"""
        <div class="card">
        <h3>{name}</h3>
        <div style="font-size:1.6rem; font-weight:700; color:#8e44ad;">{price}</div>
        <p>{L['pricing_setup']}</p>
        <span class="pill pill-blue">⏱ {L['pricing_delay']}: {delay}</span>
        </div>
        """, unsafe_allow_html=True)

    # GANTT Chart
    phases = [("Design", 0, 5), ("Dev", 5, 15), ("AI Logic", 15, 25), ("Launch", 25, 30)]
    g_df = pd.DataFrame([dict(Task=p[0], Start=p[1], End=p[2]) for p in phases])
    fig = px.timeline(g_df, x_start="Start", x_end="End", y="Task", title="Implementation Timeline (Days)")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div style="text-align:center; color:#6c6c85; font-size:0.8rem; margin-top:3rem;">RecruitAI Pro — Commercial Demo © 2024</div>', unsafe_allow_html=True)
