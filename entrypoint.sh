#!/bin/bash
set -e

echo "Starting Ollama..."
# Start Ollama server in background
ollama serve &

# Wait for server to be ready
sleep 5

echo "Pulling models..."
# Pull models
ollama pull llama3.2
ollama pull nomic-embed-text

echo "Starting FastAPI Backend..."
# Run the FastAPI backend using Uvicorn in the background
uvicorn api:app --host 0.0.0.0 --port 8000 &

# Wait a moment for FastAPI to initialize
sleep 3

echo "Starting Streamlit Frontend..."
# Run the Streamlit frontend
streamlit run app.py --server.port=8501 --server.address=0.0.0.0