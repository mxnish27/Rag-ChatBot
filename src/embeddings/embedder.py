from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from config import settings
from src.utils import log


class EmbeddingGenerator:
    """Generate embeddings for documents using HuggingFace models"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            log.info(f"Initialized embedding model: {self.model_name}")
        
        except Exception as e:
            log.error(f"Error initializing embedding model: {str(e)}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            embeddings = self.embeddings.embed_documents(texts)
            log.info(f"Generated embeddings for {len(texts)} documents")
            return embeddings
        
        except Exception as e:
            log.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        
        except Exception as e:
            log.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings"""
        test_embedding = self.embed_query("test")
        return len(test_embedding)
