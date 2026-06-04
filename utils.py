import fitz  # PyMuPDF
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text from uploaded PDF bytes."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    return text

def get_mmr_retriever(text: str, persist_dir="pdf_chroma_db"):
    """Chunks text, embeds it, and returns an MMR-optimized retriever."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = [Document(page_content=chunk) for chunk in splitter.split_text(text)]

    # Use a high-quality embedding model suitable for local inference
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    vectordb = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
    vectordb.persist()
    
    # UPGRADE: Using Maximal Marginal Relevance (MMR)
    # Fetches 20 documents, but mathematically selects the 5 most diverse ones
    return vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 20})