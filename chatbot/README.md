# 🧠 ETF Chatbot (Local RAG Assistant)

This module adds an **intelligent assistant** to your [ETF Open Analytics](../README.md) project.  
It runs **entirely offline**, uses only **open-source** libraries, and requires **no GPU**.

The chatbot can:
- 💬 **Answer questions** about the project using RAG (Retrieval-Augmented Generation).
- 📊 **Evaluate ETF portfolios** when you provide ISINs and investment amounts, using the trained model `risk_model.pkl` and your PostgreSQL data.

Everything runs locally on CPU — ideal for privacy, reproducibility, and experimentation.

---

## ⚙️ Folder structure

```
chatbot/
├─ README.md                 ← this file
├─ .env.example
├─ requirements.txt
├─ main.py                   ← FastAPI entrypoint
└─ modules/
   ├─ ingest.py              ← builds vector DB from docs
   ├─ rag.py                 ← retrieval-augmented generation logic
   ├─ llm.py                 ← wrapper for Ollama or llama-cpp
   ├─ embed_store.py         ← embeddings + Chroma persistence
   ├─ router.py              ← intent detection / ISIN parser
   ├─ portfolio_tool.py      ← loads DB + risk_model.pkl
   └─ utils.py
```

Your trained model should exist at:
```
portfolio_evaluator/models/risk_model.pkl
```

---

## 🚀 Quick start

### 1. Environment setup
```bash
cd etf-open-analytics/chatbot
cp .env.example .env
```

Edit `.env`:
```ini
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/etf_db
OLLAMA_HOST=http://10.10.10.40:11434
LLM_MODEL_NAME=phi3:mini        # or llama3.1:8b-instruct-q4_K_M
RAG_COLLECTION=etf_docs
CHROMA_PERSIST_DIR=.chroma
EMBEDDING_MODEL=intfloat/e5-small-v2
```

> You can point `OLLAMA_HOST` to any reachable Ollama instance.  
> If you prefer everything local, llama-cpp will run the GGUF model directly on CPU.

---

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

---

### 3. Build the local knowledge base
The ingestion script automatically scans:
- the main project README (`../README.md`)
- the `portfolio_evaluator/README.md`
- and this chatbot’s own README (`./README.md`)

To (re)build the embeddings:
```bash
python -m modules.ingest
```

Example output:
```
Indexed 3 documents (125 chunks total)
```

This creates a persistent Chroma store under `.chroma/`.

---

### 4. Run the API
```bash
uvicorn main:app --reload
```
Then open [http://localhost:8000/docs](http://localhost:8000/docs)  
and test `/chat`.

---

## 💬 Example requests

### Portfolio evaluation
```bash
curl.exe -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{""message"": ""Evaluate this portfolio: 10000 on CH1129538448 and 2000 on IE00BK5BQV03""}"
```

Example response:
```json
{
  "type": "portfolio_risk",
  "result": {
    "risk_score": 0.27,
    "features": {"volatility": 0.19, "sharpe": 0.73},
    "weights": {"CH1129538448": 0.83, "IE00BK5BQV03": 0.17}
  }
}
```

### General RAG question
```bash
curl.exe -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d "{""message"": ""What is max drawdown and how is it used in this project?""}"
```

Expected response:
```json
{
  "type": "rag",
  "answer": "Max drawdown represents the largest peak-to-trough loss observed in an ETF...",
  "sources": [
    {"path": "../README.md"},
    {"path": "portfolio_evaluator/README.md"}
  ]
}
```

> ⚠️ If you get `"LLM error: Extra data..."`, the model returned invalid JSON.
> This is harmless — it means the text answer was produced, but parsing failed.
> Smaller models like `phi3:mini` sometimes add formatting tokens;  
> larger ones (`llama3.1:8b-instruct-q4_K_M`) tend to output cleaner text.

---

## 🧩 Internal workflow

1. **Router** (`router.py`) checks whether the message contains ISINs and numeric amounts.  
   - If yes → portfolio evaluation path.  
   - If no → RAG path.
2. **Portfolio path:**  
   - Loads ETF data from PostgreSQL.  
   - Normalizes features with the `risk_model.pkl`’s scaler.  
   - Predicts portfolio risk using `RandomForestRegressor`.
3. **RAG path:**  
   - Embeds the query using `sentence-transformers`.  
   - Retrieves top-K relevant chunks from Chroma.  
   - Builds a context prompt.  
   - Sends the prompt to the LLM (Ollama or local llama-cpp).  
   - Returns the generated answer and source files.

---

## ⚙️ Notes & troubleshooting

- 🧠 **Model output parsing:**  
  If the response contains `"LLM error: Extra data..."`, ignore it or reduce prompt complexity.
- 🧾 **Re-ingest docs:**  
  Run `python -m modules.ingest` every time you update README files.
- 🧰 **Reset Chroma DB:**  
  Delete the `.chroma/` folder to rebuild the vector store from scratch.
- 🪶 **Model choice:**  
  - `phi3:mini`: very lightweight, fast, sometimes less structured answers.  
  - `mistral:7b-instruct` or `llama3.1:8b-instruct-q4_K_M`: slower, higher quality.

