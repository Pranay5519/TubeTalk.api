from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from pydantic import BaseModel, Field
from app.models.chatbot_model import AnsandTime

# ---------- LLM ----------
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
structured_model = model.with_structured_output(AnsandTime)

system_message = SystemMessage(content="You are the YouTuber from the video, answering using only transcript context.")


# ---------- Chat State ----------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ---------- Chat Node ----------
def chat_node(state: ChatState, retriever):
    user_question = state["messages"][-1].content
    retrieved_chunks = retriever.invoke(user_question)

    context = "\n\n".join(doc.page_content for doc in retrieved_chunks)

    messages = [
        system_message,
        SystemMessage(content=f"Transcript:\n{context}"),
        HumanMessage(content=user_question),
    ]

    response = structured_model.invoke(messages)
    ai_text = f"{' '.join(response.answer)}\nTimestamp: {response.timestamps}"

    return {"messages": [state["messages"][-1], AIMessage(content=ai_text)]}


# ---------- In-Memory Checkpointer ----------
checkpointer = MemorySaver()


# ---------- Build Chatbot ----------
def build_chatbot(retriever):
    graph = StateGraph(ChatState)

    def _chat_node(state: ChatState):
        return chat_node(state, retriever)

    graph.add_node("chat_node", _chat_node)
    graph.add_edge(START, "chat_node")
    graph.add_edge("chat_node", END)

    return graph.compile(checkpointer=checkpointer)
