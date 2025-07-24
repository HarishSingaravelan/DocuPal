from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import fitz  # PyMuPDF

# 1. Extract text from PDF
def extract_text_from_pdf(file) -> str:
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# 2. Create ChromaDB from PDF text
def create_chroma_from_text(text, persist_dir="pdf_chroma_db"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = [Document(page_content=chunk) for chunk in splitter.split_text(text)]

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")  # or 'nomic-embed-text'
    vectordb = Chroma.from_documents(docs, embeddings, persist_directory=None)
    vectordb.persist()
    return vectordb.as_retriever(search_kwargs={"k": 5})