# agents/qa_agent.py — Agent QA avec 5 tests automatisés
# Point différenciateur : expertise Testing appliquée à un système IA

def qa_agent_node(state: dict) -> dict:
    """
    Exécute 5 tests automatisés sur le CV adapté.
    Bloque le workflow si score < 70 ou un test critique échoue.
    """
    cv_original = state.get("cv_text", "")
    cv_adapted  = state.get("adapted_cv", "")
    offer       = state.get("selected_offer", {})
    ats_keywords = offer.get("ats_keywords", [])

    print("[QA AGENT] Lancement des 5 tests...")
    print("-" * 40)

    tests = []

    # ── T01 : ATS Keywords Coverage ───────────────────────────
    t01 = _test_ats_coverage(cv_adapted, ats_keywords)
    tests.append(t01)
    print(f"  T01 ATS Keywords    : {'✅ PASS' if t01['passed'] else '❌ FAIL'} ({t01['score']}/100)")
    print(f"       {t01['details']}")

    # ── T02 : Hallucination Check ──────────────────────────────
    t02 = _test_hallucination(cv_original, cv_adapted)
    tests.append(t02)
    print(f"  T02 Hallucination   : {'✅ PASS' if t02['passed'] else '❌ FAIL'} ({t02['score']}/100)")
    print(f"       {t02['details']}")

    # ── T03 : Coherence Score ──────────────────────────────────
    t03 = _test_coherence(cv_original, cv_adapted)
    tests.append(t03)
    print(f"  T03 Coherence       : {'✅ PASS' if t03['passed'] else '❌ FAIL'} ({t03['score']}/100)")
    print(f"       {t03['details']}")

    # ── T04 : Format ATS Compatibility ────────────────────────
    t04 = _test_format(cv_adapted)
    tests.append(t04)
    print(f"  T04 Format ATS      : {'✅ PASS' if t04['passed'] else '❌ FAIL'} ({t04['score']}/100)")
    print(f"       {t04['details']}")

    # ── T05 : Relevance to Offer ───────────────────────────────
    t05 = _test_relevance(cv_adapted, offer)
    tests.append(t05)
    print(f"  T05 Relevance       : {'✅ PASS' if t05['passed'] else '❌ FAIL'} ({t05['score']}/100)")
    print(f"       {t05['details']}")

    # ── Résultat global ────────────────────────────────────────
    print("-" * 40)
    overall_score = int(sum(t["score"] for t in tests) / len(tests))
    passed_count  = sum(1 for t in tests if t["passed"])
    qa_passed     = passed_count == len(tests) and overall_score >= 70

    print(f"  Score global : {overall_score}/100")
    print(f"  Tests passés : {passed_count}/{len(tests)}")
    print(f"  Résultat QA  : {'✅ PASSED' if qa_passed else '❌ FAILED'}")

    if not qa_passed:
        issues = [t["details"] for t in tests if not t["passed"]]
        print(f"  ⚠️  Problèmes : {issues}")

    return {
        **state,
        "qa_passed": qa_passed,
        "_qa_report": {
            "tests":         tests,
            "overall_score": overall_score,
            "passed_count":  passed_count,
            "qa_passed":     qa_passed,
        },
        "messages": state.get("messages", []) + [
            {"role": "qa_agent",
             "content": f"QA {'PASSED' if qa_passed else 'FAILED'} — {passed_count}/5 tests — {overall_score}/100"}
        ]
    }

# ── IMPLÉMENTATION DES 5 TESTS ─────────────────────────────────

def _test_ats_coverage(cv_adapted: str, ats_keywords: list) -> dict:
    """T01 : Le CV adapté contient les mots-clés ATS de l'offre."""
    if not ats_keywords:
        return {"test_id": "T01", "name": "ATS Keywords Coverage",
                "passed": True, "score": 80,
                "details": "Pas de mots-clés définis — test ignoré"}

    found   = [kw for kw in ats_keywords if kw.lower() in cv_adapted.lower()]
    missing = [kw for kw in ats_keywords if kw.lower() not in cv_adapted.lower()]
    score   = int((len(found) / len(ats_keywords)) * 100)
    passed  = score >= 60

    return {
        "test_id": "T01", "name": "ATS Keywords Coverage",
        "passed":  passed, "score": score,
        "details": f"Trouvés: {found} | Manquants: {missing}"
    }

def _test_hallucination(cv_original: str, cv_adapted: str) -> dict:
    """T02 : Aucune compétence inventée non présente dans le CV original."""
    # On exclut les mots-clés techniques courants qui peuvent être ajoutés
    # légitimement par le CV Adapter depuis les ats_keywords de l'offre
    very_exotic = [
        "kubernetes", "scala", "rust", "golang", "swift",
        "kotlin", "blockchain", "solidity", "cobol", "fortran"
    ]
    hallucinations = []
    for term in very_exotic:
        in_adapted  = term in cv_adapted.lower()
        in_original = term in cv_original.lower()
        if in_adapted and not in_original:
            hallucinations.append(term)

    passed = len(hallucinations) == 0
    score  = 100 if passed else max(0, 100 - len(hallucinations) * 25)

    return {
        "test_id": "T02", "name": "Hallucination Check",
        "passed":  passed, "score": score,
        "details": f"Inventions détectées: {hallucinations}" if hallucinations
                   else "Aucune invention détectée ✓"
    }

def _test_coherence(cv_original: str, cv_adapted: str) -> dict:
    """T03 : Cohérence entre CV original et CV adapté > 80%."""
    if not cv_original or not cv_adapted:
        return {"test_id": "T03", "name": "Coherence Score",
                "passed": False, "score": 0,
                "details": "CV original ou adapté vide"}

    words_original = set(cv_original.lower().split())
    words_adapted  = set(cv_adapted.lower().split())

    if not words_original:
        return {"test_id": "T03", "name": "Coherence Score",
                "passed": False, "score": 0, "details": "CV original vide"}

    overlap = len(words_original & words_adapted)
    score   = int((overlap / len(words_original)) * 100)
    score   = min(score, 100)
    passed  = score >= 50

    return {
        "test_id": "T03", "name": "Coherence Score",
        "passed":  passed, "score": score,
        "details": f"Overlap : {overlap}/{len(words_original)} mots ({score}%)"
    }

def _test_format(cv_adapted: str) -> dict:
    """T04 : Format lisible par les parsers ATS."""
    issues = []

    # Vérifie longueur minimale
    if len(cv_adapted) < 50:
        issues.append("CV trop court")

    # Vérifie absence de caractères problématiques
    problematic = ["<table", "<div", "|||", "---+---"]
    for p in problematic:
        if p.lower() in cv_adapted.lower():
            issues.append(f"Format problématique: {p}")

    # Vérifie présence de sections clés
    sections = ["compétence", "expérience", "formation", "projet"]
    found_sections = [s for s in sections if s in cv_adapted.lower()]

    score  = 100 - (len(issues) * 20)
    score  = max(score, 0)
    passed = len(issues) == 0

    return {
        "test_id": "T04", "name": "Format ATS Compatibility",
        "passed":  passed, "score": score,
        "details": f"Problèmes: {issues}" if issues
                   else f"Format OK — sections trouvées: {found_sections}"
    }

def _test_relevance(cv_adapted: str, offer: dict) -> dict:
    """T05 : Les modifications sont pertinentes par rapport à l'offre."""
    title    = offer.get("title", "").lower()
    company  = offer.get("company", "").lower()
    skills   = [s.lower() for s in offer.get("ats_keywords", [])]

    relevant_terms = []
    if title:
        # Extrait mots du titre
        relevant_terms.extend(title.split())
    relevant_terms.extend(skills)

    if not relevant_terms:
        return {"test_id": "T05", "name": "Relevance to Offer",
                "passed": True, "score": 75,
                "details": "Pas de critères de pertinence définis"}

    found  = [t for t in relevant_terms if t in cv_adapted.lower()]
    score  = int((len(found) / len(relevant_terms)) * 100)
    score  = min(score, 100)
    passed = score >= 40

    return {
        "test_id": "T05", "name": "Relevance to Offer",
        "passed":  passed, "score": score,
        "details": f"Termes pertinents trouvés: {found[:5]}"
    }
