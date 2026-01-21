from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict): 
    query: str
    result: str
    chart: str

def process_query(state: AgentState) -> AgentState:
    """Starts to precess the quert"""

    state['result'] = "Fine! I'm processing your query"
    return state

def generate_chart(state: AgentState) -> AgentState:
    """Generate the chart"""

    state["chart"] = "Chart generated successfully"

    return state

def decide_next_node(state: AgentState) -> str:
    """Check weather is necessary generate a chart or not"""

    if "chart" not in state["query"]:
        return "chart_is_not_necessary"

    return "chart_is_necessary"


graph = StateGraph(AgentState)

graph.add_node("process_query", process_query)
graph.add_node("generate_chart", generate_chart)
graph.add_node("chart_router", lambda state:state)

graph.add_edge(START, "process_query")
graph.add_edge("process_query", "chart_router")
graph.add_conditional_edges(    
    "chart_router",
    decide_next_node,
    {
        "chart_is_not_necessary": END,
        "chart_is_necessary": "generate_chart"
    }
)
graph.add_edge("generate_chart", END)

app = graph.compile()
result = app.invoke({"query": "Generate a chart for me."})

print(result)