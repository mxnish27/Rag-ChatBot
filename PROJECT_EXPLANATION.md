# Project Explanation

Comprehensive explanation of the RAG Course Chatbot architecture, components, and implementation.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Decisions](#design-decisions)

## Project Overview

### What is RAG?

**Retrieval-Augmented Generation (RAG)** combines:
- **Retrieval**: Finding relevant information from a knowledge base
- **Generation**: Using an LLM to generate responses based on retrieved context

### Why RAG?

RAG solves traditional LLM limitations:
- No knowledge cutoff
- Access to private/custom data
- Reduced hallucinations
- Source citations

### Project Purpose

Enable students to:
- Ask questions about course materials
- Get answers from lecture notes and exam papers
- Receive cited sources
- Study efficiently

## Architecture

### High-Level Overview

```
Frontend (UI) → FastAPI (API) → RAG Chain → Vector Store + LLM
```

### Component Flow

1. **User Query** → API validates and authenticates
2. **RAG Chain** → Orchestrates retrieval and generation
3. **Vector Store** → Finds relevant documents
4. **LLM** → Generates answer from context
5. **Response** → Returns answer with sources

## Core Components

### 1. Document Processor

**Document Loader** (`src/document_processor/loader.py`)
- Supports PDF, DOCX, TXT, MD
- Extracts text and metadata
- Handles multiple formats

**Document Chunker** (`src/document_processor/chunker.py`)
- Splits documents into chunks (default: 1000 chars)
- Overlap for context (default: 200 chars)
- Preserves metadata

### 2. Embedding Generator

**Implementation** (`src/embeddings/embedder.py`)
- Model: sentence-transformers/all-MiniLM-L6-v2
- Dimension: 384
- Converts text to vectors for similarity search

### 3. Vector Store

**Pinecone** (`src/vector_store/pinecone_store.py`)
- Cloud-based, scalable
- Managed service
- Production-ready

**Chroma** (`src/vector_store/chroma_store.py`)
- Local storage
- No API key needed
- Good for development

### 4. LLM Handler

**Implementation** (`src/llm/llm_handler.py`)
- Model: Llama-3-8B-Instruct (default)
- Temperature: 0.7
- Max tokens: 512
- Generates natural language responses

### 5. RAG Chain

**Implementation** (`src/rag/rag_chain.py`)

**Process:**
1. Convert query to embedding
2. Search vector store for similar documents
3. Format retrieved documents as context
4. Generate answer using LLM with context
5. Return answer with sources

### 6. API Layer

**Endpoints** (`api/main.py`)
- `POST /query` - Ask questions
- `POST /upload` - Upload documents
- `POST /ingest` - Process documents directory
- `GET /stats` - System statistics
- `GET /health` - Health check

**Features:**
- Rate limiting
- API authentication
- CORS support
- Error handling

### 7. Frontend

**Implementation** (`frontend/`)
- Chat interface
- Document upload
- Source display
- Statistics dashboard
- Built with HTML/JS/TailwindCSS

## Data Flow

### Document Ingestion

1. Upload document (PDF/DOCX/TXT/MD)
2. Load and extract text
3. Split into chunks
4. Generate embeddings
5. Store in vector database

### Query Processing

1. User asks question
2. Convert question to embedding
3. Search vector store for similar chunks
4. Retrieve top-K relevant documents
5. Format as context for LLM
6. Generate answer
7. Return answer with sources

## Technology Stack

**Backend:**
- Python 3.10+
- FastAPI (web framework)
- LangChain (RAG framework)
- HuggingFace Transformers (LLM)
- Sentence Transformers (embeddings)
- PyTorch (deep learning)

**Vector Stores:**
- Pinecone (cloud)
- Chroma (local)

**Frontend:**
- HTML/CSS/JavaScript
- TailwindCSS

**Infrastructure:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Redis (caching)

## Design Decisions

### 1. Why LangChain?

- Abstracts RAG complexity
- Modular components
- Easy to swap implementations
- Active community

### 2. Why Sentence Transformers?

- Fast inference
- Good quality embeddings
- Small model size (80MB)
- No API costs

### 3. Why Llama 3?

- Open source
- High quality responses
- Multiple sizes (8B, 70B)
- Active development

### 4. Why FastAPI?

- Fast and modern
- Automatic API docs
- Type validation
- Async support

### 5. Modular Architecture

- Easy to swap components
- Testable
- Maintainable
- Scalable

### 6. Configuration Management

- Environment variables
- Pydantic settings
- Easy deployment
- Secure secrets

## Performance Considerations

### Optimization Strategies

1. **Embedding Caching** - Cache frequent queries
2. **Model Quantization** - Reduce memory usage
3. **Batch Processing** - Process multiple queries
4. **GPU Acceleration** - Faster inference
5. **Vector Store Tuning** - Optimize search parameters

### Scalability

- Horizontal scaling with Docker Swarm/Kubernetes
- Load balancing
- Distributed vector stores
- Caching layer with Redis

## Security Features

- API key authentication
- Rate limiting
- CORS configuration
- File upload validation
- Environment variable secrets
- HTTPS support

## Monitoring and Logging

- Structured logging with loguru
- Health check endpoints
- Prometheus metrics support
- Error tracking
- Performance monitoring

## Future Enhancements

1. Multi-language support
2. Conversation history
3. Advanced filtering
4. User feedback loop
5. A/B testing
6. Model fine-tuning
7. Streaming responses
8. Mobile app

---

**Built for educational excellence! 🎓**
