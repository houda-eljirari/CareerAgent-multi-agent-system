# agents/scraper.py — Agent Scraper (offres mockées JSON réalistes)

import random

OFFRES_POOL = [
    {
        "title": "Stage Data Scientist",
        "company": "OCP Digital",
        "location": "Casablanca",
        "duration": "6 mois",
        "ats_keywords": ["Python", "PyTorch", "MLOps", "Scikit-learn", "Git"],
        "description": "Développement de modèles ML pour l'optimisation de la chaîne de valeur phosphatière.",
        "source": "LinkedIn",
    },
    {
        "title": "Stage ML Engineer",
        "company": "CIH Bank",
        "location": "Rabat",
        "duration": "6 mois",
        "ats_keywords": ["Python", "TensorFlow", "Docker", "FastAPI", "Git"],
        "description": "Déploiement de modèles de scoring crédit et détection de fraude.",
        "source": "Rekrute",
    },
    {
        "title": "Stage QA Engineer",
        "company": "Capgemini Maroc",
        "location": "Casablanca",
        "duration": "4 mois",
        "ats_keywords": ["Pytest", "Selenium", "CI/CD", "Jenkins", "Postman"],
        "description": "Automatisation des tests fonctionnels et intégration dans les pipelines CI/CD.",
        "source": "Indeed",
    },
    {
        "title": "Stage Ingénieur IA",
        "company": "Maroc Telecom",
        "location": "Rabat",
        "duration": "6 mois",
        "ats_keywords": ["Python", "LangChain", "RAG", "ChromaDB", "Docker"],
        "description": "Développement d'assistants conversationnels basés sur LLMs pour le support client.",
        "source": "LinkedIn",
    },
    {
        "title": "Stage Backend Developer",
        "company": "HPS HighTech Payment",
        "location": "Casablanca",
        "duration": "4 mois",
        "ats_keywords": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
        "description": "Développement d'APIs REST pour les systèmes de paiement électronique.",
        "source": "Rekrute",
    },
    {
        "title": "Stage MLOps Engineer",
        "company": "IBM Maroc",
        "location": "Casablanca",
        "duration": "6 mois",
        "ats_keywords": ["MLOps", "Docker", "Kubernetes", "Python", "CI/CD"],
        "description": "Mise en place de pipelines MLOps pour le déploiement continu de modèles en production.",
        "source": "LinkedIn",
    },
    {
        "title": "Stage Test Automation Engineer",
        "company": "CGI Maroc",
        "location": "Casablanca",
        "duration": "5 mois",
        "ats_keywords": ["Selenium", "Cypress", "Pytest", "BDD", "Gherkin"],
        "description": "Création de frameworks d'automatisation de tests pour des applications web critiques.",
        "source": "Indeed",
    },
    {
        "title": "Stage Data Engineer",
        "company": "Attijariwafa Bank Digital",
        "location": "Casablanca",
        "duration": "6 mois",
        "ats_keywords": ["Python", "Spark", "Kafka", "SQL", "Docker"],
        "description": "Construction de pipelines de données pour la plateforme analytique de la banque.",
        "source": "Emploi.ma",
    },
    {
        "title": "Stage NLP Engineer",
        "company": "inwi",
        "location": "Rabat",
        "duration": "4 mois",
        "ats_keywords": ["Python", "Hugging Face", "LangChain", "NLP", "FastAPI"],
        "description": "Développement de modèles NLP pour l'analyse des sentiments clients.",
        "source": "LinkedIn",
    },
    {
        "title": "Stage DevOps & MLOps",
        "company": "Oracle Maroc",
        "location": "Casablanca",
        "duration": "6 mois",
        "ats_keywords": ["Docker", "Kubernetes", "CI/CD", "Python", "Git"],
        "description": "Automatisation des déploiements et intégration des workflows ML dans le cloud Oracle.",
        "source": "LinkedIn",
    },
    {
        "title": "Stage Développeur IA Générative",
        "company": "BMCE Bank",
        "location": "Casablanca",
        "duration": "5 mois",
        "ats_keywords": ["LangChain", "LangGraph", "Python", "RAG", "OpenAI"],
        "description": "Conception d'agents IA pour automatiser le traitement des documents bancaires.",
        "source": "Rekrute",
    },
    {
        "title": "Stage Computer Vision",
        "company": "OCP Digital",
        "location": "Khouribga",
        "duration": "6 mois",
        "ats_keywords": ["Python", "OpenCV", "PyTorch", "YOLO", "Git"],
        "description": "Développement de systèmes de vision par ordinateur pour le contrôle qualité.",
        "source": "Indeed",
    },
    {
        "title": "Stage Full Stack AI",
        "company": "Capgemini Maroc",
        "location": "Casablanca",
        "duration": "4 mois",
        "ats_keywords": ["Python", "FastAPI", "React", "Docker", "LangChain"],
        "description": "Développement d'une application web intégrant des fonctionnalités IA.",
        "source": "LinkedIn",
    },
    {
        "title": "Stage Performance Testing",
        "company": "HPS HighTech Payment",
        "location": "Casablanca",
        "duration": "3 mois",
        "ats_keywords": ["JMeter", "Python", "API Testing", "Postman", "CI/CD"],
        "description": "Tests de charge et performance sur les systèmes de paiement.",
        "source": "Emploi.ma",
    },
    {
        "title": "Stage IA & Robotique",
        "company": "Maroc Telecom",
        "location": "Rabat",
        "duration": "6 mois",
        "ats_keywords": ["Python", "ROS", "PyTorch", "OpenCV", "Git"],
        "description": "Développement d'algorithmes de navigation autonome pour robots industriels.",
        "source": "LinkedIn",
    },
]


def scraper_node(state: dict) -> dict:
    """
    Agent Scraper — retourne des offres structurées filtrées par domaine.
    Les offres sont mockées mais réalistes (Maroc, 2025).
    """
    domain = state.get("target_domain", "").lower()
    query  = state.get("user_query", "").lower()

    print(f"[SCRAPER] Recherche d'offres — domaine: '{domain}' | query: '{query}'")

    # Filtrage par domaine cible
    domain_keywords = _get_domain_keywords(domain, query)
    filtered = _filter_offers(OFFRES_POOL, domain_keywords)

    # Si pas assez d'offres filtrées, compléter avec des offres aléatoires
    if len(filtered) < 5:
        remaining = [o for o in OFFRES_POOL if o not in filtered]
        filtered += random.sample(remaining, min(5 - len(filtered), len(remaining)))

    print(f"[SCRAPER] {len(filtered)} offres trouvées pour '{domain}'")

    return {
        **state,
        "job_offers": filtered,
        "messages": state.get("messages", []) + [
            {
                "role": "scraper",
                "content": f"{len(filtered)} offres trouvées — domaine: {domain}"
            }
        ]
    }


def _get_domain_keywords(domain: str, query: str) -> list:
    """Retourne les mots-clés associés au domaine cible."""
    mapping = {
        "intelligence artificielle": ["IA", "ML", "LangChain", "NLP", "PyTorch", "TensorFlow", "RAG"],
        "testing":                   ["QA", "Selenium", "Pytest", "Cypress", "BDD", "JMeter", "Test"],
        "qa":                        ["QA", "Selenium", "Pytest", "Cypress", "BDD", "JMeter", "Test"],
        "backend":                   ["FastAPI", "Backend", "PostgreSQL", "API", "Docker"],
        "devops":                    ["Docker", "Kubernetes", "CI/CD", "MLOps", "DevOps"],
        "data science":              ["Data", "Spark", "SQL", "Scikit-learn", "Analytics"],
        "full stack":                ["React", "FastAPI", "Full Stack", "Docker"],
    }
    for key, kws in mapping.items():
        if key in domain or key in query:
            return kws
    return ["Python", "IA", "ML", "Data"]  # fallback générique


def _filter_offers(offers: list, keywords: list) -> list:
    """Filtre et trie les offres selon les mots-clés du domaine."""
    scored = []
    for offer in offers:
        title_text = (offer["title"] + " " + offer["description"]).lower()
        ats        = [k.lower() for k in offer["ats_keywords"]]
        score      = sum(1 for kw in keywords if kw.lower() in title_text or kw.lower() in ats)
        if score > 0:
            scored.append((score, offer))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [o for _, o in scored]