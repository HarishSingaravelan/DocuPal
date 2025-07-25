#!/bin/bash
set -e

# Start Ollama server in background
ollama serve &

# Wait for server to be done
sleep 5

# Pull models
ollama pull llama3.2
ollama pull mxbai-embed-large

# Run your Python app
streamlit run /app/app.py --server.port=8501 --server.address=0.0.0.0
