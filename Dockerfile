FROM ollama/ollama

RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

# Copy all decoupled architecture files
COPY api.py /app/api.py
COPY agent.py /app/agent.py
COPY utils.py /app/utils.py
COPY app.py /app/app.py
COPY entrypoint.sh /entrypoint.sh
COPY requirements.txt /app/requirements.txt

RUN chmod +x /entrypoint.sh

WORKDIR /app

# Install Python dependencies
RUN pip install --break-system-packages -r requirements.txt

# Expose ports: FastAPI (8000), Streamlit (8501), Ollama (11434)
EXPOSE 8000
EXPOSE 8501
EXPOSE 11434

# Override the default entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD []