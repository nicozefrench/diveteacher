"""
RAG (Retrieval-Augmented Generation) Chain

This module implements the RAG workflow:
1. Query Neo4j knowledge graph for relevant context
2. Build prompt with retrieved context
3. Stream LLM response
"""

from typing import AsyncGenerator, List, Dict, Any
from app.core.llm import get_llm
from app.integrations.neo4j import neo4j_client
from app.core.config import settings


async def retrieve_context(question: str, top_k: int = None) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context from Neo4j knowledge graph
    
    Args:
        question: User's question
        top_k: Number of context chunks to retrieve (default: from settings)
        
    Returns:
        List of context dictionaries with text and metadata
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K
    
    # Query Neo4j for relevant entities and relationships
    context_nodes = await neo4j_client.query_context(question, top_k=top_k)
    
    return context_nodes


def build_rag_prompt(question: str, context: List[Dict[str, Any]]) -> tuple[str, str]:
    """
    Build RAG prompt from question and retrieved context
    
    Args:
        question: User's question
        context: List of context dictionaries
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    
    # Build context string
    context_parts = []
    for idx, ctx in enumerate(context, 1):
        text = ctx.get("text", "")
        source = ctx.get("source", "Unknown")
        context_parts.append(f"[Context {idx} - Source: {source}]\n{text}")
    
    context_str = "\n\n".join(context_parts)
    
    # System prompt
    system_prompt = """You are a helpful AI assistant that answers questions based ONLY on the provided context from uploaded documents.

CRITICAL RULES:
1. Answer ONLY using information from the provided context
2. If the context doesn't contain enough information, say "I don't have enough information in the uploaded documents to answer that question"
3. NEVER make up or infer information not present in the context
4. Cite the source (Context 1, Context 2, etc.) when answering
5. Be concise but thorough

Your goal is to provide accurate, grounded answers that users can trust."""
    
    # User prompt
    if context_parts:
        user_prompt = f"""Context from uploaded documents:

{context_str}

---

Question: {question}

Answer based ONLY on the context above:"""
    else:
        user_prompt = f"""No relevant context found in uploaded documents.

Question: {question}

Please explain that you don't have enough information to answer this question."""
    
    return system_prompt, user_prompt


async def rag_stream_response(
    question: str, 
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> AsyncGenerator[str, None]:
    """
    RAG chain: Retrieve → Build prompt → Stream LLM response
    
    Args:
        question: User's question
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens to generate
        
    Yields:
        Response tokens as they are generated
    """
    
    # Step 1: Retrieve context
    context = await retrieve_context(question)
    
    # Step 2: Build prompt
    system_prompt, user_prompt = build_rag_prompt(question, context)
    
    # Step 3: Stream LLM response
    llm = get_llm()
    async for token in llm.stream_completion(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    ):
        yield token


async def rag_query(
    question: str, 
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Dict[str, Any]:
    """
    RAG query with full response (non-streaming)
    
    Args:
        question: User's question
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens to generate
        
    Returns:
        Dictionary with answer, context, and metadata
    """
    
    # Retrieve context
    context = await retrieve_context(question)
    
    # Build prompt
    system_prompt, user_prompt = build_rag_prompt(question, context)
    
    # Get LLM response
    llm = get_llm()
    full_response = ""
    async for token in llm.stream_completion(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    ):
        full_response += token
    
    return {
        "question": question,
        "answer": full_response,
        "context": context,
        "num_sources": len(context)
    }

