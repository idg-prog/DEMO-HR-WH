"""
SocialFlow AI — Démo d'automatisation Lead Gen (WhatsApp / FB / IG)
Développé pour démo n8n + Meta API + Voiceflow
Auteur: Anas — AI Automation Engineer
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="SocialFlow AI — Automatisation Meta & Voiceflow",
    page_icon="💬",
    layout="wide",
)

# ============================================================
# STYLE (Dark Premium)
# ============================================================
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .hero {
        background: linear-gradient(135deg, #0084ff 0%, #a200ff 100%);
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
    .pill {
        padding: 0.2rem 0.6rem;
        border-radius: 10px;
        font-size: 0.8rem;
    }
    .pill-wa { background: #25D366; color: black; }
    .pill-ig { background: #E1306C; color: white; }
    .pill-fb { background: #4267B2; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MOCK DATA: LEADS FROM SOCIAL MEDIA
# ============================================================
@st.cache_data
def load_leads(n=30):
    channels = ["WhatsApp", "Instagram", "Facebook Messenger"]
    intents = ["Achat immédiat", "Demande de prix", "Support technique", "Prise de RDV"]
    status = ["Nouveau", "Qualifié (IA)", "Transféré au CRM", "Vente conclue"]
    
    data = []
    for i in range(n):
        channel = random.choice(channels)
        data.append({
            "Lead ID": f"LX-{5000+i}",
            "Client": f"User_{random.randint(100,999)}",
            "Canal": channel,
            "Dernier Message": random.choice(["Je veux commander", "C'est quoi le prix ?", "Est-ce dispo ?", "Je cherche un expert"]),
            "Score Intention (Voiceflow)": random.randint(40, 99),
            "Statut": random.choice(status),
            "Date": (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime("%H:%M - %d/%m"),
        })
    return pd.DataFrame(data)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🚀 SocialFlow AI")
st.sidebar.caption("n8n + Meta + Voiceflow Orchestration")

menu = st.sidebar.radio("Menu", [
    "🏠 Vue d'ensemble",
    "⚙️ Pipeline n8n",
    "🧠 Intelligence Voiceflow",
    "📊 Dashboard Leads",
    "💰 ROI & Setup"
])

st.sidebar.markdown("---")
st.sidebar.info("Cette démo montre comment automatiser vos messages Meta via n8n et Voiceflow.")

# ============================================================
# PAGE 1: OVERVIEW
# ============================================================
if menu == "🏠 Vue d'ensemble":
    st.markdown('<div class="hero"><h1>Omni-channel AI Automation</h1><p>Gérez vos conversations WhatsApp, Instagram et Facebook Messenger à l\'échelle avec une IA conversationnelle avancée.</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Messages traitées / mois", "12,450", "+15%")
    col2.metric("Taux de réponse auto", "94%", "+2%")
    col3.metric("Leads qualifiés via IA", "842", "+22%")

    st.markdown("### 🛠 La Stack Technologique")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/WhatsApp.svg/1200px-WhatsApp.svg.png", width=50)
        st.markdown("**Meta API**")
        st.caption("Réception des Webhooks (WA Business, IG DM, FB Messenger).")
    with c2:
        st.image("https://n8n.io/images/og-image.png", width=100) # Simulé
        st.markdown("**n8n Orchestrator**")
        st.caption("Route les messages, extrait les données et connecte le CRM.")
    with c3:
        st.image("https://mintlify.s3-us-west-1.amazonaws.com/voiceflow/logo/light.png", width=120)
        st.markdown("**Voiceflow (LLM)**")
        st.caption("L'agent intelligent qui gère la conversation et qualifie le lead.")

# ============================================================
# PAGE 2: n8n PIPELINE
# ============================================================
elif menu == "⚙️ Pipeline n8n":
    st.markdown("## ⚙️ Workflow n8n (Le Cerveau)")
    st.write("Visualisation du flux automatisé entre Meta et votre CRM.")

    dot = """
    digraph G {
        rankdir=LR;
        bgcolor="transparent";
        node [fontname="Helvetica" shape=box style=filled color="#2a2d40" fontcolor=white];
        
        Meta [label="📱 Meta Webhook\\n(WA/IG/FB)" fillcolor="#0084ff"];
        n8n [label="⚡ n8n.io\\n(Trigger)" fillcolor="#ff6d5a"];
        VF [label="🧠 Voiceflow API\\n(Traitement IA)" fillcolor="#a200ff"];
        Router [label="⚖️ Router\\n(Check Intent)"];
        CRM [label="🗄️ Google Sheets / Airtable" fillcolor="#2ecc71"];
        Alert [label="🔔 Slack / Email Notification" fillcolor="#f39c12"];
        
        Meta -> n8n;
        n8n -> VF;
        VF -> Router;
        Router -> CRM [label="Lead Qualifié"];
        Router -> Alert [label="Urgence Client"];
        CRM -> Meta [label="Réponse Auto"];
    }
    """
    st.graphviz_chart(dot)
    
    with st.expander("Comment ça marche techniquement ?"):
        st.markdown("""
        1. **Webhook Meta** : n8n écoute les nouveaux messages en temps réel.
        2. **Identification** : n8n vérifie si le client existe déjà dans votre base.
        3. **Dialogue Voiceflow** : Le message est envoyé à Voiceflow (via Knowledge Base + GPT-4).
        4. **Extraction** : Voiceflow renvoie le nom, l'email et l'intention du client.
        5. **Action** : n8n met à jour le CRM et répond instantanément sur le bon canal.
        """)

# ============================================================
# PAGE 3: VOICEFLOW SIMULATION
# ============================================================
elif menu == "🧠 Intelligence Voiceflow":
    st.markdown("## 🧠 Simulation Voiceflow AI")
    st.caption("Testez comment l'IA analyse et qualifie une demande client social media.")

    col_sim1, col_sim2 = st.columns([1, 1])
    
    with col_sim1:
        st.markdown("#### 💬 Message entrant")
        user_msg = st.text_area("Simuler un message client (ex: 'Salut, je veux commander le pack premium à 50€')", height=150)
        canal = st.selectbox("Canal source", ["WhatsApp", "Instagram DM", "Facebook"])
        
        if st.button("Lancer l'analyse IA"):
            with st.spinner("Voiceflow analyse le message..."):
                # Simulation de retour API Voiceflow
                st.session_state.vf_result = {
                    "intent": "Achat / Commande" if "prix" in user_msg or "commander" in user_msg else "Information",
                    "sentiment": "Positif",
                    "entities": ["Pack Premium", "50€"],
                    "confidence": 98
                }
    
    with col_sim2:
        st.markdown("#### 🛠 Extraction JSON (vers n8n)")
        if 'vf_result' in st.session_state:
            st.json(st.session_state.vf_result)
            st.success(f"Action n8n : Créer un ticket dans le CRM avec score {st.session_state.vf_result['confidence']}%")
        else:
            st.info("Entrez un message pour voir l'extraction de données.")

# ============================================================
# PAGE 4: DASHBOARD LEADS
# ============================================================
elif menu == "📊 Dashboard Leads":
    st.markdown("## 📊 Monitoring des Leads Social Media")
    
    df = load_leads()
    
    # Filtres
    f1, f2 = st.columns(2)
    canal_filter = f1.multiselect("Filtrer par Canal", df["Canal"].unique(), default=df["Canal"].unique())
    intent_filter = f2.slider("Score IA Minimum", 0, 100, 50)
    
    filtered_df = df[(df["Canal"].isin(canal_filter)) & (df["Score Intention (Voiceflow)"] >= intent_filter)]

    # Table
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    # Chart
    st.markdown("### Répartition des messages par canal")
    fig = px.bar(filtered_df, x="Canal", color="Canal", title="Volume de leads détectés")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 5: ROI & PRICING
# ============================================================
elif menu == "💰 ROI & Setup":
    st.markdown("## 💰 Investissement & Rentabilité")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card">
        <h3>Pack Automation Pro</h3>
        <ul>
            <li>Setup n8n (Auto-hébergé ou Cloud)</li>
            <li>Design Agent Voiceflow (Multi-langue)</li>
            <li>Intégration API Meta (WA/IG/FB)</li>
            <li>Dashboard Leads temps réel</li>
        </ul>
        <hr>
        <b>Prix estimé : 25 000 MAD / setup unique</b>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        volume = st.slider("Volume messages mensuel", 100, 10000, 1000)
        saved_time = (volume * 3) / 60 # 3 min par message
        st.metric("Temps gagné / mois", f"{saved_time:.0f} Heures")
        st.info("L'IA traite 90% des demandes répétitives sans intervention humaine.")

st.markdown('<div style="text-align:center; color:gray; font-size: 0.8rem; margin-top: 50px;">SocialFlow AI — Démo technique Meta + n8n + Voiceflow</div>', unsafe_allow_html=True)
