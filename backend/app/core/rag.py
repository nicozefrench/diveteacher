"""
RAG (Retrieval-Augmented Generation) Chain avec Graphiti

This module implements the RAG workflow:
1. Query Graphiti knowledge graph for relevant facts (hybrid search)
2. Build prompt with retrieved facts
3. Stream LLM response (Mistral 7b on Ollama)
"""

from typing import AsyncGenerator, List, Dict, Any
from app.core.llm import get_llm
from app.integrations.graphiti import search_knowledge_graph
from app.core.config import settings


async def retrieve_context(
    question: str, 
    top_k: int = None,
    group_ids: List[str] = None
) -> Dict[str, Any]:
    """
    Retrieve relevant context using Graphiti's hybrid search
    
    Args:
        question: User's question
        top_k: Number of results (default: from settings)
        group_ids: Filter by group_ids (multi-tenant)
        
    Returns:
        Dictionary with facts (EntityEdges) from Graphiti
        {
            "facts": List[Dict],  # Relations extraites
            "total": int
        }
        
    Note:
        - Uses Graphiti native search (semantic + BM25 + RRF)
        - Returns EntityEdges (relations) not just text chunks
        - More semantic than pure full-text search
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K
    
    # Graphiti hybrid search
    facts = await search_knowledge_graph(
        query=question,
        num_results=top_k,
        group_ids=group_ids
    )
    
    return {
        "facts": facts,
        "total": len(facts)
    }


def build_rag_prompt(question: str, context: Dict[str, Any]) -> tuple[str, str]:
    """
    Build RAG prompt from question and Graphiti facts
    
    Args:
        question: User's question
        context: Dictionary with "facts" key (from Graphiti search)
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    
    facts = context.get("facts", [])
    
    # Build context string from facts
    context_parts = []
    
    if facts:
        context_parts.append("=== KNOWLEDGE FROM DIVING MANUALS ===\n")
        for idx, fact_data in enumerate(facts, 1):
            fact = fact_data.get("fact", "")
            relation_type = fact_data.get("relation_type", "")
            valid_at = fact_data.get("valid_at", "")
            
            context_parts.append(
                f"[Fact {idx} - {relation_type}]\n"
                f"{fact}\n"
                f"Valid: {valid_at if valid_at else 'Current'}"
            )
    
    context_str = "\n\n".join(context_parts)
    
    # System prompt (DiveTeacher-specific)
    system_prompt = """You are DiveTeacher, an AI assistant specialized in scuba diving education.

CRITICAL RULES:
1. Answer ONLY using information from the provided knowledge facts
2. If context is insufficient, say "I don't have enough information in the diving manuals to answer that question accurately"
3. NEVER make up or infer information not present in the context
4. Cite facts: [Fact 1], [Fact 2] when answering
5. Be concise but thorough
6. Use technical diving terms accurately
7. For FFESSM/SSI procedures, cite exact source material

Your goal: Provide accurate, grounded answers that diving students and instructors can trust for their training and safety."""
    
    # User prompt
    if context_parts:
        user_prompt = f"""Knowledge from diving manuals:

{context_str}

---

Question: {question}

Answer based ONLY on the knowledge above. Cite your facts:"""
    else:
        user_prompt = f"""No relevant knowledge found in diving manuals.

Question: {question}

Please explain you don't have enough information to answer this accurately."""
    
    return system_prompt, user_prompt


async def rag_stream_response(
    question: str, 
    temperature: float = 0.7,
    max_tokens: int = 2000,
    group_ids: List[str] = None
) -> AsyncGenerator[str, None]:
    """
    RAG chain: Retrieve (Graphiti) → Build prompt → Stream LLM response
    
    Args:
        question: User's question
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens to generate
        group_ids: Filter by group_ids (multi-tenant)
        
    Yields:
        Response tokens as they are generated
    """
    
    # Step 1: Retrieve context via Graphiti
    context = await retrieve_context(question, group_ids=group_ids)
    
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
    max_tokens: int = 2000,
    group_ids: List[str] = None
) -> Dict[str, Any]:
    """
    RAG query with full response (non-streaming)
    
    Args:
        question: User's question
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens to generate
        group_ids: Filter by group_ids (multi-tenant)
        
    Returns:
        Dictionary with answer, context, and metadata
    """
    
    # Retrieve context
    context = await retrieve_context(question, group_ids=group_ids)
    
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
        "num_sources": len(context.get("facts", []))
    }
