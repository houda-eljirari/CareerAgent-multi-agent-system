# test_analyste.py
from agents.analyste import analyste_node

state = {
    "cv_text": "Étudiante Master IA. Compétences : Python, LangChain, LangGraph, Git, Docker, RAG, ChromaDB. Projet : système multi-agent.",
    "user_query": "analyser les offres",
    "target_domain": "IA",
    "job_offers": [
        {"title": "Stage Data Scientist",  "company": "OCP Digital",     "location": "Casablanca"},
        {"title": "Stage ML Engineer",     "company": "CIH Bank",        "location": "Rabat"},
        {"title": "Stage QA Engineer",     "company": "Capgemini Maroc", "location": "Casablanca"},
    ],
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

result = analyste_node(state)

print("\n📊 Classement des offres :")
for o in result["ranked_offers"]:
    print(f"  {o['fit_level']:10} | {o['score']:3}/100 | {o['title']} chez {o['company']}")
    print(f"             Matched : {o['matched_skills']}")
    print(f"             Missing : {o['missing_skills']}")