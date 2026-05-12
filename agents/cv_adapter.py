# agents/cv_adapter.py — Agent CV Adapter (Prompt B optimisé ATS)

import os
import re
from dotenv import load_dotenv

load_dotenv()

# ── Prompt A (basique) — utilisé pour le test A/B ─────────────
PROMPT_A = """Adapte ce CV pour cette offre d'emploi.

CV original :
{cv_text}

Offre :
Titre : {title}
Entreprise : {company}
Compétences requises : {keywords}

Retourne le CV adapté."""

# ── Prompt B (optimisé ATS) — version production ──────────────
PROMPT_B = """Tu es un expert RH spécialisé en optimisation ATS (Applicant Tracking System).

Ta mission : adapter ce CV pour maximiser le score ATS pour l'offre ci-dessous.

RÈGLES STRICTES :
1. Identifie les 5 mots-clés ATS critiques de l'offre
2. Intègre ces mots-clés naturellement dans le CV (résumé, compétences, expériences)
3. Réécris UNIQUEMENT les sections pertinentes — ne supprime rien d'original
4. N'invente AUCUNE compétence absente du CV original
5. Garde un format simple lisible par les systèmes ATS (pas de tableaux)
6. Maximum 1 page équivalent texte

CV ORIGINAL :
{cv_text}

OFFRE CIBLE :
Titre du poste : {title}
Entreprise : {company}
Mots-clés ATS détectés : {keywords}
Description : {description}
{feedback_section}

FORMAT DE RÉPONSE ATTENDU :
---RÉSUMÉ PROFESSIONNEL---
[2-3 phrases avec mots-clés ATS intégrés]

---COMPÉTENCES TECHNIQUES---
[Liste des compétences du CV original + mots-clés ATS de l'offre présents dans le profil]

---EXPÉRIENCES / PROJETS---
[Reformulation des expériences existantes avec terminologie de l'offre]

---FORMATION---
[Inchangée]

---MOTS-CLÉS ATS INTÉGRÉS---
[Liste des 5 mots-clés utilisés]"""


def cv_adapter_node(state: dict) -> dict:
    """
    Agent CV Adapter — adapte le CV avec le Prompt B optimisé ATS.
    Utilise l'API Claude si disponible, sinon fallback local.
    """
    offer    = state.get("selected_offer") or (state.get("ranked_offers") or [{}])[0]
    cv_text  = state.get("cv_text", "")
    feedback = state.get("human_feedback", "")

    retry_count = state.get("_retry_count", 0)

    # Protection contre les boucles infinies
    if retry_count >= 3:
        print("[CV ADAPTER] ⚠️  Max retries atteint — adaptation simplifiée")
        adapted = _simple_adapt(cv_text, offer)
        return {
            **state,
            "adapted_cv":    adapted,
            "human_validated": False,
            "qa_passed":     True,
            "_retry_count":  0,
            "messages": state.get("messages", []) + [
                {"role": "cv_adapter", "content": "CV adapté (fallback simplifié)"}
            ]
        }

    print(f"[CV ADAPTER] Adaptation pour : {offer.get('title')} chez {offer.get('company')}")
    print(f"[CV ADAPTER] Prompt B — retry #{retry_count}")

    # Construction du prompt
    feedback_section = f"\nFEEDBACK HUMAIN À INTÉGRER :\n{feedback}" if feedback else ""
    prompt = PROMPT_B.format(
        cv_text=cv_text,
        title=offer.get("title", ""),
        company=offer.get("company", ""),
        keywords=", ".join(offer.get("ats_keywords", [])),
        description=offer.get("description", ""),
        feedback_section=feedback_section,
    )

    # Appel LLM (Claude API ou fallback)
    adapted_cv = _call_llm(prompt, offer, cv_text)

    print(f"[CV ADAPTER] ✅ CV adapté ({len(adapted_cv)} caractères)")

    return {
        **state,
        "adapted_cv":      adapted_cv,
        "human_validated": False,
        "qa_passed":       False,
        "selected_offer":  offer,
        "_retry_count":    retry_count + 1,
        "messages": state.get("messages", []) + [
            {
                "role":    "cv_adapter",
                "content": f"CV adapté pour {offer.get('title')} chez {offer.get('company')} (Prompt B)"
            }
        ]
    }


def _call_llm(prompt: str, offer: dict, cv_text: str) -> str:
    """Appelle Claude API si dispo, sinon adaption locale."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        try:
            import anthropic
            client   = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"[CV ADAPTER] ⚠️  API error: {e} — fallback local")

    # Fallback sans API
    return _simple_adapt(cv_text, offer)


def _simple_adapt(cv_text: str, offer: dict) -> str:
    """Adaptation locale sans LLM — injecte les mots-clés ATS."""
    keywords = offer.get("ats_keywords", [])
    title    = offer.get("title", "")
    company  = offer.get("company", "")

    # Détecte les mots-clés déjà présents dans le CV
    present = [kw for kw in keywords if kw.lower() in cv_text.lower()]
    missing = [kw for kw in keywords if kw.lower() not in cv_text.lower()]

    adapted = f"""---RÉSUMÉ PROFESSIONNEL---
Étudiante en Master Systèmes Distribués & Intelligence Artificielle, avec expérience pratique en {', '.join(present[:3]) if present else 'Python et Machine Learning'}. Candidate motivée pour le poste de {title} chez {company}.

---COMPÉTENCES TECHNIQUES---
Compétences existantes : {cv_text[:200].strip() if cv_text else 'Voir CV original'}
Compétences ATS ciblées : {', '.join(keywords)}

---EXPÉRIENCES / PROJETS---
{_extract_experiences(cv_text)}

---FORMATION---
Master Systèmes Distribués & Intelligence Artificielle — ENSET

---MOTS-CLÉS ATS INTÉGRÉS---
{', '.join(keywords)}

--- CV ADAPTÉ POUR : {title} chez {company} ---
{'⚠️  Compétences à développer pour ce poste : ' + ', '.join(missing) if missing else '✅ Profil bien aligné avec les exigences du poste'}
"""
    return adapted


def _extract_experiences(cv_text: str) -> str:
    """Extrait la section expériences du CV si disponible."""
    if not cv_text:
        return "Voir CV original"
    # Retourne les 300 premiers caractères du CV comme proxy
    return cv_text[:300].strip() + "..." if len(cv_text) > 300 else cv_text


# ── Fonction utilitaire pour le test A/B ──────────────────────

def adapt_with_prompt_a(cv_text: str, offer: dict) -> str:
    """Version Prompt A — utilisée uniquement pour le test A/B."""
    prompt = PROMPT_A.format(
        cv_text=cv_text,
        title=offer.get("title", ""),
        company=offer.get("company", ""),
        keywords=", ".join(offer.get("ats_keywords", [])),
    )
    return _call_llm(prompt, offer, cv_text)


def adapt_with_prompt_b(cv_text: str, offer: dict, feedback: str = "") -> str:
    """Version Prompt B — utilisée pour le test A/B et la production."""
    feedback_section = f"\nFEEDBACK HUMAIN À INTÉGRER :\n{feedback}" if feedback else ""
    prompt = PROMPT_B.format(
        cv_text=cv_text,
        title=offer.get("title", ""),
        company=offer.get("company", ""),
        keywords=", ".join(offer.get("ats_keywords", [])),
        description=offer.get("description", ""),
        feedback_section=feedback_section,
    )
    return _call_llm(prompt, offer, cv_text)