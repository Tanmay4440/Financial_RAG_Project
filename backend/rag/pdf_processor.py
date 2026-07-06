import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from backend.config import settings

def process_pdf(file_path: str, filename: str):
    doc = fitz.open(file_path)
    documents = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text") 
        if text.strip():
            documents.append(Document(
                page_content=text,
                metadata={"source": filename, "page": page_num + 1}
            ))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    return splitter.split_documents(documents)