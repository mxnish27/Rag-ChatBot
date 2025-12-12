# Setup Guide

Complete setup instructions for the RAG Course Chatbot.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [First-Time Setup](#first-time-setup)
5. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **Python**: 3.10 or higher
- **RAM**: 8GB (16GB recommended)
- **Storage**: 10GB free space
- **Internet**: Required for downloading models

### Recommended Requirements

- **RAM**: 16GB+
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for faster inference)
- **Storage**: 20GB+ SSD

### GPU Support (Optional)

For GPU acceleration:
- NVIDIA GPU with CUDA support
- CUDA Toolkit 11.8+
- cuDNN 8.6+

## Installation Methods

### Method 1: Local Installation (Recommended for Development)

#### Step 1: Install Python

**Windows:**
```bash
# Download from python.org or use winget
winget install Python.Python.3.10
```

**macOS:**
```bash
brew install python@3.10
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

#### Step 2: Clone Repository

```bash
git clone <repository-url>
cd rag-course-chatbot
```

#### Step 3: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**For GPU Support:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Method 2: Docker Installation (Recommended for Production)

#### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

**Install Docker:**

**Windows/macOS:**
- Download Docker Desktop from docker.com

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### Setup with Docker

```bash
# Clone repository
git clone <repository-url>
cd rag-course-chatbot

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor

# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Configuration

### Step 1: Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Choose Vector Store

#### Option A: Chroma (Local, No API Key Required)

```env
VECTOR_STORE=chroma
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
```

**Pros:**
- No API key needed
- Free
- Good for development
- Data stored locally

**Cons:**
- Not scalable for large deployments
- Manual backup required

#### Option B: Pinecone (Cloud, API Key Required)

1. Sign up at [pinecone.io](https://www.pinecone.io/)
2. Create a new project
3. Get your API key and environment

```env
VECTOR_STORE=pinecone
PINECONE_API_KEY=your-api-key-here
PINECONE_ENVIRONMENT=your-environment
PINECONE_INDEX_NAME=course-chatbot
```

**Pros:**
- Scalable
- Managed service
- Automatic backups
- Better for production

**Cons:**
- Requires API key
- Costs money (free tier available)

### Step 3: Configure LLM

#### Option A: Use Llama 3 8B (Recommended)

```env
LLM_MODEL=meta-llama/Llama-3-8B-Instruct
HUGGINGFACE_TOKEN=your-hf-token
```

**Requirements:**
- HuggingFace account
- Accept Llama 3 license on HuggingFace
- ~16GB RAM

#### Option B: Use Llama 3 70B (High Performance)

```env
LLM_MODEL=meta-llama/Llama-3-70B-Instruct
HUGGINGFACE_TOKEN=your-hf-token
```

**Requirements:**
- GPU with 40GB+ VRAM or
- CPU with 128GB+ RAM
- Model quantization recommended

#### Option C: Use Smaller Model (Low Resource)

```env
LLM_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

**Requirements:**
- ~4GB RAM
- No HuggingFace token needed

### Step 4: Get HuggingFace Token (If Using Llama)

1. Go to [huggingface.co](https://huggingface.co/)
2. Sign up or log in
3. Go to Settings → Access Tokens
4. Create a new token with read permissions
5. Accept Llama 3 model license:
   - Visit [meta-llama/Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Llama-3-8B-Instruct)
   - Click "Agree and access repository"

### Step 5: Additional Configuration

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Security (Enable for production)
API_KEY_ENABLED=false
API_KEY=your-secret-key-here

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_UPLOAD_SIZE=10485760  # 10MB

# RAG Settings
RETRIEVAL_TOP_K=5
SIMILARITY_THRESHOLD=0.7
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=512
```

## First-Time Setup

### Step 1: Create Data Directories

The application will create these automatically, but you can do it manually:

```bash
mkdir -p data/documents
mkdir -p data/uploads
mkdir -p data/chroma_db
mkdir -p logs
```

### Step 2: Add Your Documents

Place your course materials in `data/documents/`:

```bash
data/documents/
├── course_notes/
│   ├── chapter1.pdf
│   ├── chapter2.pdf
│   └── chapter3.pdf
├── exam_papers/
│   ├── midterm_2023.pdf
│   └── final_2023.pdf
└── study_guides/
    └── summary.docx
```

**Supported Formats:**
- PDF (.pdf)
- Word Documents (.docx)
- Text Files (.txt)
- Markdown (.md)

### Step 3: Ingest Documents

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Windows: venv\Scripts\activate

# Ingest all documents
python scripts/ingest_documents.py

# Or ingest a specific file
python scripts/ingest_documents.py --file data/documents/course_notes.pdf
```

**Expected Output:**
```
2024-01-15 10:30:00 | INFO     | Starting document ingestion...
2024-01-15 10:30:05 | INFO     | Loaded 15 documents
2024-01-15 10:30:10 | INFO     | Created 234 chunks
2024-01-15 10:30:30 | INFO     | Document ingestion completed successfully!
```

### Step 4: Start the Application

#### Local Development

**Terminal 1 - Start API:**
```bash
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
python -m http.server 3000
```

#### Docker

```bash
docker-compose up -d
```

### Step 5: Verify Installation

1. **Check API Health:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

2. **Check Stats:**
```bash
curl http://localhost:8000/stats
```

3. **Test Query:**
```bash
python scripts/test_query.py "What topics are covered in the course?"
```

4. **Open Frontend:**
- Navigate to http://localhost:3000
- Try asking a question

## Troubleshooting

### Issue: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'langchain'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Windows: venv\Scripts\activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: Out of Memory

**Error:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Use CPU instead of GPU:**
```env
# In config/config.py or set device manually
device = "cpu"
```

2. **Use smaller model:**
```env
LLM_MODEL=TinyLlama/TinyLlama-1.1B-Chat-v1.0
```

3. **Reduce batch size and tokens:**
```env
LLM_MAX_TOKENS=256
CHUNK_SIZE=500
RETRIEVAL_TOP_K=3
```

### Issue: Pinecone Connection Error

**Error:**
```
PineconeException: Invalid API key
```

**Solution:**
1. Verify API key in `.env`
2. Check Pinecone dashboard for correct environment
3. Ensure index name matches

**Alternative:** Use Chroma instead:
```env
VECTOR_STORE=chroma
```

### Issue: HuggingFace Token Error

**Error:**
```
OSError: You are trying to access a gated repo
```

**Solution:**
1. Get HuggingFace token (see Step 4 above)
2. Accept model license on HuggingFace
3. Add token to `.env`:
```env
HUGGINGFACE_TOKEN=hf_your_token_here
```

### Issue: Slow Inference

**Solutions:**

1. **Enable GPU:**
```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

2. **Use Model Quantization:**
```python
# In src/llm/llm_handler.py
load_in_8bit=True  # or load_in_4bit=True
```

3. **Reduce model size:**
```env
LLM_MODEL=meta-llama/Llama-3-8B-Instruct  # Instead of 70B
```

### Issue: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**

**Find and kill process:**
```bash
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Or use different port:**
```bash
uvicorn api.main:app --port 8001
```

### Issue: Documents Not Loading

**Check:**

1. **File format supported:**
```bash
# Supported: .pdf, .docx, .txt, .md
```

2. **File permissions:**
```bash
chmod 644 data/documents/*
```

3. **File size:**
```env
MAX_UPLOAD_SIZE=10485760  # Increase if needed
```

4. **Check logs:**
```bash
tail -f logs/app_*.log
```

### Getting Help

If you encounter issues not covered here:

1. Check logs in `logs/` directory
2. Enable debug mode:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

3. Run with verbose output:
```bash
python scripts/ingest_documents.py --verbose
```

4. Check system resources:
```bash
# Linux/macOS
htop

# Windows
Task Manager
```

## Next Steps

After successful setup:

1. Read [README.md](README.md) for usage examples
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
3. Explore API documentation at http://localhost:8000/docs
4. Customize configuration for your use case

---

**Setup complete! 🎉**
