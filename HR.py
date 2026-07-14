"""
RecruitAI Pro — Démo d'automatisation de screening CV par IA
Développé pour démonstration commerciale (cabinets de recrutement / RH)
Auteur: Anas — AI Automation Engineer
Stack démo: Streamlit (déployable sur Streamlit Community Cloud)
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
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="RecruitAI Pro — Screening CV Automatisé",
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
# MOCK DATA — CVTHÈQUE
# ============================================================
CITIES = ["Casablanca", "Rabat", "Marrakech", "Tanger", "Dubai", "Abu Dhabi", "Fès", "Agadir"]
POSTES = ["Développeur Full Stack", "Business Developer", "Comptable Senior", "Chef de Projet IT",
          "Ingénieur DevOps", "Chargé RH", "Data Analyst", "Responsable Marketing"]
DIPLOMES = ["Bac+5 Ingénieur", "Master Finance", "Bac+3 Licence Pro", "MBA", "Bac+5 Data Science",
            "Master RH", "Bac+2 BTS", "Doctorat"]
STATUTS = ["Nouveau", "Présélectionné", "Entretien programmé", "Rejeté", "Embauché"]
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
            "Nom": f"{random.choice(PRENOMS)} {random.choice(NOMS)}",
            "Poste visé": random.choice(POSTES),
            "Ville": random.choice(CITIES),
            "Diplôme": random.choice(DIPLOMES),
            "Expérience (ans)": random.randint(0, 12),
            "Score IA": score,
            "Statut": random.choice(STATUTS) if score < 90 else random.choice(["Présélectionné", "Entretien programmé", "Embauché"]),
            "Email": f"{random.choice(PRENOMS).lower()}.{random.choice(NOMS).lower().replace(' ', '')}@email.com",
            "Source": random.choice(["Gmail", "Outlook", "Site carrière"]),
            "Date réception": (datetime.now() - timedelta(days=random.randint(0, 45))).strftime("%d/%m/%Y"),
        })
    return pd.DataFrame(rows)

# ============================================================
# CV SAMPLES (pour la démo sans upload)
# ============================================================
SAMPLE_JOBS = {
    "Développeur Full Stack (Casablanca)": """Nous recherchons un Développeur Full Stack (H/F) basé à Casablanca.
Compétences requises: Python, JavaScript, React, FastAPI, SQL, Git, Docker.
Expérience: 3 à 6 ans minimum en développement web.
Diplôme: Bac+5 Ingénieur informatique ou équivalent.
Anglais professionnel requis. Autonomie, esprit d'équipe, capacité à travailler en environnement agile.""",
    "Business Developer (Dubai)": """Poste de Business Developer basé à Dubai, UAE.
Compétences requises: prospection B2B, négociation, CRM (Odoo/Salesforce), anglais courant, arabe un plus.
Expérience: 2 à 5 ans en développement commercial, idéalement secteur tech ou services.
Diplôme: Bac+5 École de commerce ou équivalent.
Permis de conduire souhaité, disponibilité pour déplacements régionaux.""",
}

SAMPLE_RESUMES = {
    "Candidat A — Profil Dev fort": """Youssef El Amrani
Casablanca, Maroc | youssef.elamrani@email.com
Ingénieur informatique, Bac+5 (ENSIAS)

Expérience:
- 4 ans en développement Full Stack (Python, FastAPI, React, PostgreSQL)
- Mise en place de pipelines CI/CD avec Docker et Git
- Expérience agile (Scrum), travail en équipe internationale

Compétences: Python, JavaScript, React, SQL, Docker, Git, FastAPI, API REST
Langues: Français (natif), Anglais (professionnel), Arabe (natif)
""",
    "Candidat B — Profil junior": """Sara Bennani
Rabat, Maroc | sara.bennani@email.com
Licence Pro Informatique, Bac+3

Expérience:
- 1 an de stage en développement web (HTML, CSS, JavaScript)
- Projet académique de site e-commerce avec PHP

Compétences: HTML, CSS, JavaScript, PHP, notions de MySQL
Langues: Français (natif), Anglais (intermédiaire)
""",
    "Candidat C — Profil Business Dev": """Karim Tazi
Dubai, UAE | karim.tazi@email.com
MBA, Bac+5 École de commerce

Expérience:
- 5 ans en développement commercial B2B secteur tech, marché GCC
- Gestion CRM (Salesforce), closing de contrats > 100K USD
- Anglais courant, arabe natif, réseau professionnel Dubai/Abu Dhabi

Compétences: Négociation, prospection B2B, CRM, closing, gestion de comptes clés
Langues: Arabe (natif), Anglais (courant), Français (professionnel)
""",
}

STOPWORDS = set("""le la les un une des du de et à a au aux en pour par sur avec dans ou est sont
this that the a an and or of to for with in on is are will be we you your our
h f poste recherche recherchons requises requis minimum idéalement""".split())

SKILL_BANK = ["python", "javascript", "react", "sql", "docker", "git", "fastapi", "java", "php",
              "html", "css", "excel", "power bi", "sap", "odoo", "salesforce", "crm", "négociation",
              "prospection", "marketing", "comptabilité", "finance", "rh", "communication", "anglais",
              "arabe", "français", "agile", "scrum", "devops", "data", "mysql", "postgresql", "aws"]

# ============================================================
# LOCAL SCORING ENGINE (fallback sans clé API — 100% gratuit)
# ============================================================
def extract_years_experience(text):
    matches = re.findall(r"(\d+)\s*(?:ans|an|years?)", text.lower())
    return max([int(m) for m in matches], default=0)

def extract_skills(text):
    text_low = text.lower()
    return sorted({s for s in SKILL_BANK if s in text_low})

def tokenize(text):
    words = re.findall(r"[a-zàâäéèêëïîôöùûüç]+", text.lower())
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
        verdict = "Fortement recommandé"
    elif final_score >= 50:
        verdict = "À considérer"
    else:
        verdict = "Peu adapté au poste"

    why = (
        f"Le candidat maîtrise {len(matched)} des {len(job_skills) if job_skills else '—'} compétences clés recherchées "
        f"({', '.join(matched) if matched else 'aucune correspondance directe détectée'}). "
        f"Expérience détectée: environ {resume_years} an(s), contre {job_years_req} an(s) requis. "
        + (f"Compétences manquantes à clarifier en entretien: {', '.join(missing)}." if missing else
           "Aucune compétence clé manquante détectée.")
    )

    return {
        "score": final_score,
        "verdict": verdict,
        "matched_skills": matched,
        "missing_skills": missing,
        "years_detected": resume_years,
        "why": why,
        "engine": "Moteur local (règles + correspondance mots-clés) — gratuit, sans appel API",
    }

def try_ai_scoring(resume_text, job_desc, provider, api_key):
    """Tente un scoring via une vraie API LLM si une clé est fournie dans la démo live."""
    prompt = f"""Tu es un assistant de recrutement expert. Analyse ce CV par rapport à cette offre d'emploi.
Réponds STRICTEMENT en JSON, sans texte autour, avec les clés:
score (entier 0-100), verdict (courte phrase), matched_skills (liste), missing_skills (liste), why (2-3 phrases expliquant le score).

OFFRE D'EMPLOI:
{job_desc}

CV DU CANDIDAT:
{resume_text}
"""
    try:
        if provider == "Claude (Anthropic)":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            resp = client.messages.create(
                model="claude-sonnet-4-6",
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
        data["engine"] = f"IA en direct — {provider}"
        data["years_detected"] = extract_years_experience(resume_text)
        return data
    except Exception as e:
        st.warning(f"⚠️ Appel API réel indisponible ({e}). Bascule sur le moteur local de démo.")
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
st.sidebar.caption("Démo commerciale — Automatisation screening CV")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Aperçu de la solution",
        "🏗️ Architecture technique",
        "🧠 Démo — Scoring IA",
        "🗂️ CVthèque & Dashboard",
        "📅 Prise de RDV automatique",
        "💰 Coût & Délais",
    ],
)

with st.sidebar.expander("⚙️ Mode Démo Live (optionnel)"):
    st.caption("Branche une vraie clé API pour scorer un CV en direct pendant la démo. Rien n'est stocké.")
    ai_provider = st.selectbox("Fournisseur IA", ["Aucun (moteur local gratuit)", "Claude (Anthropic)", "OpenAI (GPT)", "Gemini (Google)"])
    ai_key = st.text_input("Clé API", type="password") if ai_provider != "Aucun (moteur local gratuit)" else None

st.sidebar.markdown("---")
st.sidebar.caption("Proposé par **Anas** · AI Automation Engineer\nContact commercial : votre-email@domaine.com")

# ============================================================
# PAGE 1 — APERÇU
# ============================================================
if page == "🏠 Aperçu de la solution":
    st.markdown("""
    <div class="hero">
        <h1>🎯 RecruitAI Pro</h1>
        <p>Automatisation complète du tri des CV par Intelligence Artificielle — de la réception de l'email
        jusqu'à la proposition d'entretien, sans intervention manuelle.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in zip(
        [c1, c2, c3, c4],
        ["-80%", "24/7", "< 30 sec", "100%"],
        ["Temps de tri manuel", "Traitement automatique", "Par CV analysé", "Traçabilité candidats"]
    ):
        col.markdown(f'<div class="metric-card"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("### Comment ça fonctionne")
    steps = [
        ("1️⃣ Connexion boîte mail / site carrière", "Connexion à Gmail ou Outlook via API (OAuth), et/ou au site carrière de l'agence via son API si disponible."),
        ("2️⃣ Extraction automatique", "Chaque nouveau CV reçu (PDF/DOCX) est détecté et son contenu extrait automatiquement."),
        ("3️⃣ Analyse IA (Claude / GPT / Gemini)", "Le CV est comparé à la fiche de poste : score de pertinence, points forts, points faibles, justification détaillée."),
        ("4️⃣ Enregistrement en base (CVthèque)", "Informations structurées (diplôme, expérience, localisation, compétences) sauvegardées automatiquement."),
        ("5️⃣ Dashboard RH en temps réel", "Le recruteur visualise, filtre et trie tous les candidats scorés, sans ouvrir un seul CV manuellement."),
        ("6️⃣ Prise de RDV automatique", "Si le score dépasse le seuil défini, un lien Calendly est envoyé automatiquement au candidat pour planifier l'entretien."),
    ]
    for title, desc in steps:
        st.markdown(f'<div class="step-box"><b>{title}</b><br><span style="color:#b8b8d1">{desc}</span></div>', unsafe_allow_html=True)

    st.markdown("### Pourquoi cette solution ?")
    colA, colB = st.columns(2)
    with colA:
        st.markdown("""
        <div class="card">
        <h3>😩 Sans automatisation</h3>
        <ul>
        <li>Un recruteur lit 100+ CV/semaine manuellement</li>
        <li>Biais humain, fatigue, incohérence de jugement</li>
        <li>Candidats qualifiés perdus dans la pile</li>
        <li>Aucune base de données structurée réutilisable</li>
        <li>Délai de réponse aux candidats de plusieurs jours</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    with colB:
        st.markdown("""
        <div class="card">
        <h3>🚀 Avec RecruitAI Pro</h3>
        <ul>
        <li>Tri de centaines de CV en quelques minutes</li>
        <li>Score objectif, cohérent, justifié par l'IA</li>
        <li>CVthèque exploitable pour de futurs postes</li>
        <li>Entretien proposé automatiquement aux meilleurs profils</li>
        <li>Le recruteur se concentre sur l'entretien, pas le tri</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# PAGE 2 — ARCHITECTURE
# ============================================================
elif page == "🏗️ Architecture technique":
    st.markdown("## 🏗️ Architecture technique")
    st.caption("Vue d'ensemble du pipeline d'automatisation — de la réception du CV à la prise de RDV.")

    dot = """
    digraph G {
        rankdir=LR;
        bgcolor="transparent";
        node [fontname="Helvetica" fontsize=11 style="filled,rounded" shape=box color="#3d3d5c" fontcolor="white"];
        edge [color="#8e44ad" fontcolor="#b8b8d1" fontname="Helvetica" fontsize=9];

        Gmail [label="📧 Gmail / Outlook API\\n(OAuth)" fillcolor="#2d1b4e"];
        Site [label="🌐 Site carrière\\n(API si dispo)" fillcolor="#2d1b4e"];
        Parse [label="📄 Extraction texte\\nPDF / DOCX" fillcolor="#1b3a4e"];
        LLM [label="🧠 Moteur IA\\nClaude / GPT / Gemini" fillcolor="#4e1b3a"];
        Score [label="📊 Scoring + Justification\\n(0-100)" fillcolor="#4e1b3a"];
        DB [label="🗄️ Base de données\\nCVthèque structurée" fillcolor="#1b4e2d"];
        Dash [label="📈 Dashboard RH\\n(temps réel)" fillcolor="#1b4e2d"];
        Calendly [label="📅 Calendly\\nRDV auto si score OK" fillcolor="#4e3a1b"];
        Reject [label="✉️ Email réponse\\nautomatique si score faible" fillcolor="#4e3a1b"];

        Gmail -> Parse;
        Site -> Parse;
        Parse -> LLM;
        LLM -> Score;
        Score -> DB;
        DB -> Dash;
        Score -> Calendly [label="score ≥ seuil"];
        Score -> Reject [label="score < seuil"];
        Dash -> Calendly [label="validation manuelle RH" style=dashed];
    }
    """
    st.graphviz_chart(dot, use_container_width=True)

    st.markdown("### Détail des composants")
    tabs = st.tabs(["🔌 Connexion emails", "🧠 Moteur IA", "🗄️ Base de données", "📈 Dashboard", "📅 Scheduling"])

    with tabs[0]:
        st.markdown("""
        - **Gmail API** ou **Microsoft Graph API (Outlook)** connectés en OAuth2 (accès en lecture seule sur la boîte de réception candidatures)
        - Détection automatique des nouveaux emails contenant une pièce jointe CV (filtre par mot-clé objet / dossier dédié)
        - Optionnel : webhook depuis le site carrière si celui-ci expose une API (ex: formulaire de candidature → webhook n8n)
        """)
    with tabs[1]:
        st.markdown("""
        - Choix du fournisseur selon le budget client : **Claude (Anthropic)**, **GPT (OpenAI)** ou **Gemini (Google)**
        - Prompt structuré : CV + fiche de poste → JSON (score, points forts, points faibles, justification)
        - Architecture orchestrée avec **n8n** (workflow no-code/low-code) + scripts **Python (FastAPI)** pour la logique métier
        """)
    with tabs[2]:
        st.markdown("""
        - Base de données structurée (PostgreSQL / Airtable / Google Sheets selon budget)
        - Champs extraits automatiquement : nom, ville, diplôme, années d'expérience, compétences, score, statut
        - Sert de **CVthèque réutilisable** pour de futurs postes similaires (recherche par filtres)
        """)
    with tabs[3]:
        st.markdown("""
        - Dashboard type **Streamlit / Power BI / Looker Studio** connecté en direct à la base de données
        - Filtres par poste, ville, score, statut — vue "pipeline" pour suivi RH
        - Accès web sécurisé, utilisable par toute l'équipe recrutement
        """)
    with tabs[4]:
        st.markdown("""
        - Intégration **Calendly API** : lien d'entretien envoyé automatiquement par email si score ≥ seuil défini par l'agence
        - Email de réponse automatique (personnalisé) envoyé aux candidats non retenus
        - Le recruteur garde la main : validation manuelle possible avant envoi si souhaité
        """)

# ============================================================
# PAGE 3 — DEMO SCORING
# ============================================================
elif page == "🧠 Démo — Scoring IA":
    st.markdown("## 🧠 Démo interactive — Scoring IA d'un CV")
    st.caption("Cette page simule ce que verrait le système en temps réel après réception d'un CV par email.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Fiche de poste")
        job_choice = st.selectbox("Choisir un exemple de poste", list(SAMPLE_JOBS.keys()) + ["✏️ Coller ma propre fiche de poste"])
        if job_choice == "✏️ Coller ma propre fiche de poste":
            job_desc = st.text_area("Fiche de poste", height=220, placeholder="Colle ici la description du poste...")
        else:
            job_desc = st.text_area("Fiche de poste", value=SAMPLE_JOBS[job_choice], height=220)

    with col2:
        st.markdown("#### 📄 CV du candidat")
        source = st.radio("Source du CV", ["Utiliser un exemple", "Uploader un fichier (PDF/DOCX/TXT)"], horizontal=True)
        if source == "Utiliser un exemple":
            cand_choice = st.selectbox("Choisir un exemple de candidat", list(SAMPLE_RESUMES.keys()))
            resume_text = st.text_area("Contenu du CV", value=SAMPLE_RESUMES[cand_choice], height=220)
        else:
            uploaded = st.file_uploader("Charger un CV", type=["pdf", "docx", "txt"])
            resume_text = extract_text_from_upload(uploaded) if uploaded else ""
            if resume_text:
                st.text_area("Texte extrait", value=resume_text, height=220)

    threshold = st.slider("🎯 Seuil de recommandation automatique (score minimum pour proposer un entretien)", 0, 100, 70)

    if st.button("🚀 Lancer l'analyse IA", type="primary", use_container_width=True):
        if not job_desc or not resume_text:
            st.error("Merci de fournir une fiche de poste et un CV.")
        else:
            with st.spinner("Analyse en cours..."):
                result = None
                if ai_provider != "Aucun (moteur local gratuit)" and ai_key:
                    result = try_ai_scoring(resume_text, job_desc, ai_provider, ai_key)
                if result is None:
                    result = score_resume_local(resume_text, job_desc)

            st.markdown("---")
            r1, r2 = st.columns([1, 2])
            with r1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=result["score"],
                    title={"text": "Score de pertinence"},
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

                pill_class = "pill-green" if result["score"] >= 75 else "pill-orange" if result["score"] >= 50 else "pill-red"
                st.markdown(f'<span class="pill {pill_class}">{result["verdict"]}</span>', unsafe_allow_html=True)
                st.caption(f"🔧 {result['engine']}")

            with r2:
                st.markdown("#### 💬 Justification IA")
                st.info(result["why"])
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown("**✅ Compétences en correspondance**")
                    if result.get("matched_skills"):
                        for s in result["matched_skills"]:
                            st.markdown(f"- {s}")
                    else:
                        st.caption("Aucune détectée")
                with cc2:
                    st.markdown("**⚠️ Compétences manquantes**")
                    if result.get("missing_skills"):
                        for s in result["missing_skills"]:
                            st.markdown(f"- {s}")
                    else:
                        st.caption("Aucune")

                st.markdown("#### 📌 Action automatique déclenchée")
                if result["score"] >= threshold:
                    st.success("✅ Score au-dessus du seuil → **lien Calendly envoyé automatiquement** au candidat + notification RH.")
                else:
                    st.warning("❌ Score sous le seuil → candidat **archivé dans la CVthèque** + email de réponse automatique envoyé.")

# ============================================================
# PAGE 4 — CVTHEQUE
# ============================================================
elif page == "🗂️ CVthèque & Dashboard":
    st.markdown("## 🗂️ CVthèque & Dashboard RH")
    st.caption("Base de données structurée — alimentée automatiquement par l'analyse IA de chaque nouveau CV.")

    df = load_candidates()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.markdown(f'<div class="metric-card"><div class="val">{len(df)}</div><div class="lbl">Candidats total</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="metric-card"><div class="val">{(df["Score IA"]>=75).sum()}</div><div class="lbl">Score ≥ 75</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="metric-card"><div class="val">{(df["Statut"]=="Entretien programmé").sum()}</div><div class="lbl">Entretiens programmés</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="metric-card"><div class="val">{(df["Statut"]=="Embauché").sum()}</div><div class="lbl">Embauchés</div></div>', unsafe_allow_html=True)
    k5.markdown(f'<div class="metric-card"><div class="val">{round(df["Score IA"].mean())}</div><div class="lbl">Score moyen</div></div>', unsafe_allow_html=True)

    st.markdown("")
    f1, f2, f3, f4 = st.columns(4)
    poste_f = f1.multiselect("Poste", sorted(df["Poste visé"].unique()))
    ville_f = f2.multiselect("Ville", sorted(df["Ville"].unique()))
    statut_f = f3.multiselect("Statut", sorted(df["Statut"].unique()))
    score_f = f4.slider("Score minimum", 0, 100, 0)

    filtered = df.copy()
    if poste_f: filtered = filtered[filtered["Poste visé"].isin(poste_f)]
    if ville_f: filtered = filtered[filtered["Ville"].isin(ville_f)]
    if statut_f: filtered = filtered[filtered["Statut"].isin(statut_f)]
    filtered = filtered[filtered["Score IA"] >= score_f]
    filtered = filtered.sort_values("Score IA", ascending=False)

    tab1, tab2 = st.tabs(["📋 Table des candidats", "📊 Vue analytique"])

    with tab1:
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score IA": st.column_config.ProgressColumn("Score IA", min_value=0, max_value=100, format="%d"),
            },
        )
        st.caption(f"{len(filtered)} candidat(s) affiché(s) sur {len(df)}")

        st.markdown("#### 🔍 Fiche candidat détaillée")
        pick = st.selectbox("Sélectionner un candidat", filtered["Nom"] + " — " + filtered["ID"])
        if pick:
            cid = pick.split("—")[-1].strip()
            cand = df[df["ID"] == cid].iloc[0]
            cc1, cc2, cc3 = st.columns([2, 2, 1])
            with cc1:
                st.markdown(f"**{cand['Nom']}**")
                st.caption(f"📍 {cand['Ville']} · 🎓 {cand['Diplôme']} · 💼 {cand['Expérience (ans)']} ans d'expérience")
                st.caption(f"📧 {cand['Email']} · 📨 Reçu via {cand['Source']} le {cand['Date réception']}")
            with cc2:
                pill_class = "pill-green" if cand["Score IA"] >= 75 else "pill-orange" if cand["Score IA"] >= 50 else "pill-red"
                st.markdown(f'Score IA: <span class="pill {pill_class}">{cand["Score IA"]}/100</span>', unsafe_allow_html=True)
                st.markdown(f'Statut: <span class="pill pill-blue">{cand["Statut"]}</span>', unsafe_allow_html=True)
            with cc3:
                if st.button("📅 Envoyer lien Calendly", key=f"cal_{cid}"):
                    st.success(f"Email envoyé à {cand['Email']} avec le lien de prise de RDV ✅")

    with tab2:
        g1, g2 = st.columns(2)
        with g1:
            fig1 = px.pie(df, names="Statut", title="Répartition par statut", hole=0.5,
                          color_discrete_sequence=px.colors.sequential.Purp)
            fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            fig2 = px.histogram(df, x="Score IA", nbins=15, title="Distribution des scores IA",
                                color_discrete_sequence=["#8e44ad"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig2, use_container_width=True)

        g3, g4 = st.columns(2)
        with g3:
            by_poste = df.groupby("Poste visé")["Score IA"].mean().reset_index().sort_values("Score IA")
            fig3 = px.bar(by_poste, x="Score IA", y="Poste visé", orientation="h", title="Score moyen par poste",
                         color_discrete_sequence=["#3498db"])
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig3, use_container_width=True)
        with g4:
            by_ville = df["Ville"].value_counts().reset_index()
            by_ville.columns = ["Ville", "Nombre"]
            fig4 = px.bar(by_ville, x="Ville", y="Nombre", title="Candidats par ville",
                         color_discrete_sequence=["#2ecc71"])
            fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# PAGE 5 — SCHEDULING
# ============================================================
elif page == "📅 Prise de RDV automatique":
    st.markdown("## 📅 Prise de rendez-vous automatique")
    st.caption("Dès qu'un candidat dépasse le seuil de score défini, le système propose automatiquement un créneau d'entretien.")

    df = load_candidates()
    qualified = df[df["Score IA"] >= 75].sort_values("Score IA", ascending=False)

    st.markdown(f"### 🎯 {len(qualified)} candidats qualifiés pour entretien (score ≥ 75)")

    calendly_link = st.text_input("Lien Calendly de l'agence (à configurer une seule fois)", value="https://calendly.com/votre-agence/entretien-30min")

    for _, cand in qualified.head(8).iterrows():
        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{cand['Nom']}** — {cand['Poste visé']} · {cand['Ville']}")
            c2.markdown(f'<span class="pill pill-green">{cand["Score IA"]}/100</span>', unsafe_allow_html=True)
            with c3:
                if st.button("Envoyer invitation", key=f"invite_{cand['ID']}"):
                    st.toast(f"📧 Email envoyé à {cand['Nom']} avec {calendly_link}")
            st.markdown("<hr style='margin:0.3rem 0; opacity:0.15'>", unsafe_allow_html=True)

    st.markdown("### ✉️ Aperçu de l'email automatique envoyé au candidat")
    st.markdown("""
    <div class="card">
    <b>Objet : Votre candidature a retenu notre attention 🎉</b><br><br>
    Bonjour [Prénom],<br><br>
    Nous avons bien reçu votre CV pour le poste de [Poste]. Après analyse de votre profil,
    nous souhaitons échanger avec vous lors d'un court entretien.<br><br>
    👉 Merci de choisir un créneau qui vous convient via ce lien : <i>[lien Calendly]</i><br><br>
    À très bientôt,<br>
    L'équipe recrutement
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE 6 — PRICING & TIMELINE
# ============================================================
elif page == "💰 Coût & Délais":
    st.markdown("## 💰 Coût de mise en place & délais de livraison")

    st.markdown("### 📦 Formules")
    p1, p2, p3 = st.columns(3)
    plans = [
        ("Starter", "15 000 MAD", "Connexion Gmail OU Outlook, scoring IA, CVthèque simple (Google Sheets/Airtable), dashboard Streamlit basique.", "2 semaines"),
        ("Pro", "30 000 MAD", "Gmail + Outlook + site carrière, base de données PostgreSQL, dashboard avancé, intégration Calendly automatique, emails de réponse auto.", "3 à 4 semaines"),
        ("Enterprise", "Sur devis", "Multi-agences, multi-postes, intégration ATS/CRM existant (Odoo, etc.), tableaux de bord personnalisés, support prioritaire.", "5 à 8 semaines"),
    ]
    for col, (name, price, desc, delay) in zip([p1, p2, p3], plans):
        col.markdown(f"""
        <div class="card">
        <h3>{name}</h3>
        <div style="font-size:1.6rem; font-weight:700; color:#8e44ad;">{price}</div>
        <p style="color:#9a9ab0; font-size:0.85rem;">Setup unique</p>
        <p>{desc}</p>
        <span class="pill pill-blue">⏱ {delay}</span>
        </div>
        """, unsafe_allow_html=True)

    st.caption("💡 Tarifs indicatifs à ajuster selon le marché cible (Maroc / Dubai) et la complexité réelle du besoin client.")

    st.markdown("### 📅 Timeline de déploiement type (formule Pro)")
    today = datetime.now()
    phases = [
        ("Cadrage & accès API", today, today + timedelta(days=3)),
        ("Connexion Gmail/Outlook + extraction CV", today + timedelta(days=3), today + timedelta(days=8)),
        ("Intégration moteur IA + prompt scoring", today + timedelta(days=8), today + timedelta(days=14)),
        ("Base de données + CVthèque", today + timedelta(days=14), today + timedelta(days=18)),
        ("Dashboard RH", today + timedelta(days=18), today + timedelta(days=23)),
        ("Intégration Calendly + emails auto", today + timedelta(days=23), today + timedelta(days=26)),
        ("Tests, recette client, mise en prod", today + timedelta(days=26), today + timedelta(days=30)),
    ]
    gantt_df = pd.DataFrame(phases, columns=["Phase", "Début", "Fin"])
    fig = px.timeline(gantt_df, x_start="Début", x_end="Fin", y="Phase", color="Phase",
                      color_discrete_sequence=px.colors.qualitative.Bold)
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white",
                      showlegend=False, height=380)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧮 Calculateur de coût mensuel & ROI")
    c1, c2 = st.columns(2)
    with c1:
        volume = st.slider("Nombre de CV analysés / mois", 50, 5000, 500, step=50)
        cost_per_cv = st.slider("Coût API IA par CV (MAD)", 0.05, 0.5, 0.15, step=0.01)
        hosting = st.slider("Coût hébergement / maintenance mensuel (MAD)", 0, 2000, 300, step=50)
    with c2:
        minutes_saved = st.slider("Minutes économisées par CV (tri manuel)", 1, 15, 5)
        hr_hourly_cost = st.slider("Coût horaire chargé RH (MAD)", 50, 300, 120, step=10)

    api_cost = volume * cost_per_cv
    monthly_cost = api_cost + hosting
    time_saved_hours = (volume * minutes_saved) / 60
    money_saved = time_saved_hours * hr_hourly_cost
    net_gain = money_saved - monthly_cost

    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(f'<div class="metric-card"><div class="val">{monthly_cost:,.0f} MAD</div><div class="lbl">Coût mensuel solution</div></div>', unsafe_allow_html=True)
    r2.markdown(f'<div class="metric-card"><div class="val">{time_saved_hours:,.0f} h</div><div class="lbl">Temps RH économisé/mois</div></div>', unsafe_allow_html=True)
    r3.markdown(f'<div class="metric-card"><div class="val">{money_saved:,.0f} MAD</div><div class="lbl">Valeur du temps économisé</div></div>', unsafe_allow_html=True)
    r4.markdown(f'<div class="metric-card"><div class="val" style="color:{"#2ecc71" if net_gain>0 else "#e74c3c"}">{net_gain:,.0f} MAD</div><div class="lbl">Gain net mensuel estimé</div></div>', unsafe_allow_html=True)

    st.caption("⚠️ Estimations à but commercial/pédagogique, à ajuster selon les tarifs réels des API (OpenAI/Anthropic/Google) et le contexte du client.")

st.markdown('<div class="footer-note">RecruitAI Pro — Démo commerciale générée avec Streamlit · Non connecté à des données réelles</div>', unsafe_allow_html=True)
