import sys
import argparse
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src import DocumentLoader, DocumentChunker, RAGChain, log
from config import settings


def main():
    parser = argparse.ArgumentParser(
        description="Ingest documents into the RAG system"
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=settings.DOCUMENTS_DIR,
        help="Directory containing documents to ingest"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Single file to ingest"
    )
    
    args = parser.parse_args()
    
    try:
        log.info("Starting document ingestion...")
        
        document_loader = DocumentLoader(settings.DOCUMENTS_DIR)
        document_chunker = DocumentChunker()
        rag_chain = RAGChain()
        
        if args.file:
            log.info(f"Loading single file: {args.file}")
            documents = document_loader.load_document(args.file)
        else:
            log.info(f"Loading documents from directory: {args.directory}")
            documents = document_loader.load_directory(args.directory)
        
        if not documents:
            log.warning("No documents found to ingest")
            return
        
        log.info(f"Loaded {len(documents)} documents")
        
        chunks = document_chunker.chunk_documents(documents)
        log.info(f"Created {len(chunks)} chunks")
        
        rag_chain.add_documents(chunks)
        
        log.info("Document ingestion completed successfully!")
        log.info(f"Total documents: {len(documents)}")
        log.info(f"Total chunks: {len(chunks)}")
        
    except Exception as e:
        log.error(f"Error during ingestion: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
