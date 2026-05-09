# test_graph.py — Test du routing LangGraph
from graph import app

config = {"configurable": {"thread_id": "test-1"}}

# ── TEST 1 : Chercher des offres ──
print("=" * 50)
print("TEST 1 — Chercher des offres de stage")
print("=" * 50)

state_1 = {
    "cv_text": "Étudiante Master IA, compétences Python, ML",
    "user_query": "Je cherche un stage en IA",
    "target_domain": "Intelligence Artificielle",
    "job_offers": [],
    "ranked_offers": [],
    "selected_offer": {},
    "adapted_cv": "",
    "gaps": [],
    "interview_questions": [],
    "next_agent": "",
    "human_validated": False,
    "human_feedback": "",
    "qa_passed": False,
    "messages": [],
}

result = app.invoke(state_1, config)

print("\n📋 Résultat :")
print(f"  Offres trouvées : {len(result.get('job_offers', []))}")
for o in result.get("job_offers", []):
    print(f"  → {o['title']} chez {o['company']} (score: {o['score']})")

print("\n💬 Messages du workflow :")
for m in result.get("messages", []):
    print(f"  [{m['role']}] {m['content']}")


# ── TEST 2 : Adapter le CV ──
print("\n" + "=" * 50)
print("TEST 2 — Adapter le CV")
print("=" * 50)

config2 = {"configurable": {"thread_id": "test-2"}}

state_2 = {
    "cv_text": "Étudiante Master IA, compétences Python, ML",
    "user_query": "Je veux adapter mon cv",
    "target_domain": "IA",
    "job_offers": [],
    "ranked_offers": [],
    "selected_offer": {"title": "Stage Data Scientist", "company": "OCP Digital"},
    "adapted_cv": "",
    "gaps": [],
    "interview_questions": [],
    "next_agent": "",
    "human_validated": False,
    "human_feedback": "",
    "qa_passed": False,
    "messages": [],
}

# Lance jusqu'au point d'interruption human_loop
result2 = app.invoke(state_2, config2)

print("\n📋 Résultat avant validation humaine :")
print(f"  CV adapté : {result2.get('adapted_cv')}")
print(f"  QA passé : {result2.get('qa_passed')}")
print(f"  Human validé : {result2.get('human_validated')}")
print("\n⚠️  Le graph est en pause — attente validation humaine")

# Simule la validation humaine
print("\n✅ Simulation : l'utilisateur valide le CV")

# ⚠️ La bonne façon de reprendre après interruption LangGraph :
# On met à jour le state via update_state, puis on reprend avec None
app.update_state(config2, {"human_validated": True})

# Reprend depuis le point d'interruption
result3 = app.invoke(None, config2)

print("\n📋 Résultat après validation :")
print(f"  Gaps détectés : {result3.get('gaps')}")
print(f"  Questions entretien : {len(result3.get('interview_questions', []))}")
print("\n💬 Messages du workflow :")
for m in result3.get("messages", []):
    print(f"  [{m['role']}] {m['content']}")