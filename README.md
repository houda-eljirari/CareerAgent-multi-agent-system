# CareerAgent — Système Multi-Agent Intelligent

> **Trouve ton stage, adapte ton CV, prépare ton entretien.**  
> Projet de Fin de Module — Master SDIA · ENSET Mohammedia · 2024-2025

---

## Présentation

**CareerAgent** est un écosystème multi-agent intelligent conçu pour accompagner les étudiants dans leur recherche de stage dans les domaines de l'IA, du Testing et du Backend. Le système orchestre 7 agents spécialisés via **LangGraph**, intègre un **RAG agentique** avec ChromaDB, et propose une interface web interactive développée avec **Streamlit**.

### Ce que fait CareerAgent

1. **Scrape** des offres de stage (mockées, 15 offres réalistes au Maroc)
2. **Analyse** et classe les offres selon le profil du candidat via RAG itératif
3. **Adapte** le CV avec un Prompt B optimisé ATS
4. **Valide** le CV adapté via 5 tests automatisés (Agent QA)
5. **Intègre** une validation humaine (Human-in-the-Loop)
6. **Identifie** les compétences manquantes (Gap Analyzer)
7. **Génère** 5 questions d'entretien ciblées

---

## Architecture

```
CareerAgent/
├── graph.py                  # Orchestrateur LangGraph principal
├── agents/
│   ├── analyste.py           # Agent RAG itératif (Membre 1)
│   ├── qa_agent.py           # Agent QA — 5 tests (Membre 1)
│   ├── scraper.py            # Agent Scraper — 15 offres (Membre 2)
│   ├── cv_adapter.py         # Agent CV Adapter Prompt B (Membre 2)
│   ├── gap_analyzer.py       # Agent Gap Analyzer (Membre 2)
│   └── entretien.py          # Agent Entretien Prep (Membre 2)
├── rag/
│   └── vector_store.py       # ChromaDB + embeddings
├── tools/
│   └── prompt_evaluation.py  # Test A/B Prompt A vs B
├── ui/
│   └── app.py                # Interface Streamlit (5 étapes)
├── data/
│   └── knowledge_base/       # Documents RAG
├── .env                      # Clés API (non versionné)
└── requirements.txt
```

### Flux LangGraph

```
[Supervisor] → [Scraper] → [Analyste RAG] → [Supervisor]
                                                  ↓
                                          [CV Adapter]
                                                  ↓
                                           [QA Agent]
                                          ↙         ↘
                                    PASS            FAIL
                                      ↓               ↓
                               [Human Loop]    [CV Adapter]
                              ↙          ↘
                          Validé       Refusé
                            ↓
                    [Gap Analyzer] → [Entretien] → END
```

---

## Installation

### Prérequis

- Python 3.10+
- [uv](https://astral.sh/uv) (recommandé) ou pip
- Git

### Étapes

```bash
# 1. Cloner le repo
git clone https://github.com/houda-eljirari/CareerAgent-multi-agent-system.git
cd CareerAgent-multi-agent-system

# 2. Créer l'environnement virtuel
uv venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Installer les dépendances
uv pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et ajouter ta clé API si disponible :
# ANTHROPIC_API_KEY=sk-ant-...

# 5. Initialiser la base ChromaDB
python -c "from rag.vector_store import seed_knowledge_base; seed_knowledge_base()"

# 6. Lancer l'application
streamlit run ui/app.py
```

---

## Utilisation

### Interface Web (Streamlit)

```bash
streamlit run ui/app.py
# → http://localhost:8501
```

**5 étapes dans l'interface :**

| Étape | Description |
|-------|-------------|
|  Profil | Upload CV PDF ou colle le texte + choix du domaine |
|  Offres | Visualise les offres classées par score ATS |
|  Adaptation | L'agent CV Adapter optimise ton CV pour l'offre |
|  Validation | Valide ou refuse le CV adapté (Human-in-the-Loop) |
|  Résultats | Gaps identifiés + questions d'entretien + téléchargement |

### Test A/B des Prompts

```bash
python tools/prompt_evaluation.py
```

---

## Les 7 Agents

| Agent | Rôle | Technologie |
|-------|------|-------------|
| **Supervisor** | Routing conditionnel entre agents | LangGraph |
| **Scraper** | 15 offres mockées filtrées par domaine | Python |
| **Analyste** | RAG itératif — 2 requêtes par offre | ChromaDB |
| **CV Adapter** | Adaptation ATS avec Prompt B optimisé | LLM / Fallback |
| **QA Agent** | 5 tests automatisés (ATS, Hallucination, Format...) | Python |
| **Gap Analyzer** | Compétences manquantes + plan 30/60/90j | LLM / Fallback |
| **Entretien** | 5 questions ciblées (technique + comportemental) | LLM / Fallback |

---

## Évaluation des Prompts (Test A/B)

| | Prompt A | Prompt B |
|--|---------|---------|
| Score moyen ATS | 60/100 | 65/100 |
| Hallucinations | 0 | 0 |
| Victoires | 0/5 | 5/5 |
| **Gain** | — | **+5 pts** |

> Le Prompt B utilise une structure ATS stricte en 5 sections avec intégration ciblée des mots-clés sans invention de compétences.

---

## Technologies

| Technologie | Usage |
|-------------|-------|
| **LangGraph** | Orchestration multi-agent + checkpoints |
| **ChromaDB** | Base vectorielle RAG |
| **Streamlit** | Interface web interactive |
| **pdfplumber** | Extraction texte depuis CV PDF |
| **sentence-transformers** | Embeddings locaux |
| **Python 3.12** | Langage principal |
| **uv** | Gestionnaire de paquets rapide |

---

