# test_integration.py — Test complet end-to-end
from graph import app

config = {"configurable": {"thread_id": "integration-1"}}

state = {
    "cv_text": "Étudiante Master IA. Compétences : Python, LangChain, LangGraph, Git, Docker, RAG. Projet : système multi-agent avec ChromaDB.",
    "user_query": "Je cherche un stage en IA",
    "target_domain": "IA",
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

print("=" * 55)
print("ÉTAPE 1 — Recherche et scoring des offres")
print("=" * 55)
result = app.invoke(state, config)

print("\n📊 Offres classées :")
for o in result.get("ranked_offers", []):
    print(f"  {o.get('fit_level','?'):10} | {o.get('score',0):3}/100 | {o['title']}")

# Sélectionne la meilleure offre
best_offer = result["ranked_offers"][0]
print(f"\n✅ Offre sélectionnée : {best_offer['title']} chez {best_offer['company']}")

print("\n" + "=" * 55)
print("ÉTAPE 2 — Adaptation CV + QA")
print("=" * 55)

config2 = {"configurable": {"thread_id": "integration-2"}}
state2  = {**result,
    "user_query":      "Je veux adapter mon cv",
    "selected_offer":  best_offer,
    "adapted_cv":      "",
    "human_validated": False,
    "qa_passed":       False,
    "messages":        [],
}

result2 = app.invoke(state2, config2)

print(f"\n📄 CV adapté (extrait) : {result2.get('adapted_cv','')[:100]}...")
print(f"🔬 QA passé : {result2.get('qa_passed')}")
print("\n⚠️  Graph en pause — validation humaine requise")

print("\n" + "=" * 55)
print("ÉTAPE 3 — Validation humaine + Gap + Entretien")
print("=" * 55)

print("✅ Simulation : tu valides le CV")
app.update_state(config2, {"human_validated": True})
result3 = app.invoke(None, config2)

print(f"\n📋 Gaps identifiés : {result3.get('gaps')}")
print(f"🎤 Questions générées : {len(result3.get('interview_questions', []))}")
for q in result3.get("interview_questions", []):
    print(f"  → [{q['type']}] {q['question']}")

print("\n" + "=" * 55)
print("✅ FLUX COMPLET END-TO-END RÉUSSI !")
print("=" * 55)
print("\n💬 Historique complet des agents :")
for m in result3.get("messages", []):
    print(f"  [{m['role']:12}] {m['content']}")