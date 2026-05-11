# agents/entretien.py — Agent Entretien Prep (5 questions ciblées)

import os
from dotenv import load_dotenv

load_dotenv()

# ── Banque de questions par type ───────────────────────────────
QUESTIONS_TECHNIQUES = {
    "Python":       "Comment gères-tu les exceptions en Python et quand utilises-tu un context manager ?",
    "PyTorch":      "Explique la différence entre .detach() et .no_grad() dans PyTorch.",
    "TensorFlow":   "Quelle est la différence entre un modèle Sequential et Functional API dans TensorFlow ?",
    "LangChain":    "Comment implémentes-tu une chaîne RAG avec LangChain ? Décris les étapes.",
    "LangGraph":    "Explique le concept de StateGraph dans LangGraph et comment tu gères les checkpoints.",
    "Docker":       "Quelle est la différence entre une image Docker et un conteneur ? Comment optimises-tu une image ?",
    "MLOps":        "Décris un pipeline MLOps complet du training au déploiement en production.",
    "Kubernetes":   "Explique la différence entre un Deployment et un StatefulSet dans Kubernetes.",
    "FastAPI":      "Comment implémentes-tu l'authentification JWT dans une API FastAPI ?",
    "Selenium":     "Comment gères-tu les éléments dynamiques (chargés en AJAX) avec Selenium ?",
    "Pytest":       "Explique les fixtures Pytest et comment tu organises tes tests en conftest.py.",
    "Cypress":      "Quelle est la différence entre cy.get() et cy.find() dans Cypress ?",
    "CI/CD":        "Décris un pipeline GitHub Actions complet pour un projet Python avec tests et déploiement.",
    "RAG":          "Explique le processus de chunking et son impact sur la qualité d'un système RAG.",
    "ChromaDB":     "Comment gères-tu les embeddings et la similarité cosine dans ChromaDB ?",
    "Scikit-learn": "Explique la différence entre fit(), transform() et fit_transform() dans Scikit-learn.",
    "Git":          "Décris ta stratégie de branching Git dans un projet en équipe.",
    "SQL":          "Quelle est la différence entre INNER JOIN et LEFT JOIN ? Donne un exemple concret.",
    "NLP":          "Explique la tokenisation BPE (Byte Pair Encoding) et pourquoi elle est utilisée dans les LLMs.",
    "Hugging Face": "Comment fine-tunes-tu un modèle pré-entraîné Hugging Face sur un dataset custom ?",
    "OpenCV":       "Comment détectes-tu des contours dans une image avec OpenCV ? Cite les fonctions clés.",
    "JMeter":       "Comment paramètres-tu un test de charge avec JMeter pour simuler 1000 utilisateurs ?",
    "BDD":          "Explique le cycle Given-When-Then en BDD avec un exemple concret.",
    "Postman":      "Comment utilises-tu les variables d'environnement Postman dans une collection de tests ?",
}

QUESTIONS_COMPORTEMENTALES = [
    {
        "question": "Décris une situation où tu as dû apprendre une nouvelle technologie rapidement pour un projet.",
        "conseil":  "Utilise la méthode STAR : Situation, Tâche, Action, Résultat."
    },
    {
        "question": "Comment gères-tu les désaccords techniques avec un collègue ou un supérieur ?",
        "conseil":  "Montre ta capacité d'écoute et de compromis constructif."
    },
    {
        "question": "Parle-moi d'un projet qui n'a pas fonctionné comme prévu. Qu'as-tu appris ?",
        "conseil":  "Sois honnête sur l'échec, mets l'accent sur les leçons apprises."
    },
    {
        "question": "Comment organises-tu ton travail quand tu dois gérer plusieurs tâches en parallèle ?",
        "conseil":  "Cite des outils concrets : Trello, GitHub Issues, Notion..."
    },
    {
        "question": "Qu'est-ce qui te motive à rejoindre cette équipe plutôt qu'une autre entreprise ?",
        "conseil":  "Montre que tu as fait des recherches sur l'entreprise."
    },
]

QUESTIONS_MOTIVATION = [
    "Où te vois-tu dans 3 ans après ce stage ?",
    "Qu'est-ce qui t'a poussé à choisir la spécialité {domain} dans ton Master ?",
    "Quel projet personnel ou académique es-tu le plus fier(e) de présenter ?",
    "Comment restes-tu à jour sur les dernières avancées en {domain} ?",
    "Qu'est-ce que tu espères apporter à l'équipe de {company} pendant ce stage ?",
]


def entretien_node(state: dict) -> dict:
    """
    Agent Entretien Prep — génère 5 questions ciblées :
    2 techniques (basées sur les mots-clés ATS de l'offre)
    2 comportementales
    1 motivation
    """
    offer  = state.get("selected_offer", {})
    cv     = state.get("cv_text", "")
    domain = state.get("target_domain", "Intelligence Artificielle")
    gaps   = state.get("gaps", [])

    print(f"[ENTRETIEN] Génération des questions pour : {offer.get('title')} chez {offer.get('company')}")

    # Génération via LLM si disponible, sinon banque locale
    questions = _call_llm(offer, cv, domain, gaps)
    if not questions:
        questions = _build_questions_local(offer, domain, gaps)

    print(f"[ENTRETIEN] ✅ {len(questions)} questions générées")

    return {
        **state,
        "interview_questions": questions,
        "messages": state.get("messages", []) + [
            {
                "role":    "entretien",
                "content": f"{len(questions)} questions générées pour {offer.get('title')}"
            }
        ]
    }


def _build_questions_local(offer: dict, domain: str, gaps: list) -> list:
    """Génère 5 questions depuis la banque locale."""
    import random

    keywords = offer.get("ats_keywords", [])
    company  = offer.get("company", "cette entreprise")
    title    = offer.get("title", "ce poste")
    questions = []

    # ── 2 questions techniques ─────────────────────────────────
    tech_asked = 0

    # Priorité aux gaps — les recruteurs testent souvent les points faibles
    for skill in gaps:
        if tech_asked >= 2:
            break
        if skill in QUESTIONS_TECHNIQUES:
            questions.append({
                "type":     "technique",
                "question": QUESTIONS_TECHNIQUES[skill],
                "conseil":  f"Sois honnête si tu ne maîtrises pas encore {skill} — montre ta volonté d'apprendre.",
            })
            tech_asked += 1

    # Compléter avec les mots-clés ATS de l'offre
    for skill in keywords:
        if tech_asked >= 2:
            break
        already = any(q.get("question") == QUESTIONS_TECHNIQUES.get(skill) for q in questions)
        if skill in QUESTIONS_TECHNIQUES and not already:
            questions.append({
                "type":     "technique",
                "question": QUESTIONS_TECHNIQUES[skill],
                "conseil":  f"Appuie ta réponse sur un projet concret où tu as utilisé {skill}.",
            })
            tech_asked += 1

    # Fallback si toujours pas assez
    if tech_asked < 2:
        questions.append({
            "type":     "technique",
            "question": f"Décris un projet technique récent en lien avec {title}. Quelles technologies as-tu utilisées ?",
            "conseil":  "Prépare 2-3 projets GitHub à présenter avec des métriques concrètes.",
        })

    # ── 2 questions comportementales ───────────────────────────
    selected_behav = random.sample(QUESTIONS_COMPORTEMENTALES, min(2, len(QUESTIONS_COMPORTEMENTALES)))
    for q in selected_behav:
        questions.append({
            "type":     "comportemental",
            "question": q["question"],
            "conseil":  q["conseil"],
        })

    # ── 1 question motivation ──────────────────────────────────
    motiv_template = random.choice(QUESTIONS_MOTIVATION)
    questions.append({
        "type":     "motivation",
        "question": motiv_template.format(domain=domain, company=company),
        "conseil":  f"Montre que tu connais {company} — visite leur site et LinkedIn avant l'entretien.",
    })

    return questions[:5]


def _call_llm(offer: dict, cv_text: str, domain: str, gaps: list) -> list | None:
    """Génère des questions personnalisées via Claude API."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
        import json

        client = anthropic.Anthropic(api_key=api_key)

        prompt = f"""Tu es un recruteur expert en entretiens tech au Maroc.

Poste : {offer.get('title')} chez {offer.get('company')} ({offer.get('location')})
Competences requises : {', '.join(offer.get('ats_keywords', []))}
Competences manquantes du candidat : {', '.join(gaps) if gaps else 'aucune'}
Extrait du CV : {cv_text[:400]}

Genere exactement 5 questions d entretien ciblees :
- 2 questions techniques (basees sur les competences ATS de l offre)
- 2 questions comportementales (methode STAR)
- 1 question motivation (specifique a l entreprise)

Reponds UNIQUEMENT en JSON valide, sans texte autour :
[
  {{
    "type": "technique|comportemental|motivation",
    "question": "question complete",
    "conseil": "conseil de preparation court (max 15 mots)"
  }}
]"""

        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return result[:5]

    except Exception as e:
        print(f"[ENTRETIEN] ⚠️  LLM echoue: {e} — fallback local")
        return None