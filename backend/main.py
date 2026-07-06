import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import os
import shutil
import json

from backend.config import settings
from backend.rag.pdf_processor import process_pdf
from backend.rag.vector_store import vs_manager
from backend.rag.llm import get_llm

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(title="Financial RAG API")

class QueryRequest(BaseModel):
    question: str
    history: List[dict] = []

@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDFs allowed.")
        
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        chunks = process_pdf(file_path, file.filename)
        vs_manager.add_documents(chunks)
        
    return {"message": "Success"}

@app.post("/query")
async def query(request: QueryRequest):
    retriever = vs_manager.get_retriever()
    if not retriever:
        raise HTTPException(status_code=400, detail="No documents indexed. Please upload PDFs first.")

    try:
        llm = get_llm()
        
        # === HOP 1: Primary Retrieval ===
        # Retrieve initial documents based on the user's raw question
        hop1_docs = retriever.invoke(request.question)
        hop1_context = "\n".join([d.page_content for d in hop1_docs])
        
        # === HOP 2: Query Decomposition & Secondary Retrieval ===
        # Ask the LLM what else it needs to look up to accurately answer the question
        hop2_prompt = f"""You are a financial analyst. Review this question and the initial text found.
Question: {request.question}
Initial Text Found: {hop1_context}

Determine what missing or related financial figure, row, or section from the statement is still needed to fully answer this question (e.g., if looking for a ratio, what is the other component? If looking for growth, what is the prior year's data?).
Output ONLY a short search phrase (maximum 5 words) to look up this missing information. Do not write full sentences.
Search Phrase:"""
        
        # Generate the secondary search query using the local LLM
        hop2_query_response = llm.invoke(hop2_prompt)
        hop2_query = hop2_query_response.content.strip()
        
        # Execute the second hop if the LLM generated a useful search query
        all_docs = list(hop1_docs)
        if hop2_query and len(hop2_query) > 2:
            hop2_docs = retriever.invoke(hop2_query)
            # Combine unique documents from both hops to prevent duplicate context
            seen_contents = set(d.page_content for d in all_docs)
            for d in hop2_docs:
                if d.page_content not in seen_contents:
                    all_docs.append(d)
        
        # === Final Synthesis ===
        # Format the combined context string and build citations
        context_str = "\n\n".join([
            f"[Source: {d.metadata.get('source')} | Page: {d.metadata.get('page')}]\n{d.page_content}"
            for d in all_docs
        ])
        citations = [{"source": d.metadata.get('source'), "page": d.metadata.get('page')} for d in all_docs]

        system_prompt = """You are an expert Financial Analyst. Answer ONLY using the provided Context. 
If the answer is not in the context, say "The provided documents do not contain this information." 
Preserve all numerical values exactly.
Context:
{context}"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

        chat_history = []
        for msg in request.history:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))

        chain = prompt | llm

        async def generate_response():
            import time
            start_time = time.time()
            
            yield json.dumps({"type": "citations", "data": citations}) + "\n"
            
            async for chunk in chain.astream({
                "context": context_str,
                "chat_history": chat_history,
                "question": request.question
            }):
                yield json.dumps({"type": "chunk", "data": chunk.content}) + "\n"
                
            elapsed_time = round(time.time() - start_time, 2)
            yield json.dumps({"type": "time", "data": elapsed_time}) + "\n"

        return StreamingResponse(generate_response(), media_type="application/x-ndjson")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.delete("/reset")
async def reset():
    vs_manager.clear()
    for f in os.listdir(settings.UPLOAD_DIR):
        os.remove(os.path.join(settings.UPLOAD_DIR, f))
    return {"message": "Reset complete."}