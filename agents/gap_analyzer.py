# agents/gap_analyzer.py — Agent Gap Analyzer (compétences manquantes + plan 30/60/90j)

import os
from dotenv import load_dotenv

load_dotenv()

# ── Base de ressources d'apprentissage par compétence ─────────
LEARNING_RESOURCES = {
    "Python":       {"niveau": "Fondamental", "durée": "30j", "ressource": "Python.org + Kaggle Learn"},
    "PyTorch":      {"niveau": "Intermédiaire", "durée": "60j", "ressource": "pytorch.org/tutorials"},
    "TensorFlow":   {"niveau": "Intermédiaire", "durée": "60j", "ressource": "tensorflow.org/tutorials"},
    "LangChain":    {"niveau": "Intermédiaire", "durée": "30j", "ressource": "python.langchain.com/docs"},
    "LangGraph":    {"niveau": "Avancé",        "durée": "30j", "ressource": "langchain-ai.github.io/langgraph"},
    "Docker":       {"niveau": "Fondamental", "durée": "30j", "ressource": "docs.docker.com/get-started"},
    "MLOps":        {"niveau": "Avancé",        "durée": "60j", "ressource": "mlops.community + DVC"},
    "Kubernetes":   {"niveau": "Avancé",        "durée": "90j", "ressource": "kubernetes.io/docs"},
    "FastAPI":      {"niveau": "Fondamental", "durée": "30j", "ressource": "fastapi.tiangolo.com"},
    "Selenium":     {"niveau": "Fondamental", "durée": "30j", "ressource": "selenium-python.readthedocs.io"},
    "Pytest":       {"niveau": "Fondamental", "durée": "30j", "ressource": "docs.pytest.org"},
    "Cypress":      {"niveau": "Intermédiaire", "durée": "30j", "ressource": "docs.cypress.io"},
    "CI/CD":        {"niveau": "Intermédiaire", "durée": "30j", "ressource": "GitHub Actions Docs"},
    "Jenkins":      {"niveau": "Intermédiaire", "durée": "30j", "ressource": "jenkins.io/doc"},
    "Hugging Face": {"niveau": "Intermédiaire", "durée": "30j", "ressource": "huggingface.co/docs"},
    "RAG":          {"niveau": "Intermédiaire", "durée": "30j", "ressource": "LangChain RAG Tutorial"},
    "ChromaDB":     {"niveau": "Fondamental", "durée": "30j", "ressource": "docs.trychroma.com"},
    "Scikit-learn": {"niveau": "Fondamental", "durée": "30j", "ressource": "scikit-learn.org/stable"},
    "Spark":        {"niveau": "Avancé",        "durée": "60j", "ressource": "spark.apache.org/docs"},
    "Kafka":        {"niveau": "Avancé",        "durée": "60j", "ressource": "kafka.apache.org/documentation"},
    "OpenCV":       {"niveau": "Intermédiaire", "durée": "30j", "ressource": "docs.opencv.org"},
    "Postman":      {"niveau": "Fondamental", "durée": "30j", "ressource": "learning.postman.com"},
    "JMeter":       {"niveau": "Intermédiaire", "durée": "30j", "ressource": "jmeter.apache.org/usermanual"},
    "BDD":          {"niveau": "Intermédiaire", "durée": "30j", "ressource": "cucumber.io/docs"},
    "Gherkin":      {"niveau": "Fondamental", "durée": "30j", "ressource": "cucumber.io/docs/gherkin"},
    "Git":          {"niveau": "Fondamental", "durée": "30j", "ressource": "git-scm.com/doc"},
    "SQL":          {"niveau": "Fondamental", "durée": "30j", "ressource": "sqlzoo.net"},
    "NLP":          {"niveau": "Intermédiaire", "durée": "60j", "ressource": "huggingface.co/learn/nlp-course"},
    "YOLO":         {"niveau": "Intermédiaire", "durée": "30j", "ressource": "docs.ultralytics.com"},
    "React":        {"niveau": "Intermédiaire", "durée": "60j", "ressource": "react.dev/learn"},
}


def gap_analyzer_node(state: dict) -> dict:
    """
    Agent Gap Analyzer — identifie les compétences manquantes
    et génère un plan d'apprentissage 30/60/90 jours.
    """
    offer    = state.get("selected_offer", {})
    cv_text  = state.get("cv_text", "")
    adapted  = state.get("adapted_cv", "")

    print(f"[GAP ANALYZER] Analyse des gaps pour : {offer.get('title', 'N/A')}")

    # Compétences requises par l'offre
    required_keywords = offer.get("ats_keywords", [])
    missing_skills    = offer.get("missing_skills", [])

    # Si missing_skills pas encore calculé par l'analyste, on le calcule
    if not missing_skills and required_keywords:
        reference_text = (cv_text + " " + adapted).lower()
        missing_skills = [
            kw for kw in required_keywords
            if kw.lower() not in reference_text
        ]

    print(f"[GAP ANALYZER] Compétences manquantes : {missing_skills}")

    # Construction du plan d'apprentissage
    plan = _build_learning_plan(missing_skills, offer)

    # Enrichissement via LLM si API disponible
    gaps_enriched = _enrich_with_llm(missing_skills, offer, cv_text) or plan

    print(f"[GAP ANALYZER] ✅ Plan généré — {len(missing_skills)} gaps identifiés")

    return {
        **state,
        "gaps": missing_skills,
        "_gap_plan": gaps_enriched,
        "messages": state.get("messages", []) + [
            {
                "role":    "gap_analyzer",
                "content": f"{len(missing_skills)} gaps identifiés : {', '.join(missing_skills)}"
            }
        ]
    }


def _build_learning_plan(missing_skills: list, offer: dict) -> list:
    """Construit un plan d'apprentissage structuré 30/60/90 jours."""
    plan = []

    for skill in missing_skills:
        resource = LEARNING_RESOURCES.get(skill, {
            "niveau":   "Intermédiaire",
            "durée":    "30j",
            "ressource": "Google + Documentation officielle"
        })

        plan.append({
            "compétence": skill,
            "niveau":     resource["niveau"],
            "durée":      resource["durée"],
            "ressource":  resource["ressource"],
            "priorité":   _get_priority(skill, offer),
        })

    # Trier par priorité (haute → moyenne → faible)
    priority_order = {"haute": 0, "moyenne": 1, "faible": 2}
    plan.sort(key=lambda x: priority_order.get(x["priorité"], 1))

    return plan


def _get_priority(skill: str, offer: dict) -> str:
    """Détermine la priorité d'une compétence selon l'offre."""
    title       = offer.get("title", "").lower()
    ats_first   = offer.get("ats_keywords", [])

    # Priorité haute : compétence principale du poste
    if ats_first and skill == ats_first[0]:
        return "haute"

    # Priorité haute : compétence dans le titre du poste
    if skill.lower() in title:
        return "haute"

    # Priorité moyenne : dans les 3 premiers mots-clés
    if skill in ats_first[:3]:
        return "moyenne"

    return "faible"


def _enrich_with_llm(missing_skills: list, offer: dict, cv_text: str) -> list | None:
    """Enrichit le plan avec des conseils personnalisés via Claude API."""
    if not missing_skills:
        return None

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
        import json

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Tu es un conseiller en développement de compétences tech.

Profil candidat (extrait CV) :
{cv_text[:500]}

Poste visé : {offer.get('title')} chez {offer.get('company')}

Compétences manquantes identifiées : {', '.join(missing_skills)}

Pour chaque compétence manquante, génère un plan d'apprentissage.
Réponds UNIQUEMENT en JSON valide, sans texte autour, avec ce format exact :
[
  {{
    "compétence": "nom",
    "niveau": "Fondamental|Intermédiaire|Avancé",
    "durée": "30j|60j|90j",
    "ressource": "lien ou nom de ressource",
    "conseil": "conseil personnalisé court (max 15 mots)",
    "priorité": "haute|moyenne|faible"
  }}
]"""

        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.strip()
        # Nettoyer les éventuels backticks markdown
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)

    except Exception as e:
        print(f"[GAP ANALYZER] ⚠️  LLM enrichment échoué: {e} — fallback local")
        return None