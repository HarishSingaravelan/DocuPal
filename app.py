import streamlit as st
from rag_utils import extract_text_from_pdf, create_chroma_from_text
from ollama_chat import ask_ollama
import time

# --- Page Configuration ---
st.set_page_config(page_title="PDF Q&A", page_icon="📄", layout="centered")

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
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.markdown("<div class='big-title'>📄🔍 DocuPal</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Upload a PDF and chat with it using local LLM and vector store!</div>", unsafe_allow_html=True)

# --- File Uploader ---
uploaded_file = st.file_uploader("📤 Upload a PDF", type=["pdf"])

# --- PDF Processing ---
if uploaded_file:
    if "last_uploaded" not in st.session_state or st.session_state.last_uploaded != uploaded_file.name:
        with st.spinner("🔄 Extracting and indexing text..."):
            text = extract_text_from_pdf(uploaded_file)
            retriever = create_chroma_from_text(text)

            # Store in session state
            st.session_state.retriever = retriever
            st.session_state.pdf_text = text
            st.session_state.chat_history = []
            st.session_state.last_uploaded = uploaded_file.name

        st.success("✅ PDF processed. Start asking questions below!")

# --- Chat Interface ---
if "retriever" in st.session_state:
    st.markdown("### 💬 Ask a question about the uploaded PDF")

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat['content'])

    if prompt := st.chat_input("Ask something about the PDF..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.spinner("🤖 Thinking..."):
            docs = st.session_state.retriever.invoke(prompt)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            answer = ask_ollama(prompt, context)

            full_response = ""
            message_placeholder = st.empty()

            for chunk in answer.split():
                full_response += chunk + " "
                time.sleep(0.04)
                message_placeholder.markdown(f"{full_response}▌")

            message_placeholder.markdown(full_response)

        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
