# GAP #1 DEVELOPMENT PLAN: Agentic Tool Selection

**Priority:** 🟡 P3 - HIGH (Implement AFTER Gap #2 & #3)  
**Date:** November 4, 2025  
**Estimated Duration:** 6 weeks (30 working days) - SPLIT INTO 2 PHASES  
**Risk Level:** 🟠 MEDIUM-HIGH  
**Value:** 🟢 VERY HIGH (+20% overall RAG quality)  
**Cost:** 💰 FREE (no API costs)

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

### **Phase 1: Basic Agentic Tools (4 weeks)**
- ✅ Implement 3 tools: rag_lookup, list_documents, full_document
- ✅ Implement agent logic (query classification, tool selection)
- ✅ Implement fallback strategies
- ✅ Test with semantic, listing, and comprehensive queries
- **Risk:** MEDIUM
- **Value:** HIGH (+15% quality)

### **Phase 2: SQL Tool (2 weeks) - DEFER IF NEEDED**
- ✅ Implement table extraction from Docling
- ✅ Create `document_rows` table in Neo4j
- ✅ Implement SQL query generation
- ✅ Test with numerical queries
- **Risk:** HIGH (table extraction complexity)
- **Value:** MEDIUM (+5% quality, but critical for diving tables)

**Rationale for Split:**
- De-risk: Validate Phase 1 before committing to complex SQL tool
- Quick wins: Get 15% improvement in 4 weeks
- Option to defer: If SQL proves too complex, Phase 1 still delivers value

---

## 📊 EXPECTED IMPACT (Validated Estimates)

| Metric | Baseline | After Phase 1 | After Phase 2 | Total Improvement |
|--------|----------|---------------|---------------|-------------------|
| **Semantic queries** | 87% | 90% (+3%) | 90% | +3% |
| **Document listing** | 0% (impossible) | 100% (+100%) | 100% | +100% |
| **Full-context queries** | 70% | 90% (+29%) | 90% | +29% |
| **Numerical queries** | 60% | 65% (+8%) | 90% (+50%) | +50% |
| **Overall RAG quality** | 87% | 92% (+6%) | 95% (+9%) | +9% |

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

**Tool #3: Get Full Document (NEW - Phase 1)**
```python
async def get_full_document_tool(
    self,
    document_id: str,
    group_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Retrieve full document text (reconstruct from all chunks).
    
    Args:
        document_id: Document identifier (filename or UUID)
        
    Returns:
        {
            "document_id": "FFESSM Niveau 1.pdf",
            "full_text": "...",  # Concatenated chunks
            "metadata": {...},
            "num_chunks": 25
        }
    """
    logger.info(f"📄 Retrieving full document: {document_id}")
    
    # Query Neo4j for all chunks of document
    query = """
    MATCH (e:EpisodeType)
    WHERE e.source_description CONTAINS $document_id
      AND ($group_ids IS NULL OR e.group_id IN $group_ids)
    RETURN e.content AS chunk_text, e.created_at AS created_at
    ORDER BY e.created_at
    """
    
    # Reconstruct full document
    # ...
    
    return {
        "document_id": document_id,
        "full_text": full_text,
        "metadata": metadata,
        "num_chunks": len(chunks)
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

## 📅 PHASE 1 PLAN (4 WEEKS)

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
- Design query to list all documents
- Extract metadata (filename, chunks, upload_date)
- Handle group_ids filter

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

**6.2 Implement Fallback Logic (4 hours)**
- Add `should_fallback()` method
- Add `execute_fallback_tool()` method
- Implement fallback strategies:
  - SEMANTIC → Try COMPREHENSIVE if few results
  - COMPREHENSIVE → Try SEMANTIC if no match
  - NUMERICAL → Try SEMANTIC (Phase 1)

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
- 40 test queries:
  - 15 semantic queries (baseline)
  - 10 document listing queries (new capability)
  - 10 comprehensive queries (should improve)
  - 5 numerical queries (partial, Phase 2 will improve)
- Each with expected tool and expected quality

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

### **DAY 16-17: Staging Deployment** (Monday-Tuesday)

**Goal:** Deploy Phase 1 to staging

**Tasks:**

**16.1 Staging Deployment (4 hours)**
- Rebuild Docker containers
- Deploy to staging
- Verify agent loads
- Test all tools

**16.2 Staging Tests (4 hours)**
- Run 20 test queries
- Verify tool selection
- Check performance
- Monitor errors

**16.3 Load Testing (4 hours)**
- 100 concurrent queries
- Verify agent overhead acceptable
- Check memory usage

**Deliverables:**
- ✅ Staging deployment successful
- ✅ Tests passing

**Time:** 12 hours (2 days × 6 hours)

---

### **DAY 18-19: Production Deployment** (Wednesday-Thursday)

**Goal:** Deploy Phase 1 to production

**Tasks:**

**18.1 Production Deployment (4 hours)**
- Deploy to production
- Verify startup
- Monitor metrics

**18.2 Production Tests (4 hours)**
- 30 real queries
- User acceptance testing
- Collect feedback

**18.3 Documentation Finalization (4 hours)**
- Update `CURRENT-CONTEXT.md`
- Finalize all docs
- Commit to GitHub

**Deliverables:**
- ✅ Production deployment
- ✅ Phase 1 COMPLETE!

**Time:** 12 hours (2 days × 6 hours)

---

### **DAY 20: Phase 2 Planning** (Friday)

**Goal:** Plan Phase 2 (SQL Tool)

**Tasks:**

**20.1 Phase 2 Design (3 hours)**
- Design table extraction pipeline
- Design `document_rows` schema
- Design SQL generation logic

**20.2 Risk Assessment (2 hours)**
- Evaluate Phase 2 complexity
- Decide: Proceed or defer?
- Document decision

**20.3 Celebrate Phase 1! (1 hour)** 🎉
- Retrospective
- Lessons learned
- Team celebration

**Deliverables:**
- ✅ Phase 2 plan (if proceeding)
- ✅ Phase 1 retrospective

**Time:** 6 hours

---

## 📊 PHASE 1 SUCCESS METRICS

### **Baseline (Before Agentic)**
- Semantic query accuracy: 87%
- Document listing: 0% (impossible)
- Comprehensive queries: 70%
- Overall RAG quality: 87%

### **Target (After Phase 1)**
- Semantic query accuracy: **90% (+3%)**
- Document listing: **100% (new capability!)**
- Comprehensive queries: **90% (+29%)**
- Overall RAG quality: **92% (+6%)**

---

## 🔄 PHASE 2 PLAN (2 WEEKS) - DEFER IF NEEDED

### **Week 5: Table Extraction**
- Day 21-22: Docling table extraction
- Day 23-24: `document_rows` schema design
- Day 25: Testing

### **Week 6: SQL Tool**
- Day 26-27: SQL query generation
- Day 28: Integration testing
- Day 29: Deployment
- Day 30: Validation

**Phase 2 Target:**
- Numerical query accuracy: **90% (+50%)**
- Overall RAG quality: **95% (+9%)**

---

## ✅ PHASE 1 ACCEPTANCE CRITERIA

### **Functional**
- [x] 3 tools implemented (rag, list, full_doc)
- [x] Agent classifies queries correctly (>90% accuracy)
- [x] Tool selection works for each query type
- [x] Fallback strategies trigger when needed

### **Quality**
- [x] Document listing works 100%
- [x] Comprehensive queries improve +20-30%
- [x] Semantic queries maintain quality
- [x] A/B test validates improvement

### **Performance**
- [x] Agent overhead <100ms
- [x] No regression in response time
- [x] Memory increase <100MB

---

**Phase 1 Status:** 🟢 READY FOR IMPLEMENTATION  
**Next Action:** Begin after Gap #2 + #3 complete  
**Estimated Start Date:** November 26, 2025 (after 3 weeks)


