from langchain_community.vectorstores import FAISS
from backend.rag.embeddings import get_embeddings
from backend.config import settings
from backend.utils.logger import logger
import os
import shutil

class VectorStoreManager:
    def __init__(self):
        self.persist_dir = settings.VECTOR_STORE_DIR
        self.embeddings = get_embeddings()
        self.db = None
        self.load()

    def load(self):
        if os.path.exists(os.path.join(self.persist_dir, "index.faiss")):
            try:
                self.db = FAISS.load_local(self.persist_dir, self.embeddings, allow_dangerous_deserialization=True)
            except Exception:
                self.db = None
        else:
            self.db = None

    def add_documents(self, docs):
        if self.db is None:
            self.db = FAISS.from_documents(docs, self.embeddings)
        else:
            self.db.add_documents(docs)
        self.db.save_local(self.persist_dir)

    def get_retriever(self, k=5, fetch_k=20):
        if not self.db:
            return None
        return self.db.as_retriever(search_type="mmr", search_kwargs={"k": k, "fetch_k": fetch_k})

    def clear(self):
        self.db = None
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
            os.makedirs(self.persist_dir)

vs_manager = VectorStoreManager()