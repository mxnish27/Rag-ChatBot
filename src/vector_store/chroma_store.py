from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from config import settings
from src.embeddings import EmbeddingGenerator
from src.utils import log


class ChromaVectorStore:
    """Chroma vector store implementation"""
    
    def __init__(self, embedding_generator: EmbeddingGenerator):
        self.embedding_generator = embedding_generator
        self.persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_generator.embeddings,
                collection_name="course_documents"
            )
            
            log.info(f"Initialized Chroma vector store at: {self.persist_directory}")
        
        except Exception as e:
            log.error(f"Error initializing Chroma: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        try:
            ids = self.vectorstore.add_documents(documents)
            self.vectorstore.persist()
            log.info(f"Added {len(documents)} documents to Chroma")
            return ids
        
        except Exception as e:
            log.error(f"Error adding documents to Chroma: {str(e)}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = None,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """Search for similar documents"""
        k = k or settings.RETRIEVAL_TOP_K
        
        try:
            results = self.vectorstore.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
            log.info(f"Retrieved {len(results)} documents for query")
            return results
        
        except Exception as e:
            log.error(f"Error searching Chroma: {str(e)}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = None,
        filter: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """Search for similar documents with scores"""
        k = k or settings.RETRIEVAL_TOP_K
        
        try:
            results = self.vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            log.info(f"Retrieved {len(results)} documents with scores")
            return results
        
        except Exception as e:
            log.error(f"Error searching Chroma: {str(e)}")
            raise
    
    def delete_collection(self):
        """Delete the Chroma collection"""
        try:
            self.vectorstore.delete_collection()
            log.info("Deleted Chroma collection")
        
        except Exception as e:
            log.error(f"Error deleting collection: {str(e)}")
            raise
