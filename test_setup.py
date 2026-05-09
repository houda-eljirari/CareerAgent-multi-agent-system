from dotenv import load_dotenv
import os

load_dotenv()

# Test 1 : clé API présente
api_key = os.getenv("GOOGLE_API_KEY")
print("✅ Clé Gemini trouvée !" if api_key else "❌ Clé API manquante dans .env")

# Test 2 : LangGraph importable
from langgraph.graph import StateGraph
print("✅ LangGraph importé !")

# Test 3 : ChromaDB importable
import chromadb
print("✅ ChromaDB importé !")

# Test 4 : Gemini accessible
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", google_api_key=api_key)
response = llm.invoke("Dis juste : setup ok")
print(f"✅ Gemini répond : {response.content}")

print("\n🎉 Setup Jour 1 terminé — prêt pour Jour 2 !")