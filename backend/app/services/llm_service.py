from typing import Dict, Any, TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from app.core.config import settings
from app.services.rag_service import rag_service

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    context: str

class LLMService:
    def __init__(self):
        # We initialize the model with the API key from settings
        # This will fail gracefully if the key is empty during init
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview", 
            temperature=0.0,
            api_key=settings.OPENAI_API_KEY or "dummy-key-for-build"
        )
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)
        
        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()

    def _retrieve_node(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve context using RAG service."""
        last_message = state["messages"][-1].content
        
        # Query ChromaDB via our rag_service
        # For MVP, we simulate retrieval if chroma isn't populated
        docs = rag_service.query(last_message, k=3)
        context = "\n".join([doc.page_content for doc in docs]) if docs else "No specific medical guidelines retrieved from local DB."
        
        return {"context": context}

    def _generate_node(self, state: AgentState) -> Dict[str, Any]:
        """Generate response grounded in retrieved context."""
        context = state["context"]
        messages = state["messages"]
        
        system_prompt = SystemMessage(content=f"""
You are an AI Medical Assistant designed to help users understand their health information.
You MUST clearly state that you are for Educational Purposes Only and are not a substitute for professional medical advice.

Use the following trusted context to answer the user's query. If the answer is not in the context, clearly state that you do not have enough specific medical information and advise consulting a doctor.

Retrieved Context:
{context}
        """)
        
        # Prepend system prompt to the conversation
        conversation = [system_prompt] + list(messages)
        
        # Invoke LLM
        response = self.llm.invoke(conversation)
        
        return {"messages": [response]}

    def process_query(self, query: str, history: list[Dict[str, str]] = None) -> Dict[str, Any]:
        """Main entry point to process a user query."""
        messages = []
        if history:
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
                    
        messages.append(HumanMessage(content=query))
        
        # Run graph
        result = self.graph.invoke({"messages": messages, "context": ""})
        
        ai_message = result["messages"][-1].content
        
        return {
            "response": ai_message,
            "citations": ["RAG Context Used"],
            "confidence_score": 0.90 # Simulated
        }

llm_service = LLMService()
