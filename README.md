# 🧠 AI Engineer Test – Knowledge Base System

This project is a containerized knowledge base system that allows:
- Uploading documents into a vector store
- Retrieving context for user queries
- Chatting with Gemini API using relevant data
- Logging all interactions for audit and analysis

---

## ⚙️ Tech Stack

- **FastAPI** – Web framework for serving APIs
- **PostgreSQL + pgvector** – Vector store database
- **LangChain** – For embeddings and retrieval
- **Gemini API** – Google Generative AI for chat responses
- **Docker & Docker Compose** – Containerization
- **Async I/O** – Fast and non-blocking API

---  

## 1. Create and Activate Virtual Environment
```bash
python3 -m venv ai-env
source ai-env/bin/activate
```

## 2. Install Dependencies
```bash
pip install fastapi uvicorn langchain google-generativeai psycopg2-binary pgvector sqlalchemy asyncpg python-dotenv

```

## 4. Add Your API Key
Create a *.env* file in the root directory:

```env
GEMINI_API_KEY=your-api-key-here
```

## 5. Start PostgreSQL + FastAPI Using Docker
```bash
docker-compose up --build
```
### This will:
- Start PostgreSQL with *pgvector*
- Start your FastAPI server on http://localhost:8000 


------------------------------

## Project Structure
### (In this project I have not used MCP Integration and LangGraph)
```
app/
├── api/
│   ├── knowledge.py        # Knowledge base endpoints
│   ├── chat.py             # Chat and audit endpoints
├── db/
│   ├── database.py         # Database connection/session
│   ├── models.py           # SQLAlchemy models
├── services/
│   ├── embedder.py         # Embedding service (e.g., LangChain)
│   ├── gemini.py           # Gemini API integration
main.py                     # FastAPI entry point
Dockerfile                  # App container
docker-compose.yml          # DB + app orchestration
requirements.txt            # Python dependencies

```

## Sample Requests (cURL)
### Query documents
```
curl -X POST http://localhost:8000/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What helps with chaining LLM tools?"}'
```

### Chat
```
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain vector search in AI."}'
```

### Get audit log
```
curl http://localhost:8000/audit/<chat_id>
```

### List documents
```
curl http://localhost:8000/knowledge
```

### Delete a document
```
curl -X DELETE http://localhost:8000/knowledge/1
```

### Reset all documents
```
curl -X DELETE http://localhost:8000/knowledge/reset
```

## Architecture Decisions

- **FastAPI** is used as the backend framework for its async support, rapid development capabilities, and built-in OpenAPI docs.
- **PostgreSQL with `pgvector` extension** is used as the vector store, enabling efficient similarity search directly within the database.
- **Custom embedding service (`embed_text`)** is used instead of relying on LangChain. While LangChain was considered, direct embedding provides better control and simplicity for this use case.
- **Gemini API** is integrated via `stream_gemini()` to generate real-time responses in a streaming manner.
- **Audit logs** (user input, retrieved context, LLM output, latency, etc.) are recorded in the database for performance monitoring and debugging.
- **Docker Compose** is used to orchestrate both the FastAPI app and the PostgreSQL vector database, ensuring a one-command deployment (`docker-compose up`).
- **Endpoints follow RESTful structure**, and responses are streamed via `StreamingResponse` for real-time LLM interaction.
- **Robust error handling** and a `/health` check endpoint are included to support deployment readiness and diagnostics.


## Audit Tools

- Endpoint `/audit/{chat_id}` provides full trace of a chat:
  - Input, context, model response, latency, timestamp
- Useful for:
  - Debugging incorrect answers
  - Measuring response time
  - Storing user feedback

