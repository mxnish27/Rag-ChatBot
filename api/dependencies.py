from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional
import time
from collections import defaultdict

from config import settings
from src import RAGChain, log


_rag_chain_instance: Optional[RAGChain] = None


def get_rag_chain() -> RAGChain:
    """Dependency to get RAG chain instance (singleton)"""
    global _rag_chain_instance
    
    if _rag_chain_instance is None:
        log.info("Initializing RAG chain...")
        _rag_chain_instance = RAGChain()
        log.info("RAG chain initialized successfully")
    
    return _rag_chain_instance


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> None:
    """Verify API key if authentication is enabled"""
    if not settings.API_KEY_ENABLED:
        return
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
    
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit"""
        if not settings.RATE_LIMIT_ENABLED:
            return True
        
        now = time.time()
        window_start = now - settings.RATE_LIMIT_PERIOD
        
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        if len(self.requests[client_id]) >= settings.RATE_LIMIT_REQUESTS:
            return False
        
        self.requests[client_id].append(now)
        return True


rate_limiter_instance = RateLimiter()


async def rate_limiter(client_id: str = "default") -> None:
    """Rate limiting dependency"""
    if not rate_limiter_instance.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {settings.RATE_LIMIT_REQUESTS} "
                   f"requests per {settings.RATE_LIMIT_PERIOD} seconds."
        )
