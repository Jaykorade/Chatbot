from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import streamlit as st
import sqlite3

load_dotenv()


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    summary :str


llm = ChatOpenAI()
def format_messages(messages: list[BaseMessage]) -> str:
    return "\n".join([f"{msg.type.capitalize()}: {msg.content}" for msg in messages])

def summarize_conversation(state: ChatState):
    messages = state["messages"]
    prompt = [
        HumanMessage(content=(
            "Based on the following conversation, generate a short and relevant title or summary name for this chat:\n\n"
            f"{format_messages(messages)}"
        ))
    ]
    response = llm.invoke(prompt)
    return {"summary": response.content}

def chat_node(state: ChatState):
    # take user query from state
    messages = state['messages']
    # send to llm
    response = llm.invoke(messages)
    # response store state
    return {'messages': [response]}


conn = sqlite3.connect(database='chatbot.db',check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)
graph.add_node("summarize_node", summarize_conversation)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", "summarize_node")
graph.add_edge("summarize_node", END)
chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads =set()
    for ck in checkpointer.list(None):
        all_threads.add(ck.config['configurable']['thread_id'])

    return list(all_threads)