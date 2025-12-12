from typing import List, Dict, Optional
from langchain.schema import Document
from config import settings
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStoreFactory
from src.llm import LLMHandler
from src.utils import log


class RAGChain:
    """RAG (Retrieval Augmented Generation) chain implementation"""
    
    def __init__(
        self,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        llm_handler: Optional[LLMHandler] = None
    ):
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.llm_handler = llm_handler or LLMHandler()
        self.vector_store = VectorStoreFactory.create_vector_store(
            self.embedding_generator
        )
        
        self.system_prompt = """You are a helpful AI assistant that answers questions based on course notes and exam papers. 
Your role is to provide accurate, detailed answers using only the information from the provided context.

Guidelines:
- Answer questions based solely on the provided context
- If the context doesn't contain enough information, say so clearly
- Provide specific references to course materials when possible
- Be concise but thorough in your explanations
- If asked about topics not in the context, politely indicate that you don't have that information
- Format your answers clearly with proper structure"""
        
        log.info("Initialized RAG chain")
    
    def retrieve_context(
        self,
        query: str,
        k: int = None,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """Retrieve relevant documents for a query"""
        k = k or settings.RETRIEVAL_TOP_K
        
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
            
            filtered_results = [
                doc for doc, score in results
                if score >= settings.SIMILARITY_THRESHOLD
            ]
            
            log.info(
                f"Retrieved {len(filtered_results)} documents "
                f"(filtered from {len(results)} by similarity threshold)"
            )
            
            return filtered_results
        
        except Exception as e:
            log.error(f"Error retrieving context: {str(e)}")
            raise
    
    def format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents into context string"""
        if not documents:
            return "No relevant information found in the course materials."
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            content = doc.page_content.strip()
            context_parts.append(f"[Source {i}: {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def generate_answer(
        self,
        query: str,
        context: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """Generate an answer using the LLM"""
        try:
            prompt = self.llm_handler.format_prompt(
                system_prompt=self.system_prompt,
                user_message=query,
                context=context
            )
            
            answer = self.llm_handler.generate_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return answer
        
        except Exception as e:
            log.error(f"Error generating answer: {str(e)}")
            raise
    
    def query(
        self,
        question: str,
        k: int = None,
        filter: Optional[dict] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Complete RAG query: retrieve context and generate answer
        
        Returns:
            Dict with 'answer', 'context', and 'sources'
        """
        try:
            log.info(f"Processing query: {question}")
            
            retrieved_docs = self.retrieve_context(
                query=question,
                k=k,
                filter=filter
            )
            
            context = self.format_context(retrieved_docs)
            
            answer = self.generate_answer(
                query=question,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            sources = [
                {
                    "source": doc.metadata.get("source", "Unknown"),
                    "content": doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content
                }
                for doc in retrieved_docs
            ]
            
            result = {
                "answer": answer,
                "context": context,
                "sources": sources,
                "num_sources": len(sources)
            }
            
            log.info(f"Successfully generated answer with {len(sources)} sources")
            return result
        
        except Exception as e:
            log.error(f"Error processing query: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store"""
        try:
            ids = self.vector_store.add_documents(documents)
            log.info(f"Added {len(documents)} documents to vector store")
            return ids
        
        except Exception as e:
            log.error(f"Error adding documents: {str(e)}")
            raise
