from typing import List, Optional
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain.schema import Document
from pinecone import Pinecone, ServerlessSpec
from config import settings
from src.embeddings import EmbeddingGenerator
from src.utils import log


class PineconeVectorStore:
    """Pinecone vector store implementation"""
    
    def __init__(self, embedding_generator: EmbeddingGenerator):
        self.embedding_generator = embedding_generator
        
        if not settings.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is required")
        
        try:
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self.index_name = settings.PINECONE_INDEX_NAME
            
            self._initialize_index()
            
            self.vectorstore = LangchainPinecone.from_existing_index(
                index_name=self.index_name,
                embedding=self.embedding_generator.embeddings
            )
            
            log.info(f"Initialized Pinecone vector store with index: {self.index_name}")
        
        except Exception as e:
            log.error(f"Error initializing Pinecone: {str(e)}")
            raise
    
    def _initialize_index(self):
        """Create index if it doesn't exist"""
        try:
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                log.info(f"Creating new Pinecone index: {self.index_name}")
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=settings.EMBEDDING_DIMENSION,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.PINECONE_ENVIRONMENT or 'us-east-1'
                    )
                )
                log.info(f"Created Pinecone index: {self.index_name}")
            else:
                log.info(f"Using existing Pinecone index: {self.index_name}")
        
        except Exception as e:
            log.error(f"Error initializing index: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        try:
            ids = self.vectorstore.add_documents(documents)
            log.info(f"Added {len(documents)} documents to Pinecone")
            return ids
        
        except Exception as e:
            log.error(f"Error adding documents to Pinecone: {str(e)}")
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
            log.error(f"Error searching Pinecone: {str(e)}")
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
            log.error(f"Error searching Pinecone: {str(e)}")
            raise
    
    def delete_index(self):
        """Delete the Pinecone index"""
        try:
            self.pc.delete_index(self.index_name)
            log.info(f"Deleted Pinecone index: {self.index_name}")
        
        except Exception as e:
            log.error(f"Error deleting index: {str(e)}")
            raise
