from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
from utils import extract_text_from_pdf, get_mmr_retriever
from agent import build_rag_agent

app = FastAPI(title="DocuPal Agentic API")

# Global variables to store our retriever and compiled agent in memory for this session
current_retriever = None
rag_agent = None

# Pydantic schemas for request validation
class ChatRequest(BaseModel):
    question: str
    chat_history: List[Dict[str, str]] = [] # Expected format: [{"role": "user", "content": "hi"}]

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global current_retriever, rag_agent
    try:
        # 1. Read bytes safely
        file_bytes = await file.read()
        
        # 2. Extract and embed using MMR
        text = extract_text_from_pdf(file_bytes)
        current_retriever = get_mmr_retriever(text)
        
        # 3. Build the LangGraph agent
        rag_agent = build_rag_agent(current_retriever)
        
        return {"status": "success", "message": f"Document '{file.filename}' processed and Agent is ready."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    global rag_agent
    if not rag_agent:
        raise HTTPException(status_code=400, detail="Please upload a document first.")
    
    # Initial state for the LangGraph workflow
    inputs = {
        "question": request.question,
        "chat_history": request.chat_history,
        "retries": 0
    }
    
    # Run the agentic workflow
    final_state = rag_agent.invoke(inputs)
    
    return {"answer": final_state["generation"]}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)