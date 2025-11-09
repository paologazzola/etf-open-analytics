# Small, CPU-only image
FROM python:3.11-slim

WORKDIR /app
COPY chatbot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY chatbot /app
ENV PORT=8080
EXPOSE 8080

# Environment defaults (override in Helm values)
ENV LLM_BACKEND=ollama
ENV LLM_MODEL=phi3:mini
ENV LLM_URL=http://ollama:11434
ENV PORTFOLIO_EVAL_URL=http://portfolio-evaluator:8000
ENV PORTFOLIO_EVAL_PATH=/evaluate

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8080"]
