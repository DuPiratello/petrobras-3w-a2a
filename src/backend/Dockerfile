FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

ENV OLLAMA_URL=http://host.containers.internal:11434/v1/completions

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
