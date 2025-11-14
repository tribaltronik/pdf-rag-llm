# Spec-Driven Development Plan: RAG MLOPS PoC

## 1. System Requirements Specification

### 1.1 Functional Requirements
- **FR-001:** System ingest text files (TXT, PDF, MD)
- **FR-002:** System chunk text with configurable size & overlap
- **FR-003:** System embed chunks using lightweight transformer
- **FR-004:** System store embeddings in FAISS vector DB
- **FR-005:** System retrieve top-k similar chunks for query
- **FR-006:** System call external LLM API (Ollama) for inference
- **FR-007:** System return structured JSON response with answer + metadata

### 1.2 Non-Functional Requirements
- **NFR-001:** Inference latency < 2s per query
- **NFR-002:** Memory footprint < 8GB (embeddings + model)
- **NFR-003:** API throughput ≥ 10 req/s
- **NFR-004:** 99% uptime for production deployment

### 1.3 Security Requirements
- **SEC-001:** Validate file upload size (max 50MB)
- **SEC-002:** Sanitize file paths (prevent directory traversal)
- **SEC-003:** Implement rate limiting on API endpoints
- **SEC-004:** Log all queries for audit trail

---

## 2. API Contract Specification

### 2.1 Endpoints

#### POST /ingest
**Request:**
```json
{
  "file": "<binary>",
  "chunk_size": 500,
  "overlap": 100
}
```
**Response:** `200 OK`
```json
{
  "status": "success",
  "chunks": 245,
  "file_size_bytes": 125000,
  "embedding_time_ms": 1250
}
```

#### POST /query
**Request:**
```json
{
  "question": "What is RAG?",
  "top_k": 3,
  "temperature": 0.3
}
```
**Response:** `200 OK`
```json
{
  "question": "What is RAG?",
  "answer": "RAG is Retrieval-Augmented Generation...",
  "context_chunks": 3,
  "inference_time_ms": 1850,
  "model": "llama2"
}
```

#### GET /health
**Response:** `200 OK`
```json
{
  "status": "healthy",
  "vector_store": "initialized",
  "chunks_indexed": 245
}
```

---

## 3. Development Phases

### Phase 1: Core Infrastructure (Week 1)
**Acceptance Criteria:**
- [ ] FastAPI server boots without errors
- [ ] Ollama connection established & health check passes
- [ ] FAISS index initializes on startup
- [ ] All endpoints respond with correct HTTP status codes

**Tasks:**
1. Setup FastAPI project structure
2. Configure Ollama client (URL, model, timeout)
3. Initialize FAISS index schema
4. Implement `/health` endpoint with detailed checks
5. Add basic error handling & logging

**Testing:**
- Unit tests for config validation
- Integration test for Ollama connectivity

---

### Phase 2: File Ingestion & Embedding (Week 2)
**Acceptance Criteria:**
- [ ] Upload endpoint accepts TXT/PDF/MD files
- [ ] Text chunking produces expected chunk count
- [ ] Embeddings generated without OOM errors
- [ ] FAISS index populated & searchable

**Tasks:**
1. Implement file upload handler with size validation
2. Add text parsing for multiple formats
3. Implement chunking algorithm (chunk_size, overlap)
4. Load SentenceTransformer model on startup
5. Generate embeddings batch-wise
6. Persist FAISS index to disk (checkpoint)

**Testing:**
- Parametrized tests for different file sizes
- Verify chunk boundaries & overlap
- Memory profiling

---

### Phase 3: Query & Retrieval (Week 3)
**Acceptance Criteria:**
- [ ] Query endpoint retrieves top-k relevant chunks
- [ ] Retrieved context semantically relevant (manual inspection)
- [ ] Retrieval latency < 100ms for 10k chunks

**Tasks:**
1. Implement vector similarity search (FAISS)
2. Rank results by distance score
3. Format retrieved chunks as context string
4. Test retrieval quality on sample queries
5. Add caching layer for frequent queries (optional)

**Testing:**
- Retrieval recall tests
- Latency benchmarks
- Cache hit rate monitoring

---

### Phase 4: LLM Integration & RAG (Week 4)
**Acceptance Criteria:**
- [ ] LLM inference < 2s per query
- [ ] Answer quality acceptable (manual review)
- [ ] Prompt injection attempts blocked
- [ ] Error responses graceful

**Tasks:**
1. Implement Ollama API call with prompt engineering
2. Add prompt templates for RAG context injection
3. Implement timeout & retry logic
4. Add prompt sanitization/validation
5. Stream inference response handling
6. Add token counting for cost estimation

**Testing:**
- E2E RAG tests (file → query → answer)
- Adversarial prompt testing
- Latency SLA validation

---

### Phase 5: Deployment & Operations (Week 5)
**Acceptance Criteria:**
- [ ] Docker image builds & runs
- [ ] Kubernetes manifest deployed to test cluster
- [ ] Prometheus metrics exposed
- [ ] All SLOs met in staging

**Tasks:**
1. Create Dockerfile with layer optimization
2. Write Kubernetes manifests (Deployment, Service, ConfigMap)
3. Add Prometheus instrumentation
4. Implement structured logging (JSON)
5. Create health check probes (liveness, readiness)
6. Setup monitoring alerts (latency, error rate)
7. Document deployment runbook

**Testing:**
- Load testing (10 req/s sustained)
- Chaos engineering (pod restart, network delay)
- Production readiness checklist

---

## 4. Quality Gates

| Gate | Threshold | Tool |
|------|-----------|------|
| Code Coverage | ≥ 80% | pytest-cov |
| Type Checking | 0 mypy errors | mypy |
| Linting | 0 critical issues | pylint, ruff |
| Latency p95 | < 2s | locust |
| Error Rate | < 0.5% | CloudWatch/Prometheus |

---

## 5. Dependency Matrix

```
Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4 ──→ Phase 5
 (setup)     (ingest)   (retrieve)   (LLM)    (deploy)
```

Phase 2 blocked until Phase 1 complete.
Phase 4 can start after Phase 3 in parallel with optimizations.

---

## 6. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLM inference too slow | NFR-001 fail | Profile early, use smaller model |
| OOM on large files | System crash | Implement streaming ingestion |
| Hallucination in answers | Quality | Enforce context-only responses, add confidence scores |
| FAISS scalability | Search latency | Use HNSW for 10k+ chunks |

---

## 7. Success Metrics

- ✓ All AC passed
- ✓ SLOs achieved (latency, uptime, throughput)
- ✓ Zero critical security findings
- ✓ Ready for staging → production