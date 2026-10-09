from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from config import FAISS_DIRECTORY


_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def create_index(documents: list[Document]) -> FAISS:
    """Create and persist a FAISS index."""
    vector_store = FAISS.from_documents(
        documents=documents,
        embedding=_embeddings,
    )
    vector_store.save_local(FAISS_DIRECTORY)
    return vector_store


def load_index() -> FAISS:
    """Load an existing FAISS index."""
    return FAISS.load_local(
        FAISS_DIRECTORY,
        _embeddings,
        allow_dangerous_deserialization=True,
    )


def search(query: str, k: int = 5) -> list[Document]:
    """Find the most relevant documents."""
    vector_store = load_index()
    return vector_store.similarity_search(query, k=k)


def add_documents(documents: list[Document]) -> None:
    """Add documents to an existing index and persist changes."""
    vector_store = load_index()
    vector_store.add_documents(documents)
    vector_store.save_local(FAISS_DIRECTORY)