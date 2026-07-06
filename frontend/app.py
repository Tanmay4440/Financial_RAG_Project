import streamlit as st
import requests
import json
import pandas as pd
import base64
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Financial Report Assistant", page_icon="📈", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("📈 Financial Report Assistant (Local AI)")

with st.sidebar:
    st.header("Upload PDFs")
    uploaded_files = st.file_uploader("", type=["pdf"], accept_multiple_files=True)

    if st.button("Submit & Index", type="primary"):
        if uploaded_files:
            status_placeholder = st.empty()
            status_placeholder.info("Processing documents...")
            files_payload = [("files", (f.name, f.getvalue(), "application/pdf")) for f in uploaded_files]
            try:
                res = requests.post(f"{API_URL}/upload", files=files_payload, timeout=60)
                if res.status_code == 200:
                    status_placeholder.success("Indexed successfully!")
                else:
                    status_placeholder.error(f"Upload failed with status code {res.status_code}.")
            except requests.exceptions.RequestException:
                status_placeholder.error("Backend unreachable. Please verify your FastAPI terminal is running.")
                    
    st.divider()
    if st.button("Reset Session"):
        try:
            requests.delete(f"{API_URL}/reset")
            st.session_state.history = []
            st.success("Reset.")
        except:
            pass

    if st.session_state.history:
        st.divider()
        df = pd.DataFrame(st.session_state.history)
        b64 = base64.b64encode(df.to_csv(index=False).encode()).decode()
        st.markdown(f'<a href="data:file/csv;base64,{b64}" download="history.csv"><button>📥 Export CSV</button></a>', unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Display metadata subtext if available
        meta = []
        if "citations" in msg and msg["citations"]:
            meta.append(f"**Sources:** {msg['citations']}")
        if "response_time" in msg and msg["response_time"]:
            meta.append(f"⏱️ **Response Time:** {msg['response_time']}s")
        if meta:
            st.caption(" | ".join(meta))

if prompt := st.chat_input("Ask about your finances..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        citation_text = ""
        response_time = 0.0

        try:
            payload = {"question": prompt, "history": st.session_state.history[:-1]}
            with requests.post(f"{API_URL}/query", json=payload, stream=True) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if data["type"] == "citations":
                            cites = {f"{c['source']} (Pg. {c['page']})" for c in data["data"] if c['source']}
                            citation_text = ", ".join(cites)
                        elif data["type"] == "chunk":
                            full_response += data["data"]
                            message_placeholder.markdown(full_response + "▌")
                        elif data["type"] == "time":
                            response_time = data["data"]
                            
            message_placeholder.markdown(full_response)
            
            # Show the metrics bar right beneath the completed text
            meta = []
            if citation_text:
                meta.append(f"**Sources:** {citation_text}")
            meta.append(f"⏱️ **Response Time:** {response_time}s")
            st.caption(" | ".join(meta))

            st.session_state.history.append({
                "role": "assistant", 
                "content": full_response, 
                "citations": citation_text,
                "response_time": response_time
            })
        except Exception as e:
            st.error("Error communicating with backend.")