from typing import Union
from config import settings
from src.embeddings import EmbeddingGenerator
from src.utils import log
from .pinecone_store import PineconeVectorStore
from .chroma_store import ChromaVectorStore


class VectorStoreFactory:
    """Factory for creating vector store instances"""
    
    @staticmethod
    def create_vector_store(
        embedding_generator: EmbeddingGenerator
    ) -> Union[PineconeVectorStore, ChromaVectorStore]:
        """Create a vector store based on configuration"""
        
        vector_store_type = settings.VECTOR_STORE.lower()
        
        if vector_store_type == "pinecone":
            log.info("Creating Pinecone vector store")
            return PineconeVectorStore(embedding_generator)
        
        elif vector_store_type == "chroma":
            log.info("Creating Chroma vector store")
            return ChromaVectorStore(embedding_generator)
        
        else:
            raise ValueError(
                f"Unsupported vector store type: {vector_store_type}. "
                "Supported types: pinecone, chroma"
            )
