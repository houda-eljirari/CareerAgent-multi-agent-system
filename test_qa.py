# test_qa.py — Test de l'Agent QA
from agents.qa_agent import qa_agent_node

print("=" * 50)
print("TEST 1 — CV de bonne qualité (doit PASSER)")
print("=" * 50)

state_good = {
    "cv_text": "Étudiante Master IA. Compétences : Python, LangChain, Git, Docker. Projet : système multi-agent LangGraph.",
    "adapted_cv": "Étudiante Master IA spécialisée en Data Science. Compétences : Python, LangChain, Git, Docker, Scikit-learn. Expérience : projet multi-agent LangGraph avec RAG. Formation : Master Systèmes Distribués.",
    "selected_offer": {
        "title": "Stage Data Scientist",
        "company": "OCP Digital",
        "ats_keywords": ["Python", "LangChain", "Git", "Docker"]
    },
    "messages": []
}

result1 = qa_agent_node(state_good)
print(f"\nQA Passed : {result1['qa_passed']}")

print("\n" + "=" * 50)
print("TEST 2 — CV avec hallucinations (doit ÉCHOUER)")
print("=" * 50)

state_bad = {
    "cv_text": "Étudiante Master IA. Compétences : Python, Git.",
    "adapted_cv": "Expert en PyTorch, TensorFlow, Kubernetes, Scala, Blockchain. Expérience chez Google et Microsoft.",
    "selected_offer": {
        "title": "Stage ML Engineer",
        "company": "CIH Bank",
        "ats_keywords": ["PyTorch", "TensorFlow"]
    },
    "messages": []
}

result2 = qa_agent_node(state_bad)
print(f"\nQA Passed : {result2['qa_passed']}")