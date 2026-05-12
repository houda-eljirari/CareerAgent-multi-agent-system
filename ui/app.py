# ui/app.py — Interface Streamlit CareerAgent
import streamlit as st
import sys
import os
import pdfplumber
import io

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph import app, AgentState

# ── Configuration de la page ──────────────────────────────────
st.set_page_config(
    page_title="CareerAgent",
    page_icon="🚀",
    layout="wide"
)

# ── CSS personnalisé ──────────────────────────────────────────
st.markdown("""
<style>
.agent-card {
    background: #f0f4ff;
    border-left: 4px solid #2E75B6;
    padding: 10px 15px;
    margin: 5px 0;
    border-radius: 4px;
}
.score-high  { color: #1A7A3A; font-weight: bold; }
.score-mid   { color: #854F0B; font-weight: bold; }
.score-low   { color: #C0392B; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Initialisation du session state ──────────────────────────
if "stage" not in st.session_state:
    st.session_state.stage = "input"
if "result" not in st.session_state:
    st.session_state.result = None
if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": "streamlit-1"}}
if "selected_offer" not in st.session_state:
    st.session_state.selected_offer = None

# ── HEADER ────────────────────────────────────────────────────
st.title("🚀 CareerAgent")
st.caption("Système Multi-Agent Intelligent — Trouve ton stage, adapte ton CV, prépare ton entretien.")
st.divider()

# ── Fonction extraction PDF ───────────────────────────────────
def extract_text_from_pdf(uploaded_file) -> str:
    """Extrait le texte d'un fichier PDF uploadé via pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF : {e}")
        return ""
    return text.strip()

# ══════════════════════════════════════════════════════════════
# ÉTAPE 1 : Input CV + Domaine
# ══════════════════════════════════════════════════════════════
if st.session_state.stage == "input":
    st.header("📄 Étape 1 — Ton profil")

    col1, col2 = st.columns([2, 1])

    with col1:
        # ── Upload PDF ────────────────────────────────────────
        st.markdown("**📎 Upload ton CV (PDF)**")
        uploaded_cv = st.file_uploader(
            "Glisse ton CV ici ou clique pour choisir",
            type=["pdf"],
            label_visibility="collapsed"
        )

        # Extraction automatique si PDF uploadé
        cv_text = ""
        if uploaded_cv is not None:
            cv_text = extract_text_from_pdf(uploaded_cv)
            if cv_text:
                st.success(f"✅ CV extrait — {len(cv_text)} caractères détectés")
                with st.expander("👁️ Aperçu du CV extrait"):
                    st.text(cv_text[:800] + ("..." if len(cv_text) > 800 else ""))

        # ── Ou saisie manuelle ────────────────────────────────
        st.markdown("**✏️ Ou colle ton CV manuellement**")
        cv_manual = st.text_area(
            "Texte du CV",
            height=150,
            placeholder="Ex: Master IA, compétences Python, LangChain, Git, Docker...",
            label_visibility="collapsed"
        )

        # Priorité au PDF, fallback sur le texte manuel
        if cv_manual:
            cv_text = cv_manual

    with col2:
        domain = st.selectbox(
            "Domaine cible",
            ["Intelligence Artificielle", "Testing / QA",
             "Backend / DevOps", "Data Science", "Full Stack"]
        )
        user_query = st.text_input(
            "Ta requête",
            value="Je cherche un stage en IA"
        )

        # Infos sur le CV chargé
        if cv_text:
            st.info(f"📄 CV prêt\n{len(cv_text)} caractères")
        else:
            st.warning("⚠️ Aucun CV chargé")

    if st.button("🔍 Lancer la recherche", type="primary", use_container_width=True):
        if not cv_text:
            st.error("Upload ton CV en PDF ou colle son contenu avant de continuer !")
        else:
            with st.spinner("🤖 Les agents travaillent..."):
                state = {
                    "cv_text":             cv_text,
                    "user_query":          user_query,
                    "target_domain":       domain,
                    "job_offers":          [],
                    "ranked_offers":       [],
                    "selected_offer":      {},
                    "adapted_cv":          "",
                    "gaps":                [],
                    "interview_questions": [],
                    "next_agent":          "",
                    "human_validated":     False,
                    "human_feedback":      "",
                    "qa_passed":           False,
                    "messages":            [],
                }
                result = app.invoke(state, st.session_state.config)
                st.session_state.result = result
                st.session_state.stage  = "offers"
                st.rerun()

# ══════════════════════════════════════════════════════════════
# ÉTAPE 2 : Affichage des offres classées
# ══════════════════════════════════════════════════════════════
elif st.session_state.stage == "offers":
    st.header("📊 Étape 2 — Offres classées")

    result        = st.session_state.result
    ranked_offers = result.get("ranked_offers", [])

    if not ranked_offers:
        st.warning("Aucune offre trouvée.")
    else:
        st.success(f"✅ {len(ranked_offers)} offres analysées et classées !")

        for i, offer in enumerate(ranked_offers):
            score     = offer.get("score", 0)
            fit_level = offer.get("fit_level", "?")
            color     = "score-high" if score >= 70 else ("score-mid" if score >= 40 else "score-low")

            with st.expander(f"#{i+1} — {offer['title']} chez {offer['company']} | Score : {score}/100"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Entreprise :** {offer.get('company')}")
                    st.markdown(f"**Localisation :** {offer.get('location', 'N/A')}")
                    st.markdown(f"**Niveau de fit :** `{fit_level}`")
                with col2:
                    st.markdown(f"**✅ Compétences matchées :** {', '.join(offer.get('matched_skills', []))}")
                    st.markdown(f"**❌ Compétences manquantes :** {', '.join(offer.get('missing_skills', []))}")

                if st.button(f"Choisir cette offre", key=f"offer_{i}"):
                    st.session_state.selected_offer = offer
                    st.session_state.stage = "cv_adapt"
                    st.session_state.config = {"configurable": {"thread_id": "streamlit-2"}}
                    st.rerun()

    if st.button("⬅️ Recommencer"):
        st.session_state.stage = "input"
        st.rerun()

# ══════════════════════════════════════════════════════════════
# ÉTAPE 3 : Adaptation CV + QA
# ══════════════════════════════════════════════════════════════
elif st.session_state.stage == "cv_adapt":
    st.header("✏️ Étape 3 — Adaptation du CV")

    offer = st.session_state.selected_offer
    st.info(f"Offre sélectionnée : **{offer['title']}** chez **{offer['company']}**")

    with st.spinner("🤖 Agent CV Adapter + Agent QA en cours..."):
        state2 = {
            **st.session_state.result,
            "user_query":      "Je veux adapter mon cv",
            "selected_offer":  offer,
            "adapted_cv":      "",
            "human_validated": False,
            "qa_passed":       False,
            "messages":        [],
        }
        result2 = app.invoke(state2, st.session_state.config)
        st.session_state.result = result2
        st.session_state.stage  = "validation"
        st.rerun()

# ══════════════════════════════════════════════════════════════
# ÉTAPE 4 : Human-in-the-Loop
# ══════════════════════════════════════════════════════════════
elif st.session_state.stage == "validation":
    st.header("⚠️ Étape 4 — Validation Humaine")
    st.warning("Le système attend ta validation avant de continuer.")

    result = st.session_state.result

    # Rapport QA
    qa_report = result.get("_qa_report", {})
    if qa_report:
        st.subheader("🔬 Rapport QA")
        cols = st.columns(5)
        for i, test in enumerate(qa_report.get("tests", [])):
            with cols[i]:
                icon = "✅" if test["passed"] else "❌"
                st.metric(
                    label=test["name"][:15],
                    value=f"{test['score']}/100",
                    delta=icon
                )
        st.markdown(f"**Score global : {qa_report.get('overall_score')}/100**")

    # CV adapté
    st.subheader("📄 CV Adapté")
    adapted_cv = result.get("adapted_cv", "")
    st.text_area("CV adapté par l'agent", value=adapted_cv, height=200)

    # Boutons de validation
    st.subheader("Ta décision")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Valider ce CV", type="primary", use_container_width=True):
            app.update_state(st.session_state.config, {"human_validated": True})
            st.session_state.stage = "results"
            st.rerun()

    with col2:
        feedback = st.text_input("Ton feedback (optionnel)")
        if st.button("❌ Refuser et corriger", use_container_width=True):
            app.update_state(st.session_state.config, {
                "human_validated": False,
                "human_feedback":  feedback
            })
            st.session_state.stage = "cv_adapt"
            st.rerun()

# ══════════════════════════════════════════════════════════════
# ÉTAPE 5 : Résultats finaux
# ══════════════════════════════════════════════════════════════
elif st.session_state.stage == "results":
    st.header("🎉 Étape 5 — Résultats Finaux")

    with st.spinner("🤖 Gap Analyzer + Entretien Prep en cours..."):
        result3 = app.invoke(None, st.session_state.config)
        st.session_state.result = result3

    # Gaps
    st.subheader("📈 Compétences à développer")
    gaps = result3.get("gaps", [])
    if gaps:
        cols = st.columns(len(gaps))
        for i, gap in enumerate(gaps):
            with cols[i]:
                st.error(f"❌ {gap}")
    else:
        st.success("Aucun gap majeur détecté !")

    # Plan d'apprentissage
    gap_plan = result3.get("_gap_plan", [])
    if gap_plan:
        st.subheader("📚 Plan d'apprentissage")
        for item in gap_plan:
            with st.expander(f"[{item.get('priorité','?').upper()}] {item.get('compétence')} — {item.get('durée')}"):
                st.markdown(f"**Niveau :** {item.get('niveau')}")
                st.markdown(f"**Ressource :** {item.get('ressource')}")
                if item.get('conseil'):
                    st.info(item.get('conseil'))

    # Questions d'entretien
    st.subheader("🎤 Questions d'entretien")
    questions = result3.get("interview_questions", [])
    for q in questions:
        with st.expander(f"[{q.get('type','?').upper()}] {q.get('question','?')}"):
            st.info(f"💡 Conseil : {q.get('conseil', 'Prépare une réponse structurée avec des exemples concrets.')}")

    # CV à télécharger
    st.subheader("📥 Télécharger le CV adapté")
    adapted_cv = result3.get("adapted_cv", "")
    st.download_button(
        label="📄 Télécharger CV adapté (.txt)",
        data=adapted_cv,
        file_name="cv_adapte.txt",
        mime="text/plain"
    )

    # Historique agents
    with st.expander("💬 Historique des agents"):
        for m in result3.get("messages", []):
            st.markdown(f"**[{m['role']}]** {m['content']}")

    if st.button("🔄 Nouvelle recherche", type="primary"):
        st.session_state.stage  = "input"
        st.session_state.result = None
        st.session_state.config = {"configurable": {"thread_id": "streamlit-new"}}
        st.rerun()