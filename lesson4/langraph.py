# The code snippet you provided is importing the necessary modules and setting up the environment for
# using the OpenAI API. Here's a breakdown of each line:

###
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import os
import requests
from datetime import datetime
from secret_key import openai_key 

###
os.environ["OPENAI_API_KEY"] = openai_key  

url="https://jsonplaceholder.typicode.com/posts"
class State(TypedDict):
    messages: Annotated[list, add_messages]


#"Fetch posts from a placeholder API"
@tool()
def fetch_posts_by_user(id: int):
    """Fetch posts by user ID from a placeholder API."""
    response = requests.get(f'https://jsonplaceholder.typicode.com/posts/?userId={id}')
    if response.status_code == 200:
        response = response.json()
        print(response)
        return response
    else:
        return {"error": "Failed to fetch posts"}
        
        
tools=[fetch_posts_by_user]
tool_node= ToolNode(tools)
llm_tools= ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo").bind_tools(tools)
llm=ChatOpenAI(temperature=0.5, model="gpt-3.5-turbo")  
 
SYSTEM_PROMPT = "You are a helpful assistant that fetches posts from a placeholder API and translates them to English summarize and export the reponse to md file."
def run_llm(state:State) :
    """Run the LLM with the given state."""
    messages = state["messages"]
    full_messege=[HumanMessage(content=SYSTEM_PROMPT)]+messages
    response = llm_tools.invoke(full_messege)
   # print(response.content)
    return {"messages":[response]}

def translate_summary_post(state:State):
    """Translate a post to English."""
    print("tarnslate node")
    last_meesage = state["messages"][-1].content
    prompt = f"Given the following blog translate each title and body of the post to english and then suumarize them return on the follow format title: pose: : {last_meesage}"
    #use the llm without bind tool to avoid recursive tools call
    response = llm.invoke([HumanMessage(content=prompt)])
   # print(response.content)
    return {"messages":[response]}

def format(state:State):
    print("summarize node")
    """Summarize a list of posts."""
    final_messages = state["messages"][-1].content
    return {"messages": [HumanMessage(content=f'📕 final report:\n{final_messages}')]}


def generate_md_file(state:State) -> None:
    """Generate a markdown file from the posts."""
    first_message = state["messages"][0].content
    user_id = first_message.split("user ")[-1]
    filename = f"posts_by_user_{user_id}.md"
    md_content = f"""
    **Posts by User {user_id}**
    generated report by langraph :
    {state["messages"][-1].content}

    """ 
    with open(filename, "w", encoding="utf-8") as f:
            f.write(md_content)
#Create a state graph to manage the flow of the application

graph_builder = StateGraph(State)
graph_builder.add_node("intial_fetch", run_llm)
graph_builder.add_node("tools",tool_node)
graph_builder.add_node("translate_summary_post",translate_summary_post)
graph_builder.add_node("printed_format", format)
graph_builder.add_node("generate_md_file", generate_md_file)
graph_builder.add_edge(START, "intial_fetch") 
graph_builder.add_conditional_edges("intial_fetch", tools_condition)
graph_builder.add_edge("tools", "translate_summary_post")
graph_builder.add_edge("translate_summary_post", "printed_format")
graph_builder.add_edge("printed_format", "generate_md_file")
graph_builder.add_edge("generate_md_file", END)
graph=graph_builder.compile()


user_id = input("enter user id to fetch posts by user: ")
result = graph.invoke({"messages": [HumanMessage(content=f"Fetch posts for user {user_id}")]})
print("ai agents Result\n:", result["messages"][-1].content)
print("##################################################")
for i, message in enumerate(result["messages"]):
        print(f"Message {i}: {message.content}")
   
# Try to extract posts from the result and write to markdown

