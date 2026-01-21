import os
from typing import Annotated, Sequence, TypedDict   
from langgraph.graph import StateGraph, START, END
from langchain.messages import ToolMessage, SystemMessage, AnyMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

API_KEY = os.getenv("API_KEY")

class AgentState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]

@tool
def add(a: int, b:int):
    """This is an addition function that adds two numbers together"""
    return a + b

@tool
def mult(a: int, b:int):
    """This is an multiplication function that multiply two numbers together"""
    return a * b

@tool
def sub(a: int, b:int):
    """This is an substraction function that subtracts two numbers together"""
    return a - b

tools = [add, mult, sub]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=API_KEY).bind_tools(tools=tools)

def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content="You are my AI assistant, please answer my query to the best of your ability.")
    response = model.invoke([system_prompt] + state["messages"])

    return {"messages": [response]}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"
    
graph = StateGraph(AgentState)
graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)

graph.set_entry_point("our_agent")
graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue":"tools",
        "end": END
    }
)

graph.add_edge("tools", "our_agent")

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if  isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages":[("user", "Add 23 + 1 then multiply the result by 2")]}
app.invoke(inputs)
# print_stream(app.stream(inputs, stream_mode="values"))

