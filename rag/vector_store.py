# rag/vector_store.py — Base vectorielle ChromaDB (embeddings intégrés)
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import os

load_dotenv()

CHROMA_PATH = "./chroma_db"
COLLECTION  = "careeragent_knowledge"

# Embeddings intégrés ChromaDB — aucune API requise !
default_ef = embedding_functions.DefaultEmbeddingFunction()

def get_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_collection():
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION,
        embedding_function=default_ef
    )

def get_retriever(k: int = 3):
    """Retourne une fonction de recherche simple."""
    collection = get_collection()
    def retriever(query: str):
        results = collection.query(
            query_texts=[query],
            n_results=k
        )
        docs = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            docs.append({"page_content": doc, "metadata": meta})
        return docs
    return retriever

def add_cv_to_rag(cv_text: str):
    """Ajoute le CV à la base."""
    collection = get_collection()
    # Découpe en chunks de 500 caractères
    chunks = [cv_text[i:i+500] for i in range(0, len(cv_text), 500)]
    ids = [f"cv_chunk_{i}" for i in range(len(chunks))]
    collection.add(
        documents=chunks,
        metadatas=[{"type": "cv"} for _ in chunks],
        ids=ids
    )
    print(f"[RAG] ✅ {len(chunks)} chunks CV ajoutés")

def seed_knowledge_base():
    """Initialise la base avec des connaissances de démarrage."""
    collection = get_collection()

    docs = [
        "Compétences clés pour les stages IA/ML au Maroc en 2025 : Python, PyTorch, TensorFlow, Scikit-learn, LangChain, LangGraph, Hugging Face, RAG, ChromaDB, MLOps, Docker, Git, FastAPI. Les recruteurs marocains recherchent surtout : Python avancé, deep learning, APIs REST, et des projets concrets sur GitHub.",
        "Compétences clés pour les stages Testing/QA en 2025 : Selenium, Pytest, Cypress, JUnit, Postman, Jest, JMeter, CI/CD GitHub Actions, Jenkins, BDD Gherkin, Cucumber, API Testing, Performance Testing, Test Automation Framework.",
        "Bonnes pratiques ATS pour CV tech 2025 : utiliser les mots-clés exacts de l'offre, sections simples Résumé Compétences Expérience Formation Projets, quantifier les réalisations, format PDF simple police Arial, maximum 1 page pour moins de 2 ans d'expérience.",
        "Entreprises tech qui recrutent des stagiaires au Maroc 2025 : OCP Digital, Maroc Telecom, CIH Bank, HPS HighTech Payment, Capgemini Maroc, CGI Maroc, IBM Maroc, Oracle Maroc, inwi, BMCE Bank, Attijariwafa bank Digital. Plateformes : Rekrute.com, Indeed.ma, LinkedIn, Emploi.ma",
        "Template résumé professionnel pour stage IA : Étudiante en Master Systèmes Distribués et Intelligence Artificielle, avec expérience pratique en Python, Machine Learning et LangChain. Projet réalisé : système multi-agent avec LangGraph et RAG. Compétences : Python, PyTorch, LangChain, LangGraph, ChromaDB, Docker, Git.",
    ]

    metadatas = [
        {"type": "market", "domain": "AI"},
        {"type": "market", "domain": "Testing"},
        {"type": "best_practice", "domain": "CV"},
        {"type": "market", "domain": "Maroc"},
        {"type": "template", "domain": "CV"},
    ]

    ids = [f"seed_{i}" for i in range(len(docs))]

    # Vérifie si déjà initialisée
    existing = collection.count()
    if existing > 0:
        print(f"[RAG] Base déjà initialisée ({existing} docs)")
        return

    collection.add(documents=docs, metadatas=metadatas, ids=ids)
    print(f"[RAG] ✅ Base initialisée avec {len(docs)} documents")