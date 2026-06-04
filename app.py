import streamlit as st
import requests

# --- API Configuration ---
API_URL = "http://localhost:8000"

# --- Page Configuration ---
st.set_page_config(page_title="PDF Q&A Agent", page_icon="📄", layout="centered")

# --- Custom Styling ---
st.markdown(
    """
    <style>
        .big-title {
            font-size: 2.5em !important;
            font-weight: 800;
            color: #1F4E79;
        }
        .sub-header {
            font-size: 1.2em;
            margin-bottom: 20px;
            color: #444;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.markdown("<div class='big-title'>📄🔍 DocuPal Agent</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Upload a PDF and chat with our Agentic LLM Backend!</div>", unsafe_allow_html=True)

# --- File Uploader ---
uploaded_file = st.file_uploader("📤 Upload a PDF", type=["pdf"])

# --- PDF Processing ---
if uploaded_file:
    if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
        with st.spinner("🔄 Sending document to backend for Agentic processing (MMR Indexing)..."):
            
            # Send the file to the FastAPI backend
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            response = requests.post(f"{API_URL}/upload", files=files)
            
            if response.status_code == 200:
                st.session_state.backend_ready = True
                st.session_state.chat_history = []
                st.session_state.last_uploaded = uploaded_file.name
                st.success("✅ PDF processed by the backend. The Agent is ready!")
            else:
                st.error(f"❌ Error processing PDF: {response.text}")

# --- Chat Interface ---
if st.session_state.get("backend_ready"):
    st.markdown("### 💬 Ask a question about the uploaded PDF")

    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat['content'])

    # Handle new user input
    if prompt := st.chat_input("Ask something about the PDF..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        # Append user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.spinner("🤖 Agent is thinking (Retrieving, Grading, Generating)..."):
            # Send the question and chat history to the FastAPI backend
            payload = {
                "question": prompt,
                "chat_history": st.session_state.chat_history[:-1] # Send history excluding current prompt
            }
            chat_response = requests.post(f"{API_URL}/chat", json=payload)
            
            if chat_response.status_code == 200:
                answer = chat_response.json().get("answer", "No answer generated.")
            else:
                answer = f"Error from backend: {chat_response.text}"

        # Display and store assistant response
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})