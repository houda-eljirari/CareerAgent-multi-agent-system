# test_rag.py — Test de la base RAG
from rag.vector_store import seed_knowledge_base, get_retriever

print("Initialisation de la base RAG...")
seed_knowledge_base()

print("\nTest requête 1 : compétences IA")
retriever = get_retriever()
docs = retriever("compétences requises stage IA Python")
for d in docs:
    print(f"  → [{d['metadata']['type']}] {d['page_content'][:80]}...")

print("\nTest requête 2 : entreprises Maroc")
docs2 = retriever("entreprises tech Maroc recrutement")
for d in docs2:
    print(f"  → [{d['metadata']['type']}] {d['page_content'][:80]}...")

print("\n✅ RAG fonctionnel !")