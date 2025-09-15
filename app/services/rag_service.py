# RAG 검색 서비스 (ChromaDB 기반, 없으면 더미)
from typing import List, Dict, Any
import os

async def search(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    # TODO: 실제 chromadb / faiss 붙이기
    return [{"text": f"관련 컨텍스트 {i+1} for '{query}'", "score": 0.5} for i in range(top_k)]
