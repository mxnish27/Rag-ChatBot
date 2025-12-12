# RAG Course Chatbot 🎓

A production-ready Retrieval-Augmented Generation (RAG) chatbot that answers questions from course notes and past exam papers using LangChain, vector stores (Pinecone/Chroma), and open-source LLMs (Llama 3/4).

## 🌟 Features

- **Document Processing**: Supports PDF, DOCX, TXT, and Markdown files
- **Vector Storage**: Choose between Pinecone (cloud) or Chroma (local)
- **LLM Integration**: Uses Llama 3/4 models via HuggingFace
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Modern UI**: Beautiful, responsive web interface
- **Docker Support**: Easy deployment with Docker Compose
- **Production Ready**: Includes logging, rate limiting, health checks, and monitoring

## 📋 Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ (HTML/JS/TailwindCSS)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ (REST API)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  RAG Chain  │ (LangChain)
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
┌─────┐ ┌─────┐
│Vector│ │ LLM │
│Store│ │Model│
└─────┘ └─────┘
```

**Components:**
- **Document Processor**: Loads and chunks documents
- **Embedding Generator**: Creates embeddings using sentence-transformers
- **Vector Store**: Stores and retrieves embeddings (Pinecone/Chroma)
- **LLM Handler**: Generates responses using Llama models
- **RAG Chain**: Orchestrates retrieval and generation

## 📦 Prerequisites

- Python 3.10+
- Docker & Docker Compose (for containerized deployment)
- 8GB+ RAM (16GB recommended for larger models)
- GPU (optional, but recommended for faster inference)

### API Keys (Optional)

- **Pinecone**: Required if using Pinecone vector store
- **HuggingFace**: Required for downloading gated models (Llama)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd rag-course-chatbot
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```env
# Choose vector store
VECTOR_STORE=chroma  # or pinecone

# For Pinecone (if using)
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=your-environment

# For HuggingFace (if using gated models)
HUGGINGFACE_TOKEN=your-token

# LLM Configuration
LLM_MODEL=meta-llama/Llama-3-8B-Instruct
```

### 3. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 4. Add Your Documents

Place your course notes and exam papers in the `data/documents/` directory:

```bash
data/documents/
├── course_notes.pdf
├── lecture_slides.pdf
├── exam_paper_2023.pdf
└── study_guide.docx
```

### 5. Ingest Documents

```bash
python scripts/ingest_documents.py
```

### 6. Start the Application

```bash
# Start API server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# In another terminal, serve frontend
cd frontend
python -m http.server 3000
```

### 7. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VECTOR_STORE` | Vector store type (pinecone/chroma) | `pinecone` |
| `LLM_MODEL` | HuggingFace model name | `meta-llama/Llama-3-8B-Instruct` |
| `EMBEDDING_MODEL` | Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Document chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `RETRIEVAL_TOP_K` | Number of documents to retrieve | `5` |
| `LLM_TEMPERATURE` | Generation temperature | `0.7` |
| `LLM_MAX_TOKENS` | Max tokens in response | `512` |

### Vector Store Options

**Chroma (Local)**
- No API key required
- Data stored locally
- Good for development and small deployments

**Pinecone (Cloud)**
- Requires API key
- Scalable and managed
- Better for production

## 📚 API Documentation

### Endpoints

#### `POST /query`
Query the chatbot with a question.

**Request:**
```json
{
  "question": "What is the main topic of Chapter 3?",
  "k": 5,
  "max_tokens": 512,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "answer": "Chapter 3 focuses on...",
  "sources": [...],
  "num_sources": 3
}
```

#### `POST /upload`
Upload documents to the system.

**Request:** Multipart form data with files

**Response:**
```json
{
  "message": "Documents uploaded successfully",
  "files_processed": 2,
  "chunks_created": 45
}
```

#### `POST /ingest`
Ingest all documents from the documents directory.

#### `GET /stats`
Get system statistics.

#### `GET /health`
Health check endpoint.

## 💡 Usage Examples

### Using the Web Interface

1. Open http://localhost:3000
2. Upload your course materials using the "Upload Documents" button
3. Ask questions in the chat interface
4. View sources for each answer

### Using the API

```python
import requests

# Query the chatbot
response = requests.post(
    "http://localhost:8000/query",
    json={"question": "Explain the concept of RAG"}
)
result = response.json()
print(result["answer"])
```

### Using the CLI

```bash
# Test a query
python scripts/test_query.py "What is covered in the final exam?"

# Ingest a specific file
python scripts/ingest_documents.py --file path/to/document.pdf
```

## 🐳 Deployment

### Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:
- **API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Redis**: localhost:6379

### Docker (API Only)

```bash
# Build image
docker build -t rag-chatbot .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e VECTOR_STORE=chroma \
  rag-chatbot
```

### Cloud Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to:
- AWS (EC2, ECS, Lambda)
- Google Cloud Platform
- Azure
- Heroku

## 📁 Project Structure

```
rag-course-chatbot/
├── api/                    # FastAPI application
│   ├── main.py            # API endpoints
│   └── dependencies.py    # Dependencies and middleware
├── config/                # Configuration
│   └── config.py         # Settings management
├── src/                   # Core application code
│   ├── document_processor/  # Document loading and chunking
│   ├── embeddings/         # Embedding generation
│   ├── vector_store/       # Vector store implementations
│   ├── llm/               # LLM handler
│   ├── rag/               # RAG chain
│   └── utils/             # Utilities and logging
├── frontend/              # Web interface
│   ├── index.html
│   └── app.js
├── scripts/               # Utility scripts
│   ├── ingest_documents.py
│   └── test_query.py
├── data/                  # Data directory
│   ├── documents/         # Course materials
│   ├── uploads/           # Uploaded files
│   └── chroma_db/         # Chroma database
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## 🔒 Security Considerations

- **API Keys**: Never commit `.env` file to version control
- **Rate Limiting**: Enabled by default to prevent abuse
- **CORS**: Configure `CORS_ORIGINS` for production
- **API Authentication**: Enable `API_KEY_ENABLED` for production
- **File Uploads**: Size limits and type validation included

## 🧪 Testing

```bash
# Run tests
pytest

# Test with coverage
pytest --cov=src tests/

# Test a specific query
python scripts/test_query.py "Your question here"
```

## 🛠️ Troubleshooting

### Common Issues

**1. Out of Memory**
- Use a smaller model (Llama-3-8B instead of 70B)
- Reduce `CHUNK_SIZE` and `RETRIEVAL_TOP_K`
- Enable model quantization

**2. Slow Inference**
- Use GPU if available
- Reduce `LLM_MAX_TOKENS`
- Consider using a smaller embedding model

**3. Poor Answer Quality**
- Increase `RETRIEVAL_TOP_K`
- Adjust `SIMILARITY_THRESHOLD`
- Improve document chunking strategy
- Use a larger LLM model

## 📈 Performance Optimization

- **GPU Acceleration**: Set `device=cuda` in LLM handler
- **Model Quantization**: Use 4-bit or 8-bit quantization
- **Caching**: Enable Redis for response caching
- **Batch Processing**: Process multiple queries together
- **Index Optimization**: Tune vector store parameters

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request



## 🙏 Acknowledgments

- **LangChain**: RAG framework
- **HuggingFace**: LLM and embedding models
- **Pinecone/Chroma**: Vector stores
- **FastAPI**: Web framework
- **Meta**: Llama models

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review existing issues

---

**Built with ❤️ for students and educators**
#   R a g - C h a t B o t  
 