"""
GTM Flow AI — Démo d'automatisation B2B (Apollo + LeadRocks + SMTP)
Développé pour démo n8n + Apollo API + LeadRocks + SMTP
Auteur: Anas — AI Automation Engineer
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="GTM Flow AI — Automatisation Prospection B2B",
    page_icon="🚀",
    layout="wide",
)

# ============================================================
# STYLE (Dark Premium)
# ============================================================
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        color: white;
    }
    .card {
        background: #161824;
        border: 1px solid #2a2d40;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #1c1f2e;
        border: 1px solid #34384c;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
    .status-badge {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MOCK DATA: PROSPECTING PIPELINE
# ============================================================
@st.cache_data
def load_gtm_data(n=40):
    industries = ["SaaS", "Fintech", "Logistique", "E-commerce", "IA & Data"]
    job_titles = ["CEO", "Marketing Manager", "CTO", "Head of Sales", "Operations Director"]
    enrichment_status = ["✅ Enrichi (LeadRocks)", "🟡 En attente", "❌ Email Introuvable"]
    outcomes = ["Email Envoyé", "Ouvert", "Répondu", "RDV Fixé", "Bounce"]
    
    data = []
    for i in range(n):
        data.append({
            "Prospect": f"Contact_{i+100}",
            "Entreprise": f"Company {random.choice(['Alpha', 'Beta', 'Tech', 'Global'])} {i}",
            "Poste": random.choice(job_titles),
            "Secteur": random.choice(industries),
            "Source": "Apollo.io",
            "Statut Data": random.choice(enrichment_status),
            "Séquence SMTP": random.choice(outcomes),
            "Score Lead": random.randint(50, 100),
            "Dernière Action": (datetime.now() - timedelta(days=random.randint(0, 5))).strftime("%d/%m/%Y")
        })
    return pd.DataFrame(data)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🚀 GTM Flow AI")
st.sidebar.caption("n8n + Apollo + LeadRocks + SMTP")

menu = st.sidebar.radio("Menu", [
    "🏠 Stratégie GTM",
    "⚙️ Pipeline n8n",
    "🔍 Recherche & Enrichissement",
    "📊 Tracking Campagnes",
    "💰 Calculateur ROI"
])

st.sidebar.markdown("---")
st.sidebar.info("Cette architecture automatise la prospection B2B du sourcing à l'envoi d'emails.")

# ============================================================
# PAGE 1: STRATÉGIE GTM
# ============================================================
if menu == "🏠 Stratégie GTM":
    st.markdown('<div class="hero"><h1>GTM & Outbound Automation</h1><p>Générez des opportunités qualifiées en pilotant votre stack de prospection via n8n.</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Prospects Extraits", "2,840", "Apollo")
    col2.metric("Taux d'enrichissement", "82%", "LeadRocks")
    col3.metric("Emails Envoyés", "1,120", "SMTP")
    col4.metric("Meetings Booked", "14", "+3 cette semaine")

    st.markdown("### 🛠 La Stack Technologique B2B")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.image("https://assets.apollo.io/logo/apollo-logo-m.png", width=60) # Simulé
        st.markdown("**Apollo.io API**")
        st.caption("Sourcing ciblé par filtres (Poste, CA, Effectif).")
    with c2:
        st.image("https://leadrocks.io/assets/images/logo.png", width=120) # Simulé
        st.markdown("**LeadRocks**")
        st.caption("Enrichissement des emails pro et personnels manquants.")
    with c3:
        st.image("https://n8n.io/images/og-image.png", width=80) 
        st.markdown("**n8n Orchestrator**")
        st.caption("Le moteur qui lie les outils et nettoie les données.")
    with c4:
        st.image("https://cdn-icons-png.flaticon.com/512/281/281769.png", width=50)
        st.markdown("**SMTP / Gmail / Outlook**")
        st.caption("Envoi des séquences personnalisées via API.")

# ============================================================
# PAGE 2: n8n PIPELINE (GTM)
# ============================================================
elif menu == "⚙️ Pipeline n8n":
    st.markdown("## ⚙️ Workflow n8n (Le Moteur de Prospection)")
    
    dot = """
    digraph G {
        rankdir=LR;
        bgcolor="transparent";
        node [fontname="Helvetica" shape=box style=filled color="#2a2d40" fontcolor=white];
        
        Cron [label="⏰ Trigger: Hebdomadaire" fillcolor="#ff6d5a"];
        Apollo [label="🔍 Apollo Search API\\n(ICP Targeting)" fillcolor="#1e3a8a"];
        LeadRocks [label="💎 LeadRocks\\n(Email Enrichment)" fillcolor="#2ecc71"];
        Filter [label="🛡️ Email Verifier\\n(ZeroBounce/Debounce)"];
        AI [label="✍️ GPT-4 Personalizer\\n(Ice-breaker)" fillcolor="#a200ff"];
        SMTP [label="✉️ SMTP Outbound\\n(Séquence)" fillcolor="#3b82f6"];
        CRM [label="📈 Pipedrive / Hubspot" fillcolor="#f39c12"];
        
        Cron -> Apollo;
        Apollo -> LeadRocks;
        LeadRocks -> Filter;
        Filter -> AI;
        AI -> SMTP;
        SMTP -> CRM [label="If Reply"];
    }
    """
    st.graphviz_chart(dot)
    
    with st.expander("Détails du processus automatisé"):
        st.markdown("""
        1. **Extraction (Apollo)** : On récupère 500 prospects par semaine répondant à l'ICP.
        2. **Enrichissement (LeadRocks)** : Si Apollo n'a pas l'email direct, LeadRocks prend le relais.
        3. **Nettoyage** : Filtrage des emails génériques (info@, contact@) et vérification de validité.
        4. **Personnalisation** : n8n envoie le profil LinkedIn du prospect à OpenAI pour générer une ligne d'intro unique.
        5. **Envoi (SMTP)** : L'email part via votre serveur SMTP avec un tracking d'ouverture.
        """)

# ============================================================
# PAGE 3: RECHERCHE & ENRICHISSEMENT
# ============================================================
elif menu == "🔍 Recherche & Enrichissement":
    st.markdown("## 🔍 Simulateur de Sourcing")
    
    col_in, col_out = st.columns([1, 2])
    
    with col_in:
        st.markdown("#### Filtres Apollo")
        target_title = st.text_input("Titre du poste", "Directeur Marketing")
        target_ind = st.selectbox("Secteur", ["SaaS", "Immobilier", "Santé", "E-commerce"])
        min_rev = st.slider("CA Minimum ($M)", 1, 100, 10)
        
        if st.button("Lancer l'extraction"):
            st.session_state.searching = True
            
    with col_out:
        st.markdown("#### Résultat de l'enrichissement en temps réel")
        if 'searching' in st.session_state:
            with st.status("Appels API en cours...", expanded=True) as status:
                st.write("Connexion à Apollo API...")
                st.write("Extraction de 10 prospects...")
                st.write("Vérification sur LeadRocks...")
                status.update(label="Extraction terminée !", state="complete", expanded=False)
            
            # Simulate result
            res = pd.DataFrame({
                "Nom": ["Alice Martin", "Bob Durand", "Charlie Zen"],
                "Email": ["a.martin@company.com", "b.durand@lead.io", "cz@startup.fr"],
                "Confidence": ["98%", "85%", "92%"],
                "Source": ["Apollo", "LeadRocks", "LeadRocks"]
            })
            st.table(res)
            st.success("Données poussées vers le pipeline SMTP.")
        else:
            st.info("Configurez vos filtres et lancez la recherche.")

# ============================================================
# PAGE 4: TRACKING CAMPAGNES
# ============================================================
elif menu == "📊 Tracking Campagnes":
    st.markdown("## 📊 Performance Outbound")
    
    df = load_gtm_data()
    
    # Filtres
    secteurs = st.multiselect("Filtrer par Secteur", df["Secteur"].unique(), default=df["Secteur"].unique())
    df_filtered = df[df["Secteur"].isin(secteurs)]
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    c1.metric("Taux d'ouverture", "54%", "+5%")
    c2.metric("Taux de réponse", "8.2%", "+1.5%")
    c3.metric("Bounces", "1.2%", "-0.5%")
    
    st.markdown("### Liste des prospects en cours de séquence")
    st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    
    # Graphique
    st.markdown("### Performance par canal / étape")
    fig = px.funnel(df_filtered, x="Score Lead", y="Séquence SMTP", color="Secteur")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 5: ROI CALCULATOR
# ============================================================
elif menu == "💰 Calculateur ROI":
    st.markdown("## 💰 Économie & Rentabilité")
    
    with st.container():
        st.markdown("""
        <div class="card">
        <h3>Modèle d'Automatisation GTM</h3>
        <p>Remplacez le travail manuel de sourcing et d'envoi par un flux 24/7.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_roi1, col_roi2 = st.columns(2)
        
        with col_roi1:
            hours_manual = st.number_input("Heures manuelles / semaine (sourcing + emails)", 5, 40, 15)
            cost_per_hour = st.number_input("Coût horaire (MAD)", 100, 1000, 300)
            
            manual_total = hours_manual * cost_per_hour * 4
            st.error(f"Coût manuel : {manual_total:,.0f} MAD / mois")
            
        with col_roi2:
            st.markdown("#### Coûts Stack Automation")
            st.write("- n8n Cloud: ~200 MAD/m")
            st.write("- Apollo/LeadRocks Credits: ~800 MAD/m")
            st.write("- Maintenance: 1500 MAD/m")
            
            auto_total = 2500
            st.success(f"Coût Automatisé : {auto_total:,.0f} MAD / mois")
            
        st.divider()
        st.info(f"🚀 **Économie mensuelle estimée : {manual_total - auto_total:,.0f} MAD**")

st.markdown('<div style="text-align:center; color:gray; font-size: 0.8rem; margin-top: 50px;">GTM Flow AI — Architecture n8n + Apollo + LeadRocks</div>', unsafe_allow_html=True)
