from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import httpx
import logging
from typing import Dict, Any
import PyPDF2
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF RAG LLM", version="1.0.0")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Simple in-memory document store
documents = []


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF content"""
    try:
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return ""


async def load_initial_document():
    """Load the fake_document.pdf on startup"""
    try:
        pdf_path = "/app/data/fake_document.pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                content = f.read()

            # Extract text from PDF
            text = extract_text_from_pdf(content)

            if not text.strip():
                logger.warning("No text extracted from PDF")
                return

            # Simple chunking
            chunk_size = 500
            overlap = 100
            chunks = []
            for i in range(0, len(text), chunk_size - overlap):
                chunk = text[i : i + chunk_size]
                if chunk.strip():
                    chunks.append(
                        {
                            "id": len(documents) + len(chunks),
                            "text": chunk,
                            "filename": "fake_document.pdf",
                        }
                    )

            documents.extend(chunks)
            logger.info(f"Loaded {len(chunks)} chunks from fake_document.pdf")
        else:
            logger.warning("fake_document.pdf not found")
    except Exception as e:
        logger.error(f"Failed to load initial document: {e}")


@app.on_event("startup")
async def startup_event():
    await load_initial_document()


@app.get("/")
async def read_root():
    """Serve the web UI"""
    return FileResponse("static/index.html")


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3
    temperature: float = 0.3


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
            ollama_status = (
                "connected" if response.status_code == 200 else "disconnected"
            )
    except Exception as e:
        ollama_status = "disconnected"
        logger.error(f"Ollama health check failed: {e}")

    return {
        "status": "healthy",
        "documents_stored": len(documents),
        "ollama": ollama_status,
    }


@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...), chunk_size: int = 500, overlap: int = 100
):
    """Ingest document for RAG"""
    if not file.filename.lower().endswith((".txt", ".pdf", ".md")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50MB limit
        raise HTTPException(status_code=400, detail="File too large")

    # Extract text based on file type
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(content)
    else:
        # Simple text extraction for non-PDF files
        try:
            text = content.decode("utf-8")
        except:
            text = content.decode("latin-1")

    # Simple chunking
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(
                {
                    "id": len(documents) + len(chunks),
                    "text": chunk,
                    "filename": file.filename,
                }
            )

    documents.extend(chunks)

    return {
        "status": "success",
        "chunks": len(chunks),
        "file_size_bytes": len(content),
        "embedding_time_ms": 0,
    }


@app.post("/query")
async def query_document(request: QueryRequest):
    """Query ingested documents"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Simple keyword matching for PoC
    question_words = set(request.question.lower().split())
    scored_chunks = []

    for doc in documents:
        doc_words = set(doc["text"].lower().split())
        overlap = len(question_words & doc_words)
        if overlap > 0:
            scored_chunks.append((doc, overlap))

    # Sort by overlap score and get top_k
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    top_chunks = [chunk for chunk, score in scored_chunks[: request.top_k]]

    # Simple context for LLM
    context = "\n\n".join([chunk["text"] for chunk in top_chunks])

    # Call Ollama
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "qwen2.5:0.5b",
                    "prompt": f"Context: {context}\n\nQuestion: {request.question}\n\nAnswer:",
                    "stream": False,
                },
                timeout=30.0,
            )
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "No response generated")
            else:
                answer = "Error calling LLM"
    except Exception as e:
        answer = f"LLM error: {str(e)}. Context preview: {context[:200]}..."

    return {
        "question": request.question,
        "answer": answer,
        "context_chunks": len(top_chunks),
        "inference_time_ms": 0,
        "model": "llama3.2:1b",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
