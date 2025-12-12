from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import settings
from src.utils import log


class DocumentChunker:
    """Split documents into chunks for embedding"""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        
        log.info(
            f"Initialized DocumentChunker with chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}"
        )
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks"""
        try:
            chunks = self.text_splitter.split_documents(documents)
            
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_id"] = i
                chunk.metadata["chunk_size"] = len(chunk.page_content)
            
            log.info(
                f"Split {len(documents)} documents into {len(chunks)} chunks"
            )
            return chunks
        
        except Exception as e:
            log.error(f"Error chunking documents: {str(e)}")
            raise
    
    def chunk_text(self, text: str, metadata: dict = None) -> List[Document]:
        """Split raw text into chunks"""
        try:
            chunks = self.text_splitter.split_text(text)
            
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = metadata.copy() if metadata else {}
                doc_metadata["chunk_id"] = i
                doc_metadata["chunk_size"] = len(chunk)
                
                documents.append(
                    Document(page_content=chunk, metadata=doc_metadata)
                )
            
            log.info(f"Split text into {len(documents)} chunks")
            return documents
        
        except Exception as e:
            log.error(f"Error chunking text: {str(e)}")
            raise
