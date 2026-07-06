from langchain_huggingface import HuggingFaceEmbeddings
from backend.config import settings

_embeddings_instance = None

def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    return _embeddings_instance