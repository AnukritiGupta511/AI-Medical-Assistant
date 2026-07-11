from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from app.core.config import settings

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
        # Using Local Persistent ChromaDB
        self.vector_store = Chroma(
            embedding_function=self.embeddings,
            persist_directory="./chroma_db"
        )
        
    def init_chroma(self):
        pass

    def add_documents(self, texts: list[str], metadatas: list[dict] = None):
        """Add new documents to the RAG vector store."""
        chunks = self.text_splitter.create_documents(texts, metadatas=metadatas)
        self.vector_store.add_documents(chunks)
        return len(chunks)
        
    def query(self, text: str, k: int = 3):
        """Query the vector store for relevant context."""
        return self.vector_store.similarity_search(text, k=k)

rag_service = RAGService()
