# 📈 Financial Statement Assistant (Local Multi-Hop RAG)

A completely local, privacy-preserving Retrieval-Augmented Generation (RAG) application designed specifically for analyzing complex financial documents. 

Built with a decoupled architecture (FastAPI backend + Streamlit frontend), this assistant runs entirely on your local hardware without relying on cloud APIs. It is optimized to run smoothly on lower-end GPUs.

## ✨ Features

* **100% Local Privacy:** No API keys required. Your financial documents never leave your machine.
* **Multi-Hop Retrieval:** Uses intelligent query decomposition. If you ask a complex question, the AI performs a primary search, identifies missing context (like prior-year data), and performs a secondary search before answering.
* **Hardware Optimized:** Leverages Llama 3.2 (3B) and lightweight Hugging Face embeddings to fit comfortably within 4GB of VRAM.
* **Advanced PDF Processing:** Uses `PyMuPDF` to cleanly extract difficult financial tables and multi-column layouts.
* **Source Citations:** Every response includes direct citations (Document Name & Page Number) to prevent hallucinations.
* **Performance Metrics:** Tracks and displays exact LLM generation/response times for every query.
* **Session Export:** Download your entire financial analysis conversation history as a CSV file.

## 🏗️ Architecture

* **Frontend:** Streamlit
* **Backend:** FastAPI
* **LLM Engine:** Ollama (`llama3.2` 3B)
* **Embedding Model:** HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
* **Vector Database:** FAISS
* **PDF Parser:** PyMuPDF (`fitz`)

## 📂 Project Structure

```text
Financial_RAG_Project/
├── backend/
│   ├── rag/
│   │   ├── embeddings.py     # GPU-accelerated HuggingFace embeddings
│   │   ├── llm.py            # Ollama connection & persistent VRAM loading
│   │   ├── pdf_processor.py  # PyMuPDF extraction & chunking
│   │   └── vector_store.py   # FAISS MMR retrieval
│   ├── utils/
│   │   └── logger.py         # Application logging
│   ├── config.py             # Environment configurations
│   └── main.py               # FastAPI endpoints & Multi-Hop logic
├── frontend/
│   └── app.py                # Streamlit user interface
├── logs/                     # Auto-generated backend logs
├── uploads/                  # Temporary storage for uploaded PDFs
├── vector_store/             # Persisted FAISS index files
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Author
Tanmay Gaurav

## Github
Tanmay4440
