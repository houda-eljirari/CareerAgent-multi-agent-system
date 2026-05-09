# agents/analyste.py — Agent Analyste avec RAG Agentique itératif
from rag.vector_store import get_retriever

def analyste_node(state: dict) -> dict:
    """
    RAG Agentique : 2 requêtes successives par offre.
    Requête 1 → compétences spécifiques au poste
    Requête 2 → tendances marché basées sur les résultats de R1
    """
    offers  = state.get("job_offers", [])
    cv_text = state.get("cv_text", "")

    if not offers:
        print("[ANALYSTE] Aucune offre à analyser")
        return {**state, "ranked_offers": []}

    retriever = get_retriever(k=2)
    print(f"[ANALYSTE] Analyse RAG itérative de {len(offers)} offres...")

    ranked = []
    for offer in offers:
        title   = offer.get("title", "")
        company = offer.get("company", "")

        # ── Requête RAG 1 : compétences du poste ──────────────
        query1 = f"compétences requises {title} {company}"
        docs1  = retriever(query1)
        context1 = " ".join([d["page_content"][:200] for d in docs1])
        print(f"  [RAG R1] '{query1[:40]}...' → {len(docs1)} docs")

        # ── Requête RAG 2 : marché basée sur R1 ───────────────
        # On extrait les 3 premiers mots-clés trouvés dans R1
        keywords = _extract_keywords(context1)
        query2   = f"marché emploi {' '.join(keywords)}"
        docs2    = retriever(query2)
        context2 = " ".join([d["page_content"][:200] for d in docs2])
        print(f"  [RAG R2] '{query2[:40]}...' → {len(docs2)} docs")

        # ── Calcul du score basé sur le contexte RAG ──────────
        score, matched, missing = _calculate_score(cv_text, context1 + context2)

        scored_offer = {
            **offer,
            "score":          score,
            "ats_keywords":   keywords,
            "matched_skills": matched,
            "missing_skills": missing,
            "fit_level":      _fit_level(score),
            "rag_context":    context1[:300],
        }
        ranked.append(scored_offer)
        print(f"  → {title} : {score}/100 ({_fit_level(score)})")

    # Tri par score décroissant
    ranked.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n[ANALYSTE] 🏆 Top offre : {ranked[0]['title']} — {ranked[0]['score']}/100")

    return {
        **state,
        "ranked_offers": ranked,
        "next_agent":    "supervisor",
        "messages": state.get("messages", []) + [
            {"role": "analyste",
             "content": f"Top offre : {ranked[0]['title']} ({ranked[0]['score']}/100)"}
        ]
    }

# ── Fonctions utilitaires ──────────────────────────────────────

def _extract_keywords(context: str) -> list:
    """Extrait les mots-clés techniques du contexte RAG."""
    tech_keywords = [
        "Python", "PyTorch", "TensorFlow", "Scikit-learn", "LangChain",
        "LangGraph", "Docker", "Git", "FastAPI", "MLOps", "RAG",
        "Selenium", "Pytest", "Cypress", "CI/CD", "Jenkins", "API"
    ]
    found = [kw for kw in tech_keywords if kw.lower() in context.lower()]
    return found[:5] if found else ["Python", "ML", "Git"]

def _calculate_score(cv_text: str, context: str) -> tuple:
    """Calcule le score de compatibilité CV ↔ offre."""
    keywords = _extract_keywords(context)
    matched  = [kw for kw in keywords if kw.lower() in cv_text.lower()]
    missing  = [kw for kw in keywords if kw.lower() not in cv_text.lower()]

    # Score = % de mots-clés présents dans le CV
    if not keywords:
        return 50, [], []

    base_score = int((len(matched) / len(keywords)) * 100)
    # Bonus si le CV est riche
    if len(cv_text) > 200:
        base_score = min(base_score + 10, 100)

    return base_score, matched, missing

def _fit_level(score: int) -> str:
    if score >= 80: return "Excellent"
    if score >= 60: return "Bon"
    if score >= 40: return "Moyen"
    return "Faible"
