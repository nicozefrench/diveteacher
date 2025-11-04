"""
RAG (Retrieval-Augmented Generation) Chain avec Graphiti

This module implements the RAG workflow:
1. Query Graphiti knowledge graph for relevant facts (hybrid search)
2. Optionally rerank results using cross-encoder (ms-marco-MiniLM-L-6-v2)
3. Build prompt with retrieved facts
4. Stream LLM response (Qwen 2.5 7B Q8_0 on Ollama)

Cross-Encoder Reranking (Cole Medin Pattern):
- Retrieve top_k × 4 from Graphiti if reranking enabled
- Rerank to top_k using ms-marco-MiniLM-L-6-v2
- Expected +10-15% retrieval precision improvement
"""

from typing import AsyncGenerator, List, Dict, Any
import logging
from app.core.llm import get_llm
from app.integrations.graphiti import search_knowledge_graph
from app.core.config import settings
from app.core.reranker import get_reranker

logger = logging.getLogger('diveteacher.rag')


async def retrieve_context(
    question: str, 
    top_k: int = None,
    group_ids: List[str] = None,
    use_reranking: bool = None
) -> Dict[str, Any]:
    """
    Retrieve relevant context using Graphiti's hybrid search + Optional Cross-Encoder Reranking
    
    Args:
        question: User's question
        top_k: Number of final results (default: from settings)
        group_ids: Filter by group_ids (multi-tenant)
        use_reranking: Enable cross-encoder reranking (default: from settings)
        
    Returns:
        Dictionary with facts (EntityEdges) from Graphiti
        {
            "facts": List[Dict],  # Relations extraites (optionally reranked)
            "total": int,
            "reranked": bool  # True if reranking was applied
        }
        
    Note:
        - Uses Graphiti native search (semantic + BM25 + RRF)
        - If reranking enabled: retrieves top_k × 4, reranks to top_k
        - Cross-encoder: ms-marco-MiniLM-L-6-v2 (~100ms for 20 facts)
        - Expected: +10-15% retrieval precision with reranking
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K
    
    if use_reranking is None:
        use_reranking = settings.RAG_RERANKING_ENABLED
    
    # Step 1: Retrieve more candidates if reranking enabled
    retrieval_k = top_k * settings.RAG_RERANKING_RETRIEVAL_MULTIPLIER if use_reranking else top_k
    
    logger.info(f"🔍 Retrieving {retrieval_k} facts from Graphiti (reranking={'ON' if use_reranking else 'OFF'})")
    
    # Graphiti hybrid search
    facts = await search_knowledge_graph(
        query=question,
        num_results=retrieval_k,
        group_ids=group_ids
    )
    
    logger.info(f"✅ Graphiti returned {len(facts)} facts")
    
    # Step 2: Rerank if enabled and we have more than top_k facts
    reranked = False
    if use_reranking and len(facts) > top_k:
        logger.info(f"🔁 Reranking {len(facts)} facts to top {top_k}...")
        reranker = get_reranker()
        facts = reranker.rerank(
            query=question,
            facts=facts,
            top_k=top_k
        )
        reranked = True
        logger.info(f"✅ Reranking complete, using top {len(facts)} facts")
    else:
        # No reranking, just truncate
        facts = facts[:top_k]
        if use_reranking:
            logger.info(f"ℹ️  Only {len(facts)} facts returned (≤ top_k={top_k}), no reranking needed")
        else:
            logger.info(f"ℹ️  Using top {len(facts)} facts (reranking disabled)")
    
    return {
        "facts": facts,
        "total": len(facts),
        "reranked": reranked
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
    group_ids: List[str] = None,
    use_reranking: bool = None
) -> AsyncGenerator[str, None]:
    """
    RAG chain: Retrieve (Graphiti) → Optional Rerank → Build prompt → Stream LLM response
    
    Args:
        question: User's question
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens to generate
        group_ids: Filter by group_ids (multi-tenant)
        use_reranking: Enable cross-encoder reranking (default: from settings)
        
    Yields:
        Response tokens as they are generated
    """
    
    # Step 1: Retrieve context via Graphiti (+ optional reranking)
    context = await retrieve_context(question, group_ids=group_ids, use_reranking=use_reranking)
    
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
    group_ids: List[str] = None,
    use_reranking: bool = None
) -> Dict[str, Any]:
    """
    RAG query with full response (non-streaming)
    
    Args:
        question: User's question
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens to generate
        group_ids: Filter by group_ids (multi-tenant)
        use_reranking: Enable cross-encoder reranking (default: from settings)
        
    Returns:
        Dictionary with answer, context, and metadata
    """
    
    # Retrieve context (+ optional reranking)
    context = await retrieve_context(question, group_ids=group_ids, use_reranking=use_reranking)
    
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
        "num_sources": len(context.get("facts", [])),
        "reranked": context.get("reranked", False)
    }
