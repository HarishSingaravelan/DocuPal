# import requests

# def ask_ollama(prompt):



#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={"model": "llama3.2", "prompt": prompt, "stream": False}
#     )
#     return response.json().get("response", "No response from model.")

# if __name__ == "__main__":
#     while True:
#         user_input = input("Enter your question: ")
#         if user_input.lower() == "exit":
#             break
#         ask_ollama(user_input)


from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

# Load and split PDF
def load_pdf_and_store(file_path: str, persist_directory="db"):
    loader = PyPDFLoader(file_path)
    pages = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(pages)

    embedding = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=persist_directory
    )
    vectordb.persist()
    return vectordb

# Setup prompt and model
template = """
You are a helpful assistant that answers questions based on the given context.

Context:
{context}

Question:
{question}
"""
prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(model="llama3.2")

# QA Function
def ask_ollama(question, context):
    # retriever = vectordb.as_retriever()
    # docs = retriever.invoke(question)
    # context = "\n\n".join([doc.page_content for doc in docs])

    chain = prompt | model
    return chain.invoke({"context": context, "question": question})

