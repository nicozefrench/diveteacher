# GAP #4 DEVELOPMENT PLAN: Agentic Chunking

**Priority:** 🔵 P4 - LOW (DEFERRED TO PHASE 2)  
**Date:** November 4, 2025  
**Estimated Duration:** 3 weeks (15 working days)  
**Risk Level:** 🔴 HIGH (could destabilize reliable ARIA chunking)  
**Value:** 🟡 MEDIUM (+5% quality, mainly for tables/lists)  
**Cost:** 💰 FREE (no API costs)

---

## ⚠️ IMPORTANT: DEFER TO PHASE 2

**Recommendation:** **DO NOT IMPLEMENT THIS NOW**

**Rationale:**
1. ✅ **ARIA chunking is working perfectly** (100% success rate)
2. ⚠️ **High risk** of destabilizing reliable system
3. 🟡 **Low ROI** (+5% improvement, not worth risk)
4. ✅ **Gaps #2 + #3 deliver more value** (+16% combined)
5. ✅ **Phase 2 consideration** only after Gaps #1-3 are stable

**Decision Point:**
- **If Gaps #1-3 achieve >92% quality:** Consider implementing Gap #4
- **If Gaps #1-3 achieve <92% quality:** Skip Gap #4, focus on optimizing #1-3

---

## 📋 EXECUTIVE SUMMARY (For Future Reference)

**Objective:** Replace fixed-size ARIA chunking with content-aware agentic chunking

**Approach:** Analyze document structure, create semantically meaningful sections, adapt chunk size to content type

**Why P4 (Lowest Priority):**
- ✅ ARIA chunking already works well (3000 tokens/chunk, 200 overlap)
- ⚠️ High complexity (content-aware logic, ML-based?)
- ⚠️ Uncertain ROI (may not improve much over ARIA)
- 🔴 Risk: Could destabilize current reliable system

**Current State (ARIA Chunking):**
- RecursiveCharacterTextSplitter (LangChain)
- Fixed chunk_size=3000 tokens
- Fixed overlap=200 tokens
- Splits on semantic boundaries ("\n\n", "\n", ". ", " ", "")
- **BUT:** No content-aware adaptation
- **Problem:** Tables may be split mid-table, lists mid-list

**Target State (Agentic Chunking):**
- Analyze document structure (tables, lists, code blocks, paragraphs)
- Create semantically meaningful sections
- Preserve context boundaries (don't split tables, lists, code)
- Adapt chunk size to content type (larger for tables, smaller for bullet points)
- Expected: +10% for table queries, +10% for list queries, +5% overall

---

## 🎯 WHAT IS AGENTIC CHUNKING?

### **Concept (from Cole Medin's Guide)**

Instead of fixed-size chunks:
1. Analyze document structure
2. Identify content types (table, list, paragraph, code, heading)
3. Create chunks that preserve semantic boundaries
4. Adapt chunk size to content

### **Example**

**Current (ARIA Fixed-Size):**
```
Chunk 1 (3000 tokens):
"Safety procedures include:
1. Check equipment
2. Plan dive
3. Review signals
4. Confirm buddy

Table: Dive Limits
| Depth | Time | Stop |
|-------|------|------|
| 12m   | 20min| 0min |
| 15m   | 40min| 3min |"  <-- TABLE CUT OFF!

Chunk 2 (3000 tokens):
"| 18m   | 60min| 10min|
| 21m   | 50min| 15min|

After the dive..."
```

**Problems:**
- Table split across chunks (loses context)
- Query "What are the dive limits for 18m?" may miss Chunk 1 (has table header)
- Retrieval quality degraded for table queries

**Agentic Chunking (Goal):**
```
Chunk 1 (2500 tokens):
"Safety procedures include:
1. Check equipment
2. Plan dive
3. Review signals
4. Confirm buddy"

Chunk 2 (500 tokens - ADAPTIVE!):
"Table: Dive Limits
| Depth | Time | Stop |
|-------|------|------|
| 12m   | 20min| 0min |
| 15m   | 40min| 3min |
| 18m   | 60min| 10min|
| 21m   | 50min| 15min|"  <-- FULL TABLE IN ONE CHUNK!

Chunk 3 (3000 tokens):
"After the dive, perform safety checks..."
```

**Benefits:**
- Table intact (better retrieval)
- Query "What are the dive limits for 18m?" retrieves Chunk 2 (complete table)
- +10-15% improvement for table queries

---

## 🔧 IMPLEMENTATION APPROACHES

### **Approach A: Rule-Based (Simpler)**

**Pros:**
- Predictable behavior
- Easy to debug
- Fast (no ML inference)

**Cons:**
- Requires many rules
- May miss edge cases

**Implementation:**
```python
# backend/app/services/agentic_chunker.py

class AgenticChunker:
    """
    Content-aware chunker that preserves semantic boundaries.
    """
    
    def chunk_document(self, docling_doc: DoclingDocument) -> List[Chunk]:
        """
        Chunk document using content-aware strategy.
        
        Process:
        1. Extract document structure from Docling
        2. Identify content types (table, list, paragraph)
        3. Create chunks that preserve boundaries
        4. Adapt chunk size to content type
        """
        # Extract structure
        tables = docling_doc.tables  # Docling provides table boundaries!
        lists = self._extract_lists(docling_doc.export_to_markdown())
        paragraphs = self._extract_paragraphs(docling_doc.export_to_markdown())
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for element in self._traverse_document(docling_doc):
            if element.type == "table":
                # Keep entire table in one chunk
                if current_tokens + element.tokens > self.max_chunk_size:
                    # Save current chunk, start new chunk with table
                    chunks.append(self._create_chunk(current_chunk))
                    current_chunk = element.text
                    current_tokens = element.tokens
                else:
                    current_chunk += element.text
                    current_tokens += element.tokens
            
            elif element.type == "list":
                # Keep entire list in one chunk
                # (similar logic to table)
                pass
            
            elif element.type == "paragraph":
                # Standard ARIA chunking
                # Split if exceeds max_chunk_size
                pass
        
        return chunks
```

**Rules:**
1. **Tables:** Keep entire table in one chunk (don't split)
2. **Lists:** Keep entire list together (don't split mid-list)
3. **Code blocks:** Keep entire block together
4. **Paragraphs:** Use ARIA pattern (split at sentence boundaries)
5. **Headings:** Start new chunk on H1/H2 headers

### **Approach B: ML-Based (Advanced)**

**Pros:**
- Learns optimal boundaries from data
- Adapts to new content types
- Better semantic coherence

**Cons:**
- Requires training data
- Slower (ML inference)
- Less predictable

**Implementation:**
- Train ML model to predict "should chunk here?" (binary classification)
- Features: context window, content type, embedding similarity, token count
- Use pre-trained model (e.g., SentenceTransformers for embedding similarity)

**Status:** Too complex for Phase 1, consider for Phase 3

---

## 📅 DETAILED PLAN (IF IMPLEMENTED)

### **PHASE 1: DESIGN & PROOF-OF-CONCEPT (Week 1)**

**Day 1-2: Design**
- Analyze Docling's table detection API
- Design boundary detection logic
- Choose Approach A (rule-based) vs B (ML-based)

**Day 3-4: POC Implementation**
- Implement prototype agentic chunker
- Test on 5 documents (with tables, lists)
- Compare to ARIA baseline

**Day 5: Validation**
- If POC shows +10% improvement → Continue to Phase 2
- If POC shows <5% improvement → ABORT, keep ARIA

---

### **PHASE 2: FULL IMPLEMENTATION (Week 2)**

**Day 6-8: Implement Agentic Chunker**
- Create `backend/app/services/agentic_chunker.py`
- Implement table boundary detection
- Implement list boundary detection
- Implement adaptive chunk sizing

**Day 9-10: Integration & Testing**
- Integrate with document processing pipeline
- A/B test: ARIA vs Agentic
- Measure improvement

---

### **PHASE 3: DEPLOYMENT (Week 3)**

**Day 11-13: Staging & Production**
- Deploy to staging
- Validate quality improvement
- Deploy to production if validated

**Day 14-15: Monitoring & Rollback Plan**
- Monitor chunk quality
- Prepare rollback to ARIA if issues
- Document results

---

## 🔒 RISK MITIGATION

### **Risk #1: Destabilizes ARIA (Critical)**
- **Probability:** HIGH
- **Impact:** CRITICAL (breaks ingestion)
- **Mitigation:**
  - Keep ARIA as fallback
  - Implement feature flag: `USE_AGENTIC_CHUNKING=False` (default)
  - A/B test extensively before production

### **Risk #2: No Quality Improvement**
- **Probability:** MEDIUM
- **Impact:** HIGH (wasted effort)
- **Mitigation:**
  - POC validation before full implementation
  - Abort if POC shows <5% improvement

### **Risk #3: Performance Degradation**
- **Probability:** MEDIUM
- **Impact:** MEDIUM (slower ingestion)
- **Mitigation:**
  - Profile chunking performance
  - Optimize boundary detection
  - Accept 20% overhead if quality improves significantly

---

## ✅ ACCEPTANCE CRITERIA (IF IMPLEMENTED)

### **Functional**
- [x] Tables are NOT split mid-table
- [x] Lists are kept intact
- [x] Chunk size adapts to content type
- [x] Fallback to ARIA works

### **Quality**
- [x] Table query accuracy: +10%
- [x] List query accuracy: +10%
- [x] Overall quality: +5%
- [x] A/B test validates improvement

### **Performance**
- [x] Chunking overhead <20%
- [x] Ingestion time acceptable

---

## 🎯 DECISION CRITERIA

**Proceed with Gap #4 IF:**
1. ✅ Gaps #1-3 are complete and stable
2. ✅ Overall RAG quality >92%
3. ✅ POC shows +10% improvement on table/list queries
4. ✅ ARIA remains as fallback

**Skip Gap #4 IF:**
1. ❌ Gaps #1-3 not complete
2. ❌ Overall RAG quality <92%
3. ❌ POC shows <5% improvement
4. ❌ High risk to stable system

---

## 📊 ALTERNATIVE: HYBRID APPROACH

**Instead of replacing ARIA, augment it:**

1. **Keep ARIA for most content** (paragraphs, standard text)
2. **Use special handling for tables/lists:**
   - Detect table boundaries (Docling provides this!)
   - If table + surrounding text > max_chunk_size:
     - Create dedicated chunk for table only
   - Else: Include table in regular ARIA chunk

**Benefits:**
- Lower risk (keep ARIA baseline)
- Targeted improvement (only tables/lists)
- Easier to implement

**Code:**
```python
def hybrid_chunk(docling_doc: DoclingDocument) -> List[Chunk]:
    """
    Hybrid: ARIA for text, special handling for tables.
    """
    chunks = []
    
    # Extract tables from Docling
    tables = docling_doc.tables
    
    # Split text using ARIA
    aria_chunks = aria_chunker.chunk(docling_doc.export_to_markdown())
    
    # Post-process: Extract tables to dedicated chunks
    for chunk in aria_chunks:
        if contains_table(chunk):
            # Split: table → dedicated chunk, text → ARIA chunk
            table_chunk, text_chunks = split_table(chunk)
            chunks.append(table_chunk)
            chunks.extend(text_chunks)
        else:
            chunks.append(chunk)
    
    return chunks
```

**Recommendation:** **Try hybrid approach first** (lower risk)

---

## 📝 FINAL RECOMMENDATION

**Status:** 🔵 **DEFERRED TO PHASE 2**

**Priority Order:**
1. 🔴 **P1:** Gap #2 (Reranking) - 1 week - IMPLEMENT NOW
2. 🟠 **P2:** Gap #3 (Contextual) - 2 weeks - IMPLEMENT AFTER P1
3. 🟡 **P3:** Gap #1 (Agentic Tools Phase 1) - 4 weeks - IMPLEMENT AFTER P2
4. 🟢 **P3.5:** Gap #1 (Agentic Tools Phase 2 - SQL) - 2 weeks - EVALUATE AFTER P3
5. 🔵 **P4:** Gap #4 (Agentic Chunking) - 3 weeks - **DEFER, EVALUATE LATER**

**When to Reconsider Gap #4:**
- After completing Gaps #1-3 (6+ weeks from now)
- If overall quality >92% and looking for incremental improvements
- If table/list queries are specifically problematic

**Alternative Focus:**
- Instead of Gap #4, consider:
  - Query optimization (caching, indexing)
  - R1 Distill RAG (reasoning model)
  - Audio transcription (multi-modal)
  - Web crawling (expand knowledge base)

---

**Plan Status:** 🔵 INFORMATIONAL ONLY (DO NOT IMPLEMENT NOW)  
**Revisit Date:** After Gap #1-3 complete (~12 weeks from now)  
**Next Action:** Focus on Gap #2 (Reranking) instead


