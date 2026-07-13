from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        # Using FAISS in-memory store for Vercel stateless deployment
        # Note: Vector store clears on each serverless spin-up.
        self.vector_store = None
        
    def init_chroma(self):
        pass

    def add_documents(self, texts: list[str], metadatas: list[dict] = None):
        """Add new documents to the RAG vector store."""
        chunks = self.text_splitter.create_documents(texts, metadatas=metadatas)
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vector_store.add_documents(chunks)
        return len(chunks)
        
    def query(self, text: str, k: int = 3):
        """Query the vector store for relevant context."""
        if self.vector_store is None:
            return []
        return self.vector_store.similarity_search(text, k=k)

rag_service = RAGService()
