
from langchain_groq import  ChatGroq
from dotenv import load_dotenv
import sys
import os

from langgraph.prebuilt import create_react_agent

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts import *
from state import *
from langgraph.constants import END
from langgraph.graph import StateGraph
from langchain_core.globals import set_verbose, set_debug
from agent.tools import  *


load_dotenv()


set_debug(True)
set_verbose(True)

llm = ChatGroq(model="llama-3.3-70b-versatile")


def planner_agent(state: dict) -> dict:
    user_prompt = state["user_prompt"]
    response = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    if response is None:
        raise ValueError("planner did not return a valid response")
    response.user_prompt = user_prompt

    return {"plan" : response}


def architect_agent(state:dict) -> dict:
    plan : Plan = state["plan"]
    response = llm.with_structured_output(TaskPlan).invoke(architect_prompt(plan))
    if response is None:
        raise ValueError("Architect did not return a valid response")
   #adding the plan attribute for the state(Taskplan)
    response.plan = plan #without model config this would break

    return {"task_plan" : response}

def coder_agent(state: dict) -> dict:
    coder_state:CoderState =  state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(

            task_plan=state["task_plan"],current_step_index=0

        )

    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_index >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = steps[coder_state.current_step_index]

    existing_content = read_file.run(current_task.filepath)

    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )

    system_prompt = coder_system_prompt()


    #response =  llm.invoke(system_prompt + user_prompt)


    coder_tools = [read_file, write_files, list_files, get_current_directory]
    react_agent = create_react_agent(llm,coder_tools)
    react_agent.invoke({"messages" : [{"role":"system", "content": system_prompt}
                                      ,{"role":"user", "content": user_prompt},]})


    coder_state.current_step_index += 1
    return {"coder_state" : coder_state}




graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect",architect_agent)
graph.add_node("coder", coder_agent)
graph.add_edge("planner","architect")
graph.add_edge("architect","coder")

graph.add_conditional_edges(
    "coder",
    lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"}
)


graph.set_entry_point("planner")


agent = graph.compile()

user_prompt = "create a simple calculator web application"

result = agent.invoke({"user_prompt": user_prompt})
print(result)

