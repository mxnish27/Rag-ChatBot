import pytest
from src import DocumentLoader, DocumentChunker, EmbeddingGenerator, RAGChain


def test_document_loader():
    """Test document loading functionality"""
    loader = DocumentLoader("./data/documents")
    assert loader is not None
    assert loader.get_supported_extensions() == [".pdf", ".docx", ".txt", ".md"]


def test_document_chunker():
    """Test document chunking"""
    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    assert chunker.chunk_size == 100
    assert chunker.chunk_overlap == 20


def test_embedding_generator():
    """Test embedding generation"""
    embedder = EmbeddingGenerator()
    
    test_text = "This is a test sentence"
    embedding = embedder.embed_query(test_text)
    
    assert embedding is not None
    assert len(embedding) > 0
    assert isinstance(embedding, list)


@pytest.mark.asyncio
async def test_rag_chain():
    """Test RAG chain initialization"""
    # This is a basic test - full testing requires vector store setup
    try:
        rag_chain = RAGChain()
        assert rag_chain is not None
    except Exception as e:
        # Expected if vector store not configured
        assert "PINECONE_API_KEY" in str(e) or "vector" in str(e).lower()
