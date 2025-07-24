FROM ollama/ollama

RUN apt-get update && \
    apt-get install -y python3 python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

COPY app.py /app/app.py
COPY entrypoint.sh /entrypoint.sh
COPY ollama_chat.py /app/ollama_chat.py
COPY rag_utils.py /app/rag_utils.py
COPY requirements.txt /app/requirements.txt

RUN chmod +x /entrypoint.sh

WORKDIR /app

# Install Python dependencies from requirements.txt
RUN pip install --break-system-packages -r requirements.txt

# Override the default entrypoint set by ollama/ollama
ENTRYPOINT ["/entrypoint.sh"]
