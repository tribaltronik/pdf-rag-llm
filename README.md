# PDF RAG LLM

A simple document Q&A system that lets you upload PDFs and ask questions about their content using AI.

## 🚀 Quick Start

1. **Start the services:**
   ```bash
   make up
   ```

2. **Wait for the model to download** (first time only)

3. **Check health:**
   ```bash
   make health
   ```

4. **Ask questions (document auto-loaded):**
   ```bash
   make test-query
   ```

## 📁 Project Structure

```
├── app/                   # Application code
│   ├── app.py            # FastAPI server
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # App container
├── data/                 # Sample documents
├── docker-compose.yml    # Service orchestration
└── README.md            # This file
```

## 🔧 What's Included

- **FastAPI**: Web server with automatic API docs
- **Ollama**: Local LLM with `deepseek-coder:1.3b` model preloaded
- **Document Processing**: Upload TXT, PDF, or MD files
- **Simple RAG**: Keyword matching + LLM generation

## 🌐 Access Points

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📋 API Usage

### Upload Document
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/fake_document.pdf" \
  -F "chunk_size=500" \
  -F "overlap=100"
```

### Ask Question
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main points?",
    "top_k": 3,
    "temperature": 0.3
  }'
```

## 🛑 Stop Services
```bash
make down
```

## 🛠️ Development Commands

```bash
make dev      # Start with logs
make logs     # View logs
make restart  # Restart services
make clean    # Remove everything
make test     # Run tests
make lint     # Check code quality
make format   # Format code
```

## 📝 Notes

- First run downloads the AI model (~1GB)
- Documents are stored in memory only
- Supports files up to 50MB
- Simple keyword matching (no vector embeddings yet)