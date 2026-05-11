# graph.py — Orchestrateur Principal CareerAgent (version finale)
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator
from dotenv import load_dotenv

load_dotenv()

# ── 1. AGENT STATE ────────────────────────────────────────────
class AgentState(TypedDict):
    cv_text:             str
    user_query:          str
    target_domain:       str
    job_offers:          list
    ranked_offers:       list
    selected_offer:      dict
    adapted_cv:          str
    gaps:                list
    interview_questions: list
    next_agent:          str
    human_validated:     bool
    human_feedback:      str
    qa_passed:           bool
    messages:            Annotated[list, operator.add]

# ── 2. IMPORT DES VRAIS AGENTS ────────────────────────────────
from agents.analyste     import analyste_node
from agents.qa_agent     import qa_agent_node
from agents.scraper      import scraper_node      # ← Membre 2
from agents.cv_adapter   import cv_adapter_node   # ← Membre 2
from agents.gap_analyzer import gap_analyzer_node # ← Membre 2
from agents.entretien    import entretien_node    # ← Membre 2

# ── 3. SUPERVISOR + HUMAN LOOP (restent dans graph.py) ───────
def supervisor_node(state: AgentState) -> AgentState:
    print(f"[SUPERVISOR] Requête : {state['user_query']}")
    query = state["user_query"].lower()

    if state.get("job_offers") and not state.get("ranked_offers"):
        next_a = "analyste"
    elif state.get("ranked_offers") and not state.get("adapted_cv"):
        next_a = "cv_adapter"
    elif state.get("job_offers") and not state.get("selected_offer"):
        next_a = "end"
    elif "offre" in query or "stage" in query or "cherche" in query:
        next_a = "scraper"
    elif "cv" in query or "adapter" in query:
        next_a = "cv_adapter"
    elif "entretien" in query:
        next_a = "entretien"
    else:
        next_a = "end"

    print(f"[SUPERVISOR] → routing vers : {next_a}")
    return {**state, "next_agent": next_a,
            "messages": [{"role": "supervisor", "content": f"routing → {next_a}"}]}

def human_loop_node(state: AgentState) -> AgentState:
    print("[HUMAN LOOP] ⚠️  En attente de validation humaine...")
    validated = state.get("human_validated", False)
    print(f"[HUMAN LOOP] Décision : {'✅ Validé' if validated else '❌ Refusé'}")
    return {**state,
            "messages": [{"role": "human",
            "content": f"{'approuvé' if validated else 'refusé'}"}]}

# ── 4. ROUTEURS ───────────────────────────────────────────────
def route_supervisor(state: AgentState) -> str:
    return state["next_agent"]

def route_after_qa(state: AgentState) -> str:
    return "human_loop" if state.get("qa_passed") else "cv_adapter"

def route_after_human(state: AgentState) -> str:
    return "gap_analyzer" if state.get("human_validated") else "cv_adapter"

# ── 5. CONSTRUCTION DU GRAPH ──────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor",   supervisor_node)
    graph.add_node("scraper",      scraper_node)
    graph.add_node("analyste",     analyste_node)
    graph.add_node("cv_adapter",   cv_adapter_node)
    graph.add_node("qa_agent",     qa_agent_node)
    graph.add_node("human_loop",   human_loop_node)
    graph.add_node("gap_analyzer", gap_analyzer_node)
    graph.add_node("entretien",    entretien_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor", route_supervisor,
        {"scraper": "scraper", "analyste": "analyste",
         "cv_adapter": "cv_adapter", "gap_analyzer": "gap_analyzer",
         "entretien": "entretien", "end": END}
    )

    graph.add_edge("scraper",    "analyste")
    graph.add_edge("analyste",   "supervisor")
    graph.add_edge("cv_adapter", "qa_agent")

    graph.add_conditional_edges(
        "qa_agent", route_after_qa,
        {"human_loop": "human_loop", "cv_adapter": "cv_adapter"}
    )
    graph.add_conditional_edges(
        "human_loop", route_after_human,
        {"gap_analyzer": "gap_analyzer", "cv_adapter": "cv_adapter"}
    )

    graph.add_edge("gap_analyzer", "entretien")
    graph.add_edge("entretien", END)

    memory = MemorySaver()
    return graph.compile(
        checkpointer=memory,
        interrupt_before=["human_loop"]
    )

app = build_graph()
print("✅ Graph CareerAgent v2 compilé avec succès !")