from langchain_community.chat_models import ChatOllama
from backend.config import settings

_llm_instance = None

def get_llm():
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = ChatOllama(
            model=settings.MODEL_NAME,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.1
        )
    return _llm_instance