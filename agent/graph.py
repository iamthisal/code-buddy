from langchain_groq import  ChatGroq
from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts import *
from state import *
from langgraph.constants import END
from langgraph.graph import StateGraph

load_dotenv()


llm = ChatGroq(model="llama-3.3-70b-versatile")










def planner_agent(state: dict) -> dict:
    user_prompt = state["user_prompt"]
    response = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    if response is None:
        raise ValueError("planner did not return a valid response")
    return {"plan" : response}


def architect_agent(state:dict) -> dict:
    plan : Plan = state["plan"]
    response = llm.with_structured_output(TaskPlan).invoke(architect_prompt(plan))
    if response is None:
        raise ValueError("Architect did not return a valid response")
   #adding the plan attribute for the state(Taskplan)
    response.plan = plan #without model config this would break

    return {"task_plan" : response}



graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect",architect_agent)
graph.add_edge("planner","architect")
graph.set_entry_point("planner")




agent = graph.compile()

user_prompt = "create a simple calculator web application"

result = agent.invoke({"user_prompt": user_prompt})
print(result)

