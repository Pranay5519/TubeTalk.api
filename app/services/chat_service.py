from typing import TypedDict, Annotated
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from app.models.chatbot_model import AnsandTime

# ---------- Chat State ----------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class ChatbotService:
    """
    Chatbot service that uses Gemini 2.5 Flash with structured output.
    Keeps chat state in memory and answers questions using transcript context.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash", temperature: float = 0):
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature

        # LLM with API key
        self.llm = ChatGoogleGenerativeAI(model=self.model_name,
                                          temperature=self.temperature,
                                          api_key=self.api_key)

        # Structured output
        self.structured_model = self.llm.with_structured_output(AnsandTime)

        # System message
        self.system_message = SystemMessage(
            content="You are the YouTuber from the video, answering using only transcript context."
        )

        # In-memory checkpointer
        self.checkpointer = MemorySaver()

    def _chat_node(self, state: ChatState, retriever):
        """
        Internal node: retrieves context and generates AI response.
        """
        user_question = state["messages"][-1].content
        retrieved_chunks = retriever.invoke(user_question)

        context = "\n\n".join(doc.page_content for doc in retrieved_chunks)

        messages = [
            self.system_message,
            SystemMessage(content=f"Transcript:\n{context}"),
            HumanMessage(content=user_question),
        ]

        response = self.structured_model.invoke(messages)
        ai_text = f"{' '.join(response.answer)}\nTimestamp: {response.timestamps}"

        return {"messages": [state["messages"][-1], AIMessage(content=ai_text)]}

    def build_chatbot(self, retriever):
        """
        Build and return the chatbot graph with memory checkpointing.
        """
        graph = StateGraph(ChatState)

        graph.add_node("chat_node", lambda state: self._chat_node(state, retriever))
        graph.add_edge(START, "chat_node")
        graph.add_edge("chat_node", END)

        return graph.compile(checkpointer=self.checkpointer)
