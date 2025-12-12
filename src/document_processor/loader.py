from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.schema import Document
from src.utils import log


class DocumentLoader:
    """Load documents from various file formats"""
    
    LOADERS = {
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
    }
    
    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load a single document"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension not in self.LOADERS:
            raise ValueError(f"Unsupported file type: {extension}")
        
        try:
            loader_class = self.LOADERS[extension]
            loader = loader_class(str(file_path))
            documents = loader.load()
            
            for doc in documents:
                doc.metadata["source"] = str(file_path)
                doc.metadata["file_type"] = extension
            
            log.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents
        
        except Exception as e:
            log.error(f"Error loading document {file_path}: {str(e)}")
            raise
    
    def load_directory(self, directory: Optional[str] = None) -> List[Document]:
        """Load all documents from a directory"""
        if directory is None:
            directory = self.documents_dir
        else:
            directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        all_documents = []
        
        for extension in self.LOADERS.keys():
            files = list(directory.glob(f"**/*{extension}"))
            
            for file_path in files:
                try:
                    documents = self.load_document(str(file_path))
                    all_documents.extend(documents)
                except Exception as e:
                    log.error(f"Failed to load {file_path}: {str(e)}")
                    continue
        
        log.info(f"Loaded total of {len(all_documents)} documents from {directory}")
        return all_documents
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return list(self.LOADERS.keys())
