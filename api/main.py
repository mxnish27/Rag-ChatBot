from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import os
import shutil
from pathlib import Path

from config import settings
from src import DocumentLoader, DocumentChunker, RAGChain, log
from api.dependencies import get_rag_chain, rate_limiter, verify_api_key


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG-based chatbot for course notes and exam papers"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str = Field(..., description="The question to ask")
    k: Optional[int] = Field(None, description="Number of documents to retrieve")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    temperature: Optional[float] = Field(None, description="Temperature for generation")


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    num_sources: int


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class UploadResponse(BaseModel):
    message: str
    files_processed: int
    chunks_created: int


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.post("/query", response_model=QueryResponse, dependencies=[Depends(rate_limiter)])
async def query_chatbot(
    request: QueryRequest,
    rag_chain: RAGChain = Depends(get_rag_chain),
    _: None = Depends(verify_api_key)
):
    """
    Query the chatbot with a question
    
    The chatbot will retrieve relevant context from course notes and exam papers,
    then generate an answer using the LLM.
    """
    try:
        log.info(f"Received query: {request.question}")
        
        result = rag_chain.query(
            question=request.question,
            k=request.k,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            num_sources=result["num_sources"]
        )
    
    except Exception as e:
        log.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.post("/upload", response_model=UploadResponse, dependencies=[Depends(rate_limiter)])
async def upload_documents(
    files: List[UploadFile] = File(...),
    rag_chain: RAGChain = Depends(get_rag_chain),
    _: None = Depends(verify_api_key)
):
    """
    Upload course notes or exam papers
    
    Supported formats: PDF, DOCX, TXT, MD
    """
    try:
        document_loader = DocumentLoader(settings.UPLOADS_DIR)
        document_chunker = DocumentChunker()
        
        uploaded_files = []
        
        for file in files:
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension not in settings.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type {file_extension} not supported. "
                           f"Allowed: {settings.ALLOWED_EXTENSIONS}"
                )
            
            file_size = 0
            file_path = Path(settings.UPLOADS_DIR) / file.filename
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                file_size = len(content)
                
                if file_size > settings.MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File {file.filename} exceeds maximum size "
                               f"of {settings.MAX_UPLOAD_SIZE} bytes"
                    )
                
                buffer.write(content)
            
            uploaded_files.append(str(file_path))
            log.info(f"Uploaded file: {file.filename} ({file_size} bytes)")
        
        all_documents = []
        for file_path in uploaded_files:
            documents = document_loader.load_document(file_path)
            all_documents.extend(documents)
        
        chunks = document_chunker.chunk_documents(all_documents)
        
        rag_chain.add_documents(chunks)
        
        log.info(
            f"Successfully processed {len(uploaded_files)} files "
            f"into {len(chunks)} chunks"
        )
        
        return UploadResponse(
            message="Documents uploaded and processed successfully",
            files_processed=len(uploaded_files),
            chunks_created=len(chunks)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading documents: {str(e)}"
        )


@app.post("/ingest", dependencies=[Depends(rate_limiter)])
async def ingest_documents(
    rag_chain: RAGChain = Depends(get_rag_chain),
    _: None = Depends(verify_api_key)
):
    """
    Ingest all documents from the documents directory
    
    This endpoint processes all documents in the configured documents directory
    and adds them to the vector store.
    """
    try:
        document_loader = DocumentLoader(settings.DOCUMENTS_DIR)
        document_chunker = DocumentChunker()
        
        documents = document_loader.load_directory()
        
        if not documents:
            return JSONResponse(
                content={
                    "message": "No documents found in documents directory",
                    "documents_processed": 0,
                    "chunks_created": 0
                }
            )
        
        chunks = document_chunker.chunk_documents(documents)
        
        rag_chain.add_documents(chunks)
        
        log.info(
            f"Successfully ingested {len(documents)} documents "
            f"into {len(chunks)} chunks"
        )
        
        return {
            "message": "Documents ingested successfully",
            "documents_processed": len(documents),
            "chunks_created": len(chunks)
        }
    
    except Exception as e:
        log.error(f"Error ingesting documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting documents: {str(e)}"
        )


@app.get("/stats")
async def get_stats(_: None = Depends(verify_api_key)):
    """Get statistics about the system"""
    try:
        documents_dir = Path(settings.DOCUMENTS_DIR)
        uploads_dir = Path(settings.UPLOADS_DIR)
        
        doc_count = len(list(documents_dir.glob("**/*.*"))) if documents_dir.exists() else 0
        upload_count = len(list(uploads_dir.glob("**/*.*"))) if uploads_dir.exists() else 0
        
        return {
            "documents_in_library": doc_count,
            "uploaded_documents": upload_count,
            "vector_store": settings.VECTOR_STORE,
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_model": settings.LLM_MODEL
        }
    
    except Exception as e:
        log.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
