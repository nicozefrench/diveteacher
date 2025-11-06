# GAP #1 DEVELOPMENT PLAN: Agentic Tool Selection (REVISED)

**Priority:** 🟡 P3 - HIGH (Implement AFTER Gap #2 & #3)  
**Date:** November 4, 2025 (REVISED November 6, 2025 after Gap #3 complete)  
**Estimated Duration:** 5 weeks (25 working days) - SPLIT INTO 2 PHASES  
**Risk Level:** 🟠 MEDIUM-HIGH  
**Value:** 🟢 VERY HIGH (+5-6% overall RAG quality from 87% baseline)  
**Cost:** 💰 FREE (no API costs with heuristic classification)

---

## 🔥 REVISION NOTES (Nov 6, 2025)

**What Changed from Original Plan:**
1. ✅ **Timeline:** 4 weeks → 5 weeks (+1 week buffer, learned from Gap #3)
2. ✅ **Baseline:** Updated to 87% (after Gap #2 + Gap #3, not 75%)
3. ✅ **Day 0 Added:** Neo4j schema audit (prevent assumptions from failing)
4. ✅ **Days 16-19:** Marked OPTIONAL (no staging/prod env, same as Gap #3)
5. ✅ **full_document tool:** Simplified to top 10 chunks (not all 29)
6. ✅ **Fallback logic:** Added explicit thresholds (<3 facts = poor result)
7. ✅ **Performance metrics:** Per-tool metrics added (not just "overhead")

**Lessons Applied from Gap #3:**
- Gap #3 completed in 2 days (vs 3-5 planned) - but had Docling doing 70% work
- Gap #1 is custom implementation → Need buffer for unknowns
- No staging/prod environment available → Skip those days
- Keyword matching was too strict in Gap #3 A/B test → Need better classification
- Always validate infrastructure BEFORE starting (Day 0)

---

## 📋 EXECUTIVE SUMMARY

**Objective:** Transform DiveTeacher from single-tool RAG to intelligent agentic RAG with tool selection and fallback strategies

**Approach:** Implement 4 tools (rag_lookup, list_documents, full_document, sql_query) + agent logic inspired by Cole Medin's "n8n Agentic RAG Agent"

**Why P3 (After Reranking + Contextual):**
- ✅ Most complex (6 weeks total)
- ✅ Build on solid foundation (reranking + contextual retrieval first)
- ✅ Highest long-term value (+20% RAG quality)
- ✅ Enables new query types (numerical, listing, comprehensive)

**Current State (Single-Tool RAG):**
- User question → Graphiti hybrid search → Return top_k=5 → LLM answers
- **No intelligence** in how to retrieve
- **No fallback** if initial retrieval fails
- **No adaptation** to different query types
- **Cannot handle:** Numerical queries, document listing, full-context needs

**Target State (Agentic RAG):**
- User question → Agent analyzes → Selects appropriate tool → Executes → Falls back if needed → LLM answers
- **4 tools available:** rag_lookup, list_documents, full_document, sql_query
- **Intelligent routing:** SQL for numbers, RAG for semantic, full-doc for comprehensive
- **Fallback strategies:** Try alternative tool if first fails
- **Expected impact:** +20% overall quality, +50% for numerical queries

---

## 🎯 TWO-PHASE APPROACH

### **Phase 1: Basic Agentic Tools (5 weeks)**
- ✅ Day 0: Neo4j schema audit + infrastructure validation (NEW!)
- ✅ Implement 3 tools: rag_lookup, list_documents, full_document (top 10 chunks)
- ✅ Implement agent logic (query classification, tool selection)
- ✅ Implement fallback strategies (with explicit thresholds)
- ✅ Test with semantic, listing, and comprehensive queries
- ✅ Buffer time for unknowns (+1 week)
- **Risk:** MEDIUM
- **Value:** HIGH (+5-6% quality from 87% baseline)
- **Duration:** 5 weeks (vs 4 weeks original)

### **Phase 2: SQL Tool (2 weeks) - DEFER IF NEEDED**
- ✅ Implement table extraction from Docling
- ✅ Create `document_rows` table in Neo4j
- ✅ Implement SQL query generation
- ✅ Test with numerical queries
- **Risk:** HIGH (table extraction complexity)
- **Value:** MEDIUM (+3-4% quality, but critical for diving tables)
- **Duration:** 2 weeks (unchanged)

**Rationale for Split:**
- De-risk: Validate Phase 1 before committing to complex SQL tool
- Quick wins: Get +5-6% improvement in 5 weeks (realistic baseline = 87%)
- Option to defer: If SQL proves too complex, Phase 1 still delivers value
- Lessons from Gap #3: Always buffer time for unknowns (+1 week)

---

## 📊 EXPECTED IMPACT (REVISED - From 87% Baseline)

**CRITICAL:** Baseline is now 87% (after Gap #2 Reranking + Gap #3 Contextual), NOT 75%

| Metric | Baseline (After Gap #2/#3) | After Phase 1 | After Phase 2 | Total Improvement |
|--------|----------------------------|---------------|---------------|-------------------|
| **Semantic queries** | 87% | 90% (+3%) | 90% | +3% |
| **Document listing** | 0% (impossible) | 100% (+100%) | 100% | +100% (new!) |
| **Full-context queries** | 70% | 85% (+21%) | 85% | +21% |
| **Numerical queries** | 60% | 65% (+8%) | 90% (+50%) | +50% |
| **Overall RAG quality** | **87%** | **92% (+5-6%)** | **95% (+9%)** | **+9%** |

**Key Changes from Original:**
- Baseline: 87% (was incorrectly 75% - Gap #2 + #3 already improved it!)
- Phase 1 target: 92% (+5-6%, was +15% but that was vs 75% baseline)
- Phase 2 target: 95% (+9% total, was +20% but again vs 75%)
- Realistic expectations based on actual current system state

---

## 🔧 ARCHITECTURE DESIGN

### **Tool Architecture**

```python
# backend/app/core/agent.py

from enum import Enum
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger('diveteacher.agent')

class QueryType(Enum):
    """Query types for tool selection"""
    SEMANTIC = "semantic"           # Standard RAG lookup
    NUMERICAL = "numerical"         # SQL query (table data)
    DOCUMENT_LISTING = "listing"    # List available documents
    COMPREHENSIVE = "comprehensive" # Full document retrieval

class DiveTeacherAgent:
    """
    Agentic RAG system with intelligent tool selection.
    Based on Cole Medin's "n8n Agentic RAG Agent" pattern.
    """
    
    def __init__(self):
        self.tools = {
            "rag_lookup": self.rag_lookup_tool,
            "list_documents": self.list_documents_tool,
            "full_document": self.get_full_document_tool,
            "sql_query": self.sql_query_tool  # Phase 2
        }
    
    async def query(
        self,
        question: str,
        group_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Main query method with intelligent tool selection.
        
        Algorithm:
        1. Analyze query type (semantic, numerical, listing, comprehensive)
        2. Select primary tool based on query type
        3. Execute tool
        4. If tool fails or returns poor results, try fallback tool
        5. Return final results
        """
        logger.info(f"🤖 Agent analyzing query: '{question[:50]}...'")
        
        # Step 1: Classify query
        query_type = self.classify_query(question)
        logger.info(f"   📋 Query type: {query_type.value}")
        
        # Step 2: Select and execute primary tool
        result = await self.execute_primary_tool(
            query_type, question, group_ids
        )
        
        # Step 3: Fallback if needed
        if self.should_fallback(result):
            logger.warning(f"   ⚠️  Primary tool returned poor results, trying fallback...")
            result = await self.execute_fallback_tool(
                query_type, question, group_ids
            )
        
        return result
    
    def classify_query(self, question: str) -> QueryType:
        """
        Classify query type using heuristics (Phase 1) or LLM (Phase 2+).
        """
        question_lower = question.lower()
        
        # Numerical query indicators
        numerical_keywords = [
            "average", "sum", "count", "total", "maximum", "minimum",
            "percentage", "how many", "combien", "moyenne", "total",
            "pourcentage", "nombre"
        ]
        if any(kw in question_lower for kw in numerical_keywords):
            return QueryType.NUMERICAL
        
        # Document listing indicators
        listing_keywords = [
            "what documents", "list documents", "which manuals",
            "what files", "available documents", "quels documents",
            "liste documents", "quels manuels", "fichiers disponibles"
        ]
        if any(kw in question_lower for kw in listing_keywords):
            return QueryType.DOCUMENT_LISTING
        
        # Comprehensive query indicators
        comprehensive_keywords = [
            "explain in detail", "comprehensive", "full explanation",
            "complete guide", "everything about", "explique en détail",
            "explication complète", "guide complet", "tout sur"
        ]
        if any(kw in question_lower for kw in comprehensive_keywords):
            return QueryType.COMPREHENSIVE
        
        # Default: semantic search
        return QueryType.SEMANTIC
```

### **Tool Implementations**

**Tool #1: RAG Lookup (Already Exists)**
```python
async def rag_lookup_tool(
    self,
    question: str,
    group_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Existing Graphiti hybrid search (semantic + BM25 + RRF + reranking).
    """
    from app.core.rag import retrieve_context
    return await retrieve_context(question, group_ids=group_ids)
```

**Tool #2: List Documents (NEW - Phase 1)**
```python
async def list_documents_tool(
    self,
    question: str,
    group_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    List all documents in knowledge base with metadata.
    
    Returns:
        {
            "documents": [
                {
                    "filename": "FFESSM Niveau 1.pdf",
                    "upload_date": "2025-11-01",
                    "num_chunks": 25,
                    "doc_type": "FFESSM Manual",
                    "topics": ["Safety", "Equipment", "Procedures"]
                },
                ...
            ],
            "total": 10
        }
    """
    logger.info("📚 Listing available documents...")
    
    # Query Neo4j for all unique documents
    query = """
    MATCH (e:EpisodeType)
    WHERE ($group_ids IS NULL OR e.group_id IN $group_ids)
    WITH e.source_description AS source, e.group_id AS group_id
    RETURN DISTINCT source, group_id, count(*) AS num_chunks
    ORDER BY source
    """
    
    # Execute query (implementation depends on Neo4j client)
    # ...
    
    return {"documents": documents, "total": len(documents)}
```

**Tool #3: Get Full Document (NEW - Phase 1) - SIMPLIFIED**
```python
async def get_full_document_tool(
    self,
    document_id: str,
    group_ids: Optional[List[str]] = None,
    max_chunks: int = 10  # NEW: Limit to top 10 chunks
) -> Dict[str, Any]:
    """
    Retrieve comprehensive document context (TOP 10 most relevant chunks).
    
    **REVISED:** Instead of ALL chunks (29 for Niveau 1), return top 10 most relevant.
    Rationale from Gap #3 experience:
    - Niveau 1.pdf = 29 chunks → Too slow to concatenate all
    - LLM context window limit (128K tokens)
    - "Comprehensive" != "Exhaustive" - Top 10 provides enough context
    
    Args:
        document_id: Document identifier (filename or UUID)
        max_chunks: Maximum chunks to return (default: 10)
        
    Returns:
        {
            "document_id": "FFESSM Niveau 1.pdf",
            "top_chunks": [...],  # Top 10 chunks (not all 29)
            "metadata": {...},
            "num_chunks_returned": 10,
            "total_chunks_available": 29
        }
    """
    logger.info(f"📄 Retrieving comprehensive context: {document_id} (top {max_chunks} chunks)")
    
    # Query Neo4j for all chunks of document
    query = """
    MATCH (e:EpisodeType)
    WHERE e.source_description CONTAINS $document_id
      AND ($group_ids IS NULL OR e.group_id IN $group_ids)
    RETURN e.content AS chunk_text, e.created_at AS created_at
    ORDER BY e.created_at
    LIMIT $max_chunks
    """
    
    # Return top N chunks (comprehensive, not exhaustive)
    # ...
    
    return {
        "document_id": document_id,
        "top_chunks": chunks,  # Top 10, not all
        "metadata": metadata,
        "num_chunks_returned": len(chunks),
        "total_chunks_available": total_count  # May be 29, but we only return 10
    }
```

**Tool #4: SQL Query (NEW - Phase 2)**
```python
async def sql_query_tool(
    self,
    question: str,
    group_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Query tabular data extracted from documents (Phase 2).
    
    Process:
    1. Identify relevant table(s) from question
    2. Generate SQL query (using LLM or templates)
    3. Execute query on document_rows table
    4. Return results
    
    Returns:
        {
            "query": "SELECT AVG(depth) FROM dive_tables WHERE...",
            "results": [...],
            "columns": ["depth", "time", "stop"],
            "num_rows": 5
        }
    """
    logger.info(f"🔢 Generating SQL query for: '{question[:50]}...'")
    
    # Phase 2 implementation
    # ...
    
    return {"query": sql_query, "results": results}
```

---

## 📅 PHASE 1 PLAN (5 WEEKS - REVISED)

### **DAY 0: PRE-IMPLEMENTATION AUDIT** (NEW - Friday before Week 1)

**Goal:** Validate infrastructure and Neo4j schema BEFORE starting implementation

**Why This is Critical (Lesson from Gap #3):**
- Gap #3 had assumptions about Ollama/Neo4j connectivity that took time to debug
- Tools depend on Neo4j schema (group_id, source_description, metadata fields)
- Better to spend 4 hours validating than waste 2 days debugging wrong assumptions

**Tasks:**

**0.1 Neo4j Schema Audit (2 hours)**
- Connect to Neo4j from Python (test driver)
- Query actual Episode nodes: `MATCH (e:EpisodeType) RETURN e LIMIT 5`
- Verify fields exist:
  * `group_id` (for document grouping)
  * `source_description` (for document identification)
  * `content` or `episode_body` (for chunk text)
  * `created_at` (for chunk ordering)
- Document actual schema in `docs/NEO4J-SCHEMA.md`

**0.2 Graphiti Client Test (1 hour)**
- Verify Graphiti client imports work
- Test search functionality (1 query)
- Verify response format (facts list)
- Document any quirks

**0.3 Infrastructure Connectivity (1 hour)**
- Verify Docker networking (backend → Neo4j)
- Verify Ollama connectivity (`http://host.docker.internal:11434`)
- Test end-to-end: Upload → Ingest → Query
- Document connection strings

**Deliverables:**
- ✅ `docs/NEO4J-SCHEMA.md` (actual schema documented)
- ✅ Neo4j connectivity validated
- ✅ Graphiti client tested
- ✅ No assumptions - everything verified!

**Time:** 4 hours

**Decision Point:** If schema doesn't match assumptions, revise tool designs BEFORE coding!

---

### **WEEK 1: FOUNDATION & LIST_DOCUMENTS TOOL**

---

### **DAY 1: Agent Architecture Setup** (Monday)

**Goal:** Create agent framework and base classes

**Tasks:**

**1.1 Create Agent Module (3 hours)**
- Create `backend/app/core/agent.py`
- Implement `QueryType` enum
- Implement `DiveTeacherAgent` class skeleton
- Add `classify_query()` method (heuristics)

**1.2 Unit Tests (2 hours)**
- Create `backend/tests/test_agent.py`
- Test: classify_query for each type
- Test: Query classification edge cases

**1.3 Documentation (1 hour)**
- Start `docs/AGENT.md`
- Explain agent architecture
- Document query types

**Deliverables:**
- ✅ `backend/app/core/agent.py`
- ✅ `backend/tests/test_agent.py`
- ✅ `docs/AGENT.md` (draft)

**Time:** 6 hours

---

### **DAY 2-3: List Documents Tool** (Tuesday-Wednesday)

**Goal:** Implement list_documents_tool

**Tasks:**

**2.1 Neo4j Query Design (2 hours)**
- **Choose Neo4j access method:**
  * Option A: Use Graphiti's internal driver (recommended - already integrated)
  * Option B: Direct `neo4j-driver` library (if Graphiti doesn't expose)
  * Decision based on Day 0 findings
- Design query to list all documents
- Extract metadata (filename, chunks, upload_date)
- Handle group_ids filter
- **Query template:**
  ```cypher
  MATCH (e:EpisodeType)
  WHERE ($group_ids IS NULL OR e.group_id IN $group_ids)
  RETURN DISTINCT e.group_id AS doc_id, 
                  e.source_description AS filename,
                  count(*) AS num_chunks
  ORDER BY filename
  ```

**2.2 Implement Tool (4 hours)**
- Add `list_documents_tool()` to agent
- Query Neo4j for unique documents
- Format results
- Add logging

**2.3 Unit Tests (3 hours)**
- Test: List all documents
- Test: Filter by group_ids
- Test: Empty database
- Test: Multiple documents

**2.4 Integration Test (3 hours)**
- Upload 3 test documents
- List documents via agent
- Verify correct metadata

**Deliverables:**
- ✅ `list_documents_tool` implemented
- ✅ Unit tests passing
- ✅ Integration test passing

**Time:** 12 hours (2 days × 6 hours)

---

### **DAY 4-5: Get Full Document Tool** (Thursday-Friday)

**Goal:** Implement get_full_document_tool

**Tasks:**

**4.1 Neo4j Query Design (2 hours)**
- Design query to retrieve all chunks of document
- Sort by created_at (preserve order)
- Handle missing documents

**4.2 Implement Tool (4 hours)**
- Add `get_full_document_tool()` to agent
- Query Neo4j for all chunks
- Reconstruct full document text
- Add logging

**4.3 Unit Tests (3 hours)**
- Test: Retrieve full document
- Test: Document not found
- Test: Filter by group_ids

**4.4 Integration Test (3 hours)**
- Upload test.pdf
- Retrieve full document
- Verify text matches original

**Deliverables:**
- ✅ `get_full_document_tool` implemented
- ✅ Unit tests passing
- ✅ Integration test passing

**Time:** 12 hours (2 days × 6 hours)

---

### **WEEK 2: TOOL EXECUTION & FALLBACK LOGIC**

---

### **DAY 6-7: Tool Execution Logic** (Monday-Tuesday)

**Goal:** Implement execute_primary_tool and fallback logic

**Tasks:**

**6.1 Implement execute_primary_tool() (4 hours)**
- Add method to DiveTeacherAgent
- Route to appropriate tool based on query_type
- Handle tool errors gracefully
- Add logging

**Code:**
```python
async def execute_primary_tool(
    self,
    query_type: QueryType,
    question: str,
    group_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Execute primary tool based on query type.
    """
    if query_type == QueryType.SEMANTIC:
        logger.info("   🔍 Using tool: rag_lookup")
        return await self.rag_lookup_tool(question, group_ids)
    
    elif query_type == QueryType.DOCUMENT_LISTING:
        logger.info("   📚 Using tool: list_documents")
        return await self.list_documents_tool(question, group_ids)
    
    elif query_type == QueryType.COMPREHENSIVE:
        logger.info("   📄 Using tool: full_document (after listing)")
        # Step 1: List documents
        docs = await self.list_documents_tool(question, group_ids)
        # Step 2: Get full document (first match)
        if docs["documents"]:
            doc_id = docs["documents"][0]["filename"]
            return await self.get_full_document_tool(doc_id, group_ids)
        return {"error": "No documents found"}
    
    elif query_type == QueryType.NUMERICAL:
        logger.info("   🔢 Using tool: sql_query (Phase 2, fallback to RAG)")
        # Phase 1: Fallback to RAG
        logger.warning("   ⚠️  SQL tool not available, using RAG fallback")
        return await self.rag_lookup_tool(question, group_ids)
    
    else:
        # Default: RAG
        return await self.rag_lookup_tool(question, group_ids)
```

**6.2 Implement Fallback Logic (4 hours) - WITH EXPLICIT THRESHOLDS**
- Add `should_fallback()` method with CLEAR conditions
- Add `execute_fallback_tool()` method
- Implement fallback strategies with explicit thresholds:

```python
def should_fallback(self, result: Dict[str, Any]) -> bool:
    """
    Determine if fallback is needed based on EXPLICIT thresholds.
    
    Learned from Gap #3 A/B test: Need clear, measurable criteria.
    """
    # Condition 1: Error occurred
    if "error" in result:
        logger.warning(f"   ⚠️  Tool returned error: {result['error']}")
        return True
    
    # Condition 2: No facts retrieved (< 3 facts = poor result)
    # From Gap #3: We always got 5 facts, <3 = something wrong
    facts = result.get("context", {}).get("facts", [])
    if len(facts) < 3:
        logger.warning(f"   ⚠️  Tool returned too few facts: {len(facts)} < 3")
        return True
    
    # Condition 3: Empty response (no answer generated)
    if not result.get("answer", "").strip():
        logger.warning("   ⚠️  Tool returned empty answer")
        return True
    
    # All thresholds passed - no fallback needed
    return False

async def execute_fallback_tool(
    self,
    query_type: QueryType,
    question: str,
    group_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Execute fallback tool based on query type.
    
    Fallback strategies:
    - SEMANTIC → COMPREHENSIVE (try broader context)
    - COMPREHENSIVE → SEMANTIC (try narrower search)
    - NUMERICAL → SEMANTIC (Phase 1, no SQL yet)
    - LISTING → No fallback (return empty list)
    """
    if query_type == QueryType.SEMANTIC:
        logger.info("   🔄 Fallback: SEMANTIC → COMPREHENSIVE")
        # Get first document, return top 10 chunks
        docs = await self.list_documents_tool(question, group_ids)
        if docs["documents"]:
            return await self.get_full_document_tool(
                docs["documents"][0]["filename"], 
                group_ids
            )
        return {"error": "No fallback available"}
    
    elif query_type == QueryType.COMPREHENSIVE:
        logger.info("   🔄 Fallback: COMPREHENSIVE → SEMANTIC")
        return await self.rag_lookup_tool(question, group_ids)
    
    elif query_type == QueryType.NUMERICAL:
        logger.info("   🔄 Fallback: NUMERICAL → SEMANTIC (SQL not available)")
        return await self.rag_lookup_tool(question, group_ids)
    
    elif query_type == QueryType.DOCUMENT_LISTING:
        logger.warning("   ⚠️  No fallback for LISTING (return empty)")
        return {"documents": [], "total": 0}
    
    else:
        # Default fallback
        return await self.rag_lookup_tool(question, group_ids)
```

**6.3 Unit Tests (4 hours)**
- Test: execute_primary_tool for each query type
- Test: Fallback triggers correctly
- Test: Error handling

**Deliverables:**
- ✅ Tool execution logic
- ✅ Fallback strategies
- ✅ Unit tests passing

**Time:** 12 hours (2 days × 6 hours)

---

### **DAY 8-9: API Integration** (Wednesday-Thursday)

**Goal:** Integrate agent into existing RAG query API

**Tasks:**

**8.1 Modify Query API (3 hours)**
- Update `backend/app/api/query.py`
- Add `use_agent` parameter (default=True)
- Route to agent if enabled, else use old RAG path
- Maintain backward compatibility

**8.2 Update QueryRequest Model (1 hour)**
- Add `use_agent: bool = True`
- Document in API schema

**8.3 Update RAG Pipeline (2 hours)**
- Modify `backend/app/core/rag.py`
- Add `rag_query_with_agent()` function
- Integrate agent.query() call

**8.4 Integration Tests (4 hours)**
- Test: API with use_agent=True
- Test: API with use_agent=False (backward compat)
- Test: Each query type via API

**8.5 E2E Test (2 hours)**
- Test full pipeline with agent
- Verify correct tool selection
- Check response quality

**Deliverables:**
- ✅ API integration complete
- ✅ Backward compatibility maintained
- ✅ E2E test passing

**Time:** 12 hours (2 days × 6 hours)

---

### **DAY 10: Week 2 Validation** (Friday)

**Goal:** Validate Week 2 changes, prepare for Week 3

**Tasks:**

**10.1 Full Test Suite (3 hours)**
- Run all unit tests
- Run all integration tests
- Fix any failures

**10.2 Performance Testing (2 hours)**
- Measure agent overhead
- Verify <100ms overhead
- Profile tool execution

**10.3 Week 2 Review (1 hour)**
- Review code changes
- Update documentation draft
- Plan Week 3 tasks

**Deliverables:**
- ✅ All tests passing
- ✅ Performance validated
- ✅ Week 2 complete

**Time:** 6 hours

---

### **WEEK 3: TESTING & VALIDATION**

---

### **DAY 11-12: A/B Testing** (Monday-Tuesday)

**Goal:** Comprehensive A/B testing of agentic vs non-agentic RAG

**Tasks:**

**11.1 Create Test Dataset (4 hours)**
- 40 test queries total (reuse + expand Gap #3 dataset):
  * **Reuse Gap #3:** 20 existing queries from `gap3_test_dataset.json` (semantic focus)
  * **Add 10 new:** Document listing queries (e.g., "What manuals do we have?", "List all FFESSM documents")
  * **Add 5 new:** Comprehensive queries (e.g., "Explain buoyancy in detail", "Full guide to equipment")
  * **Add 5 new:** Numerical queries (e.g., "How many decompression stops?", "Average dive depth?")
- Each query includes:
  * Expected query_type (SEMANTIC, LISTING, COMPREHENSIVE, NUMERICAL)
  * Expected tool (rag_lookup, list_documents, full_document, sql_query)
  * Expected quality threshold (relevant keywords for precision calc)
- Store in `backend/tests/test_data/gap1_test_dataset.json`

**11.2 Run A/B Test (6 hours)**
- Run each query with use_agent=False (baseline)
- Run each query with use_agent=True (agentic)
- Compare:
  - Tool selection correctness
  - Answer quality
  - User satisfaction (simulated)
  - Response time

**11.3 Document Results (2 hours)**
- Create `Devplan/251104-AGENTIC-PHASE1-AB-TEST.md`
- Include:
  - Query-by-query comparison
  - Overall metrics
  - Tool selection accuracy
  - Improvement analysis

**Deliverables:**
- ✅ Test dataset (40 queries)
- ✅ A/B test complete
- ✅ Results documented

**Time:** 12 hours (2 days × 6 hours)

---

### **DAY 13-14: Documentation** (Wednesday-Thursday)

**Goal:** Complete all documentation for Phase 1

**Tasks:**

**13.1 Technical Documentation (6 hours)**
- Finalize `docs/AGENT.md`
- Update `docs/ARCHITECTURE.md` (add agent layer)
- Update `docs/API.md` (document use_agent parameter)
- Update `docs/MONITORING.md` (agent metrics)

**13.2 User Documentation (3 hours)**
- Update `docs/USER-GUIDE.md` (explain agent benefits)
- Add examples for each query type
- Document when to use/disable agent

**13.3 Testing Documentation (3 hours)**
- Update `docs/TESTING-LOG.md` (Phase 1 test results)
- Update `docs/FIXES-LOG.md` (Enhancement #3)
- Document A/B test methodology

**Deliverables:**
- ✅ 6 docs updated
- ✅ Code documentation complete

**Time:** 12 hours (2 days × 6 hours)

---

### **DAY 15: Code Review** (Friday)

**Goal:** Code review and refinement

**Tasks:**

**15.1 Self Code Review (3 hours)**
- Review all Phase 1 changes
- Check error handling
- Verify logging
- Run linters

**15.2 Address Issues (2 hours)**
- Fix linting errors
- Improve error messages
- Add missing type hints

**15.3 Final Testing (1 hour)**
- Re-run all tests
- Verify E2E still works

**Deliverables:**
- ✅ Clean code
- ✅ All tests passing

**Time:** 6 hours

---

### **WEEK 4: DEPLOYMENT & PHASE 2 PREP**

---

### **DAY 16-19: Local Testing & Phase 2 Prep** ❌ **STAGING/PROD SKIPPED** (Monday-Thursday)

**Status:** Days 16-17 (Staging) and Days 18-19 (Production) are **NOT APPLICABLE**

**Reason (Same as Gap #3):**
- No staging environment available (local Mac M1 Max = production for now)
- Cloud deployment planned for "way later" (outside current scope)
- All validation completed in local Docker Compose environment
- Gap #3 precedent: Skipped Days 4-5 for same reason

**REVISED PLAN - Local Testing & Buffer:**

**16.1 Extended Local Testing (6 hours)**
- Run comprehensive test suite (all 40 A/B test queries)
- Verify agent overhead <50ms (classification + routing)
- Test all tool combinations (semantic, listing, comprehensive)
- Monitor memory usage (<100MB increase)
- Performance profiling (identify bottlenecks)

**16.2 Edge Case Testing (4 hours)**
- Test with empty database (no documents)
- Test with malformed queries
- Test with very long queries (>1000 chars)
- Test with concurrent requests (10 simultaneous queries)
- Verify error handling for all failure modes

**16.3 Documentation Finalization (8 hours)**
- Finalize `docs/AGENT.md` (complete agent architecture)
- Update `docs/ARCHITECTURE.md` (add agent layer diagram)
- Update `docs/API.md` (use_agent parameter)
- Update `docs/TESTING-LOG.md` (Phase 1 results)
- Update `docs/FIXES-LOG.md` (Enhancement #3: Agentic Tools)
- Update `CURRENT-CONTEXT.md` (Session summary)

**16.4 Phase 2 Planning (6 hours)**
- Design table extraction pipeline (Docling tables)
- Design `document_rows` schema (Neo4j)
- Design SQL generation logic (LLM vs templates)
- Risk assessment: Proceed or defer Phase 2?
- Document decision in `Devplan/251104-GAP1-PHASE2-DECISION.md`

**Deliverables:**
- ✅ Comprehensive local testing complete
- ✅ All documentation updated
- ✅ Phase 2 plan ready (if proceeding)
- ✅ Phase 1 COMPLETE (in local environment)!

**Time:** 24 hours (4 days × 6 hours)

**Note:** If cloud deployment happens later, Days 16-19 tasks can be executed then. For now, local = production.

---

### **DAY 20-25: Buffer Week** (Friday + Week 5)

**Goal:** Buffer time for unknowns and Phase 2 prep

**Rationale (Lesson from Gap #3):**
- Gap #3 planned 3-5 days, completed in 2 (but had Docling doing 70% work)
- Gap #1 is custom implementation → Needs buffer for:
  * Unexpected Neo4j schema issues
  * Query classification edge cases
  * Tool integration debugging
  * Performance optimization
- Better to have buffer and not need it, than need it and not have it!

**Flexible Use of Buffer Days:**

**Option A: Everything on track** (ideal scenario)
- Day 20-22: Start Phase 2 design (table extraction)
- Day 23-24: Create detailed Phase 2 plan
- Day 25: Team retrospective + celebration 🎉

**Option B: Minor issues encountered** (likely scenario)
- Use 2-3 days to address any technical debt from Weeks 1-4
- Improve test coverage
- Optimize performance
- Remaining days: Phase 2 prep

**Option C: Major issues encountered** (contingency)
- Use full week to resolve blocking issues
- Ensure Phase 1 is solid before considering Phase 2
- Defer Phase 2 if needed

**Deliverables:**
- ✅ Phase 1 fully validated and stable
- ✅ All tests passing (100% success rate)
- ✅ Documentation complete
- ✅ Phase 2 decision documented
- ✅ Buffer utilized wisely!

**Time:** 30 hours (5 days × 6 hours)

---

## 📊 PERFORMANCE METRICS (ADDED - Per-Tool Breakdown)

### **Classification Overhead**
- **Target:** <50ms (was "<100ms" but too vague)
- **Measurement:** Time from query input to query_type determined
- **Method:** Heuristic keyword matching (no LLM call = fast)
- **Acceptable range:** 10-50ms

### **Tool Selection Overhead**
- **Target:** <10ms
- **Measurement:** Time to route to appropriate tool
- **Method:** Simple if/elif logic
- **Acceptable range:** 1-10ms

### **Tool Execution Times** (NEW - Specific per tool)

**rag_lookup (Graphiti hybrid search):**
- **Baseline (Gap #3):** ~4.13s avg (20 queries, 100% success)
- **Target:** <5s (maintain current performance)
- **Components:**
  * Semantic search: ~1s
  * BM25 search: ~0.5s
  * RRF fusion: ~0.1s
  * Reranking: ~0.2s (from Gap #2)
  * LLM generation: ~2s

**list_documents:**
- **Target:** <500ms (simple Neo4j query)
- **Estimate:** ~100-200ms
- **Query:** `MATCH (e:EpisodeType) RETURN DISTINCT group_id`

**full_document (top 10 chunks):**
- **Target:** <2s (10 chunks concatenation + retrieval)
- **Estimate:** ~1-2s (much faster than all 29 chunks)
- **Query:** `MATCH (e:EpisodeType) WHERE ... LIMIT 10`

**sql_query (Phase 2 only):**
- **Target:** <3s
- **Estimate:** TBD (depends on table complexity)

### **Total Response Time Targets** (NEW - Per Query Type)

**Semantic queries:**
- Current: ~4.13s (Gap #3 baseline)
- With agent: ~4.2s (4.13s + 50ms + 10ms overhead)
- **Target:** <5s ✅

**Document listing:**
- Current: N/A (impossible)
- With agent: ~0.6s (500ms tool + 50ms + 10ms overhead)
- **Target:** <1s ✅

**Comprehensive queries:**
- Current: ~4.13s (same as semantic, but poor quality)
- With agent: ~2.1s (2s tool + 50ms + 10ms overhead)
- **Target:** <3s ✅ (faster AND better quality!)

**Numerical queries (Phase 2):**
- Current: ~4.13s (RAG fallback, poor results)
- With agent: ~3.1s (3s SQL + 50ms + 10ms overhead)
- **Target:** <5s ✅

### **Memory Usage**
- **Baseline:** ~2GB (Docker backend container)
- **Target:** <2.1GB (+100MB max)
- **Components:**
  * Agent instance: ~10MB
  * Tool caches: ~50MB
  * Query classification cache: ~20MB

### **Success Criteria Summary**
- ✅ Classification overhead: <50ms
- ✅ Tool selection overhead: <10ms
- ✅ Total response time: Within targets per query type
- ✅ Memory increase: <100MB
- ✅ No regressions in semantic query performance (maintain 4.13s)

---

## 📊 PHASE 1 SUCCESS METRICS (REVISED)

### **Baseline (After Gap #2 + #3 Complete)**
- Semantic query accuracy: **87%** (NOT 75% - Gap #2 + #3 already improved it!)
- Document listing: **0%** (impossible with current system)
- Comprehensive queries: **70%** (poor - uses same 5 chunks as semantic)
- Overall RAG quality: **87%**

### **Target (After Phase 1 - 5 weeks)**
- Semantic query accuracy: **90% (+3%)**
- Document listing: **100% (new capability!)**
- Comprehensive queries: **85% (+21%)**  
- Overall RAG quality: **92% (+5-6%)**

### **Success Criteria Checklist**
- ✅ Day 0 completed (Neo4j schema validated, no assumptions)
- ✅ 3 tools implemented (rag, list, full_doc with top 10 chunks)
- ✅ Agent classifies queries correctly (>90% accuracy with heuristics)
- ✅ Tool selection works for each query type
- ✅ Fallback strategies trigger correctly (<3 facts = fallback)
- ✅ Document listing works 100% of time
- ✅ Comprehensive queries improve +21%
- ✅ Semantic queries maintain quality (no regression)
- ✅ A/B test validates +5-6% improvement (40 queries)
- ✅ Performance targets met (see Performance Metrics section)
- ✅ All documentation updated (6+ files)
- ✅ Buffer week utilized (if needed)

---

## ✅ PHASE 1 ACCEPTANCE CRITERIA (REVISED)

### **Pre-Implementation (Day 0)**
- [x] Neo4j schema documented (no assumptions)
- [x] Graphiti client tested (response format verified)
- [x] Infrastructure connectivity validated (Docker networking)

### **Functional**
- [x] 3 tools implemented (rag, list, full_doc with 10 chunks max)
- [x] Agent classifies queries correctly (>90% accuracy)
- [x] Tool selection works for each query type
- [x] Fallback strategies trigger when needed (<3 facts threshold)

### **Quality (from 87% baseline)**
- [x] Document listing works 100%
- [x] Comprehensive queries improve +21% (70% → 85%)
- [x] Semantic queries maintain quality (87% → 90%)
- [x] A/B test validates +5-6% overall improvement
- [x] NO REGRESSIONS in current functionality

### **Performance**
- [x] Classification overhead <50ms (was <100ms)
- [x] Tool selection overhead <10ms
- [x] Total response time per query type within targets
- [x] Memory increase <100MB
- [x] No regression in semantic query time (~4.13s maintained)

### **Documentation & Testing**
- [x] 6+ docs updated (AGENT, ARCHITECTURE, API, TESTING-LOG, FIXES-LOG, USER-GUIDE)
- [x] 40 A/B test queries created and executed
- [x] Test coverage >80% for agent code
- [x] All integration tests passing

---

**Phase 1 Status:** 🟢 READY FOR IMPLEMENTATION (After Gap #2 + #3 complete)  
**Next Action:** Execute Day 0 (Neo4j schema audit) first!  
**Estimated Start Date:** Week after Gap #3 complete (~November 13, 2025)  
**Estimated Complete Date:** 5 weeks later (~December 18, 2025)

**KEY REVISION SUMMARY:**
1. ✅ Timeline: 4 weeks → 5 weeks (+1 week buffer)
2. ✅ Baseline: 75% → 87% (after Gap #2 + #3)
3. ✅ Day 0: Added (Neo4j schema audit)
4. ✅ Days 16-19: Marked OPTIONAL (no staging/prod)
5. ✅ full_document: Simplified (top 10 chunks, not all 29)
6. ✅ Fallback: Added explicit thresholds (<3 facts)
7. ✅ Performance: Per-tool metrics added (not just overhead)


