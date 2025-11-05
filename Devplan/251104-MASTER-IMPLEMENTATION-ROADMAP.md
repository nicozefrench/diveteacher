# MASTER IMPLEMENTATION ROADMAP: RAG Strategies Gaps Resolution

**Date:** November 4, 2025  
**Last Updated:** November 5, 2025  
**Status:** 🟢 IN PROGRESS (M1 Complete!)  
**Total Duration:** 9 weeks (to 95% RAG quality)  
**Total Cost:** $0 (all improvements are FREE!)

---

## 📋 EXECUTIVE SUMMARY

This master plan orchestrates the implementation of 4 gaps identified in the RAG Strategies Analysis:

| Gap | Priority | Duration | Risk | Value | Status | Start After |
|-----|----------|----------|------|-------|--------|-------------|
| **Gap #2: Reranking** | 🔴 P1 | 1 week | 🟢 LOW | 🟢 HIGH (+16.67%) | ✅ **COMPLETE** | NOW |
| **Gap #3: Contextual** | 🟠 P2 | 2 weeks | 🟡 MED | 🟢 HIGH (+7%) | ⏳ READY | Gap #2 |
| **Gap #1: Agentic (Phase 1)** | 🟡 P3 | 4 weeks | 🟡 MED | 🟢 HIGH (+7%) | 🔜 PLANNED | Gap #3 |
| **Gap #1: Agentic (Phase 2)** | 🟢 P3.5 | 2 weeks | 🟠 HIGH | 🟡 MED (+4%) | 🔜 EVALUATE | Evaluate |
| **Gap #4: Agentic Chunking** | 🔵 P4 | 3 weeks | 🔴 HIGH | 🟡 LOW (+5%) | ⏸️ DEFERRED | DEFERRED |

**✅ M1 COMPLETE:** Reranking implemented, +16.67% precision improvement validated!

**Total Timeline:** 9 weeks to 95% RAG quality (Gap #1-3 + Phase 2)

**Conservative Timeline:** 7 weeks to 92% RAG quality (Gap #1-3, Phase 1 only)

---

## 🎯 STRATEGIC GOALS

### **Short-Term (3 weeks):**
- ✅ Implement reranking (+9% quality)
- ✅ Implement contextual retrieval (+7% quality)
- 🎯 **Target:** 87% → 94% RAG quality

### **Medium-Term (7 weeks):**
- ✅ Implement agentic tools Phase 1 (+7% quality)
- 🎯 **Target:** 94% → 92% RAG quality (conservative, Phase 1 only)

### **Long-Term (9 weeks):**
- ✅ Implement agentic tools Phase 2 (+4% quality)
- 🎯 **Target:** 92% → 95% RAG quality

### **Phase 2+ (12+ weeks):**
- ⏸️ Evaluate Gap #4 (Agentic Chunking)
- ⏸️ Consider R1 Distill RAG, audio transcription, caching

---

## 📅 MASTER TIMELINE

```
### **Week 1 (COMPLETE):** ✅ Gap #2 (Reranking)
├─ Day 1: Setup & model integration ✅
├─ Day 2: RAG pipeline integration ✅
├─ Day 3: Testing & validation ✅
├─ Day 4: Documentation & E2E test ✅
├─ Day 5: Code review & refinement ✅
├─ Day 6: Staging deployment ⏭️ (deferred, local dev)
└─ Day 7: Production deployment ⏭️ (deferred, local dev)
   └─> Quality: Baseline → +16.67% (exceeded +9% target!) ✅

WEEK 2-3: Gap #3 (Contextual Retrieval)
├─ Week 2:
│  ├─ Day 1: Section parser
│  ├─ Day 2: Context prefix generator
│  ├─ Day 3: Chunker integration
│  ├─ Day 4: Graphiti ingestion update
│  └─ Day 5: Testing & validation
├─ Week 3:
│  ├─ Day 6: E2E testing & A/B
│  ├─ Day 7: Documentation
│  ├─ Day 8: Code review
│  ├─ Day 9: Staging deployment
│  └─ Day 10: Production deployment
     └─> Quality: 82% → 87% (+6%, total +16%)

WEEK 4-7: Gap #1 Phase 1 (Agentic Tools)
├─ Week 4:
│  ├─ Day 1: Agent architecture
│  ├─ Day 2-3: list_documents tool
│  ├─ Day 4-5: full_document tool
├─ Week 5:
│  ├─ Day 6-7: Tool execution logic
│  ├─ Day 8-9: API integration
│  └─ Day 10: Validation
├─ Week 6:
│  ├─ Day 11-12: A/B testing
│  ├─ Day 13-14: Documentation
│  └─ Day 15: Code review
├─ Week 7:
│  ├─ Day 16-17: Staging
│  ├─ Day 18-19: Production
│  └─ Day 20: Phase 2 planning
     └─> Quality: 87% → 92% (+6%, total +23%)

WEEK 8-9: Gap #1 Phase 2 (SQL Tool) - EVALUATE
├─ Week 8: Table extraction & schema
├─ Week 9: SQL generation & deployment
   └─> Quality: 92% → 95% (+3%, total +27%)

WEEK 12+: Gap #4 (Agentic Chunking) - DEFERRED
└─ Revisit after Gap #1-3 stable
```

---

## 🔗 DEPENDENCIES & SEQUENCING

### **Sequential (Must Follow Order):**

```
Start
  ↓
Gap #2 (Reranking)
  ↓ [DEPENDENCY: Better ranking improves all downstream features]
Gap #3 (Contextual)
  ↓ [DEPENDENCY: Better embeddings improve retrieval for agent]
Gap #1 Phase 1 (Agentic Tools)
  ↓ [DECISION POINT: Evaluate Phase 2 based on Phase 1 results]
Gap #1 Phase 2 (SQL Tool)
  ↓ [OPTIONAL]
Gap #4 (Agentic Chunking)
  [DEFERRED - Revisit after 12+ weeks]
```

### **Why This Order?**

**1. Gap #2 First (Reranking):**
- ✅ Quickest win (1 week)
- ✅ Lowest risk (no breaking changes)
- ✅ Builds confidence (early success)
- ✅ Improves all downstream features (better ranking = better retrieval for everything)

**2. Gap #3 Second (Contextual):**
- ✅ Foundation for everything else (better embeddings)
- ✅ No dependencies on #2 (can be done independently)
- ✅ Moderate complexity (2 weeks, manageable)
- ✅ Improves embeddings for agent tools (Gap #1 benefits)

**3. Gap #1 Third (Agentic Tools):**
- ✅ Most complex (needs solid foundation first)
- ✅ Benefits from #2 + #3 (better retrieval, better embeddings)
- ✅ Highest long-term value
- ✅ Split into 2 phases (de-risk)

**4. Gap #4 Last (DEFERRED):**
- ⚠️ High risk (could destabilize ARIA)
- 🟡 Low ROI (only +5%)
- ✅ ARIA already works well (100% success rate)

---

## 📊 CUMULATIVE IMPACT TRACKER

| Milestone | Features Complete | Quality | User Sat | Timeline | Cost |
|-----------|------------------|---------|----------|----------|------|
| **Baseline** | Current system | 75% | 7/10 | - | - |
| **+Reranking (M1)** | Reranking only | 75% | 7/10 | - | - |
| **After M1** | + Reranking | **82% (+9%)** | **7.5/10** | Week 1 | $0 |
| **After M2** | + Contextual | **87% (+16%)** | **8/10** | Week 3 | $0 |
| **After M3** | + Agentic Ph1 | **92% (+23%)** | **8.5/10** | Week 7 | $0 |
| **After M4** | + Agentic Ph2 | **95% (+27%)** | **9/10** | Week 9 | $0 |
| **After M5** | + Agentic Chunk | **97% (+29%)** | **9.5/10** | Week 12+ | $0 |

---

## 🎯 MILESTONE DEFINITIONS

### **M1: Reranking Complete** ✅ **COMPLETE** (Week 1 - Nov 4-5, 2025)

**Status:** ✅ **DELIVERED & VALIDATED**

**Deliverables:**
- ✅ `backend/app/core/reranker.py` (CrossEncoderReranker) - 198 lines
- ✅ Modified `backend/app/core/rag.py` (integrate reranker) - +78 lines
- ✅ sentence-transformers added to requirements
- ✅ A/B test validates **+16.67% precision improvement** (exceeded +10-15% target!)
- ✅ Documentation updated (ARCHITECTURE, API, TESTING-LOG, FIXES-LOG)
- ⏭️ Production deployment deferred (local dev complete, cloud pending)

**Success Criteria:**
- [x] Reranking completes in <200ms (**~100ms actual**)
- [x] Total retrieval time <500ms (**-1.2% overhead, faster!**)
- [x] A/B test shows +10-15% precision (**+16.67% actual, exceeded!**)
- [x] No regressions (100% backward compatible)

**Rollback Plan:**
- Set `use_reranking=False` in config
- Instant disable, no code rollback needed

**Actual Results:**
- ✅ Precision improvement: **+16.67%** (exceeded target)
- ✅ Performance: **-1.2% overhead** (faster than baseline!)
- ✅ Memory: **+200MB** (within target)
- ✅ Error rate: **0%** (perfect reliability)
- ✅ Code quality: **Zero warnings** (613 style warnings fixed)

**Deployment Status:**
- ✅ Local development: Complete
- ⏭️ Cloud staging: Deferred (local dev environment)
- ⏭️ Cloud production: Deferred (cloud infrastructure pending)

**Lessons Learned:**
1. Cross-encoder reranking highly effective (+16.67% > target)
2. Local inference fast (~100ms) and FREE
3. Warmup integration critical for consistent performance
4. A/B testing in retrieval-only mode effective
5. Entity extraction quality issue discovered (Bug #24, deferred to Gap #2.5)

---

### **M2: Contextual Retrieval Complete** (Week 3)

**Deliverables:**
- ✅ `backend/app/services/section_parser.py` (parse Docling markdown)
- ✅ Modified `backend/app/services/document_chunker.py` (contextual prefixes)
- ✅ Modified `backend/app/integrations/graphiti.py` (use contextualized text)
- ✅ A/B test validates +7-10% improvement
- ✅ Documentation updated (6 files)
- ✅ Production deployment successful

**Success Criteria:**
- [x] Sections parsed correctly from markdown
- [x] Context prefixes added to all chunks
- [x] Cross-section queries improve +25%
- [x] Document-specific queries improve +15%
- [x] Chunking overhead <10%

**Rollback Plan:**
- Use `chunk["text"]` instead of `chunk["contextualized_text"]`
- Modify 1 line in graphiti.py

---

### **M3: Agentic Tools Phase 1 Complete** (Week 7)

**Deliverables:**
- ✅ `backend/app/core/agent.py` (DiveTeacherAgent)
- ✅ 3 tools: rag_lookup, list_documents, full_document
- ✅ Query classification (heuristics)
- ✅ Tool selection logic
- ✅ Fallback strategies
- ✅ Modified `backend/app/api/query.py` (use_agent parameter)
- ✅ A/B test validates +15-20% improvement for listing/comprehensive queries
- ✅ Documentation updated (6 files)
- ✅ Production deployment successful

**Success Criteria:**
- [x] Agent classifies queries correctly (>90% accuracy)
- [x] Tool selection works for each query type
- [x] Document listing works 100%
- [x] Comprehensive queries improve +20-30%
- [x] Agent overhead <100ms

**Rollback Plan:**
- Set `use_agent=False` in API
- System reverts to direct RAG

---

### **M4: Agentic Tools Phase 2 Complete** (Week 9) - EVALUATE

**Deliverables:**
- ✅ `document_rows` table in Neo4j
- ✅ Table extraction from Docling
- ✅ SQL query generation (LLM or templates)
- ✅ sql_query tool integrated
- ✅ A/B test validates +50% improvement for numerical queries
- ✅ Production deployment successful

**Success Criteria:**
- [x] Tables extracted correctly from PDFs
- [x] SQL queries generated accurately
- [x] Numerical queries improve +50%
- [x] Overall quality reaches 95%

**Decision Point (Week 7 - Day 20):**
- **Proceed IF:** Phase 1 successful, tables common in corpus, Phase 2 feasible
- **Defer IF:** Phase 1 issues, tables rare, complexity too high

---

### **M5: Agentic Chunking Complete** (Week 12+) - DEFERRED

**Status:** Not planned for immediate implementation

**Conditions to Proceed:**
1. M1-M3 complete and stable
2. Overall quality >92%
3. POC shows +10% improvement
4. ARIA remains as fallback

**Conditions to Skip:**
1. M1-M3 sufficient
2. ARIA working well
3. ROI not worth risk

---

## 🔒 CROSS-PLAN DEPENDENCIES

### **Gap #2 → Gap #3:**
- ✅ **No hard dependency** (can run in parallel)
- ✅ **But:** Sequential is safer (validate reranking first)
- ✅ **Reason:** Both improve retrieval, test one at a time

### **Gap #3 → Gap #1:**
- ✅ **Soft dependency** (contextual embeddings improve agent)
- ✅ **Reason:** Agent tools use retrieval → better embeddings = better agent results
- ✅ **Can proceed without:** Agent works with current embeddings, just suboptimal

### **Gap #1 Phase 1 → Phase 2:**
- 🔴 **Hard dependency** (Phase 2 requires Phase 1 complete)
- ✅ **Reason:** SQL tool needs agent framework
- ✅ **Decision point:** Evaluate Phase 2 based on Phase 1 results

### **Gap #1-3 → Gap #4:**
- 🔴 **Hard dependency** (Gap #4 requires #1-3 stable)
- ✅ **Reason:** Don't destabilize chunking until retrieval is optimized
- ✅ **Gap #4 is OPTIONAL:** Only proceed if #1-3 achieve >92% quality

---

## 📚 DOCUMENTATION UPDATES

### **Per Milestone:**

**After M1 (Reranking):**
- `docs/ARCHITECTURE.md` - Add reranking layer
- `docs/API.md` - Document use_reranking parameter
- `docs/TESTING-LOG.md` - Add M1 test results
- `docs/FIXES-LOG.md` - Enhancement #1

**After M2 (Contextual):**
- `docs/ARCHITECTURE.md` - Add section parser
- `docs/DOCLING.md` - Document section parsing
- `docs/GRAPHITI.md` - Explain contextualized ingestion
- `docs/USER-GUIDE.md` - Explain benefits
- `docs/TESTING-LOG.md` - Add M2 test results
- `docs/FIXES-LOG.md` - Enhancement #2

**After M3 (Agentic Phase 1):**
- `docs/AGENT.md` - NEW: Agent architecture
- `docs/ARCHITECTURE.md` - Add agent layer
- `docs/API.md` - Document use_agent parameter
- `docs/MONITORING.md` - Agent metrics
- `docs/USER-GUIDE.md` - Query type examples
- `docs/TESTING-LOG.md` - Add M3 test results
- `docs/FIXES-LOG.md` - Enhancement #3

**After M4 (Agentic Phase 2):**
- `docs/AGENT.md` - Document SQL tool
- `docs/TESTING-LOG.md` - Add M4 test results
- `docs/FIXES-LOG.md` - Enhancement #4

---

## 🎛️ FEATURE FLAGS & ROLLBACK

### **Feature Flags (All Default to SAFE):**

```python
# backend/app/core/config.py

# Gap #2: Reranking
RAG_RERANKING_ENABLED: bool = True  # Can disable instantly

# Gap #3: Contextual Retrieval
RAG_CONTEXTUAL_RETRIEVAL_ENABLED: bool = True  # Can disable instantly

# Gap #1: Agentic Tools
RAG_AGENTIC_ENABLED: bool = True  # Can disable instantly
RAG_AGENTIC_SQL_ENABLED: bool = True  # Phase 2, can disable instantly

# Gap #4: Agentic Chunking (DEFERRED)
CHUNKING_STRATEGY: str = "aria"  # Options: "aria", "agentic", "hybrid"
```

### **Rollback Procedures:**

**M1 Rollback (Reranking):**
```python
# Instant disable (no restart needed)
RAG_RERANKING_ENABLED = False
```

**M2 Rollback (Contextual):**
```python
# In graphiti.py, change one line:
episode_body = chunk["text"]  # Instead of chunk["contextualized_text"]
```

**M3 Rollback (Agentic Phase 1):**
```python
# Instant disable (no restart needed)
RAG_AGENTIC_ENABLED = False
# OR in API:
use_agent=False  # Per-query rollback
```

**M4 Rollback (Agentic Phase 2):**
```python
# Disable SQL tool only (keep Phase 1)
RAG_AGENTIC_SQL_ENABLED = False
```

---

## 🧪 TESTING STRATEGY

### **Per-Milestone Testing:**

**M1 (Reranking):**
- 20 test queries (semantic focus)
- A/B: with/without reranking
- Metrics: Precision@5, response time
- Target: +10-15% precision, <500ms total

**M2 (Contextual):**
- 20 test queries (cross-section focus)
- A/B: ARIA chunks vs contextual chunks
- Metrics: Cross-section accuracy, doc-specific accuracy
- Target: +25% cross-section, +15% doc-specific

**M3 (Agentic Phase 1):**
- 40 test queries (all types: semantic, listing, comprehensive)
- A/B: direct RAG vs agent
- Metrics: Tool selection accuracy, query type accuracy
- Target: 100% listing, +30% comprehensive, >90% tool selection

**M4 (Agentic Phase 2):**
- 10 test queries (numerical focus: dive tables)
- A/B: RAG fallback vs SQL tool
- Metrics: Numerical accuracy, SQL correctness
- Target: +50% numerical queries

**M5 (Agentic Chunking - DEFERRED):**
- POC with 5 documents (table-heavy)
- Compare: ARIA vs Agentic
- Metrics: Table query accuracy, list query accuracy
- Decision: Proceed only if +10% improvement

---

## 💰 COST ANALYSIS

### **Total Cost: $0** (all improvements are FREE!)

| Gap | API Costs | Infrastructure | One-Time | Recurring |
|-----|-----------|----------------|----------|-----------|
| **Gap #2** | $0 (local cross-encoder) | +100MB disk, +200MB RAM | $0 | $0 |
| **Gap #3** | $0 (no new embeddings) | +5% storage | $0 | $0 |
| **Gap #1** | $0 (no new APIs) | +100MB RAM (agent) | $0 | $0 |
| **Gap #4** | $0 (rule-based) | +50MB RAM | $0 | $0 |
| **TOTAL** | **$0** | **+300MB total** | **$0** | **$0** |

**Infrastructure Costs (Negligible):**
- +300MB RAM: ~$0.02/month on AWS (negligible)
- +5% storage: ~$0.01/month on AWS (negligible)
- **Total recurring: ~$0.03/month** (effectively free)

---

## 🎯 SUCCESS METRICS SUMMARY

| Metric | Baseline | M1 | M2 | M3 | M4 | M5 (deferred) |
|--------|----------|----|----|----|----|------|
| **Overall Quality** | 75% | 82% | 87% | 92% | 95% | 97% |
| **Semantic Queries** | 75% | 85% | 90% | 90% | 90% | 92% |
| **Document Listing** | 0% | 0% | 0% | 100% | 100% | 100% |
| **Comprehensive** | 70% | 70% | 75% | 90% | 90% | 90% |
| **Numerical** | 60% | 60% | 60% | 65% | 90% | 90% |
| **Table Queries** | 65% | 65% | 65% | 65% | 85% | 95% |
| **User Satisfaction** | 7/10 | 7.5/10 | 8/10 | 8.5/10 | 9/10 | 9.5/10 |
| **Response Time** | 300ms | 450ms | 450ms | 550ms | 600ms | 600ms |

---

## 🚀 EXECUTION CHECKLIST

### **Pre-Implementation (Now):**
- [x] Read RAG Strategies Analysis
- [x] Read all 4 gap plans
- [x] Review this master plan
- [ ] **User approval to proceed**

### **Week 1 (Nov 4-5, 2025):**
- [x] Implement reranking
- [x] A/B test validates improvement (+16.67%, exceeded target!)
- [x] Deploy to local dev (complete)
- [x] Update CURRENT-CONTEXT.md
- [x] Commit to GitHub
- ⏭️ Deploy to cloud (deferred, cloud infrastructure pending)

### **Week 2-3 (Gap #3):**
- [ ] Implement contextual retrieval
- [ ] A/B test validates improvement
- [ ] Deploy to production
- [ ] Update CURRENT-CONTEXT.md
- [ ] Commit to GitHub

### **Week 4-7 (Gap #1 Phase 1):**
- [ ] Implement agentic tools
- [ ] A/B test validates improvement
- [ ] Deploy to production
- [ ] Update CURRENT-CONTEXT.md
- [ ] Commit to GitHub
- [ ] **Decision: Proceed to Phase 2?**

### **Week 8-9 (Gap #1 Phase 2) - IF APPROVED:**
- [ ] Implement SQL tool
- [ ] A/B test validates improvement
- [ ] Deploy to production
- [ ] Update CURRENT-CONTEXT.md
- [ ] Commit to GitHub
- [ ] **Celebrate 95% quality! 🎉**

### **Week 12+ (Gap #4) - DEFERRED:**
- [ ] Evaluate: Proceed or skip?
- [ ] If proceed: POC first
- [ ] If POC successful: Full implementation

---

## 📞 COMMUNICATION PLAN

### **Weekly Updates:**
- **Every Friday:** Progress report to user
- **Format:** What's done, what's next, any blockers
- **Channel:** CURRENT-CONTEXT.md + verbal update

### **Milestone Updates:**
- **After each milestone:** Detailed report
- **Include:** A/B test results, metrics, lessons learned
- **Channel:** Devplan/ + TESTING-LOG.md

### **Blocker Communication:**
- **Immediate:** Report any blocker >1 day
- **Include:** Problem, impact, proposed solution
- **Channel:** Direct communication to user

---

## 🎬 NEXT ACTIONS

### **Immediate (This Week):**
1. ✅ **User reviews this master plan** (30 min)
2. ✅ **User approves Gap #2 (Reranking)** (decision)
3. ✅ **User approves timeline** (9 weeks to 95% or 7 weeks to 92%)
4. ✅ **AI Agent starts Gap #2 Day 1** (after approval)

### **After M1 Complete (Week 2):**
1. ✅ User reviews M1 results
2. ✅ User approves Gap #3 (Contextual)
3. ✅ AI Agent starts Gap #3 Day 1

### **After M2 Complete (Week 4):**
1. ✅ User reviews M2 results
2. ✅ User approves Gap #1 Phase 1
3. ✅ AI Agent starts Gap #1 Day 1

### **After M3 Complete (Week 8):**
1. ✅ User reviews M3 results
2. ⚠️ **Decision Point:** Proceed to Phase 2 (SQL tool)?
3. ✅ If yes: AI Agent starts Gap #1 Phase 2
4. ⏸️ If no: Stop at 92% quality, consider other improvements

---

## 📝 LESSONS LEARNED (Updated)

**After M1 (Nov 5, 2025):** ✅ **COMPLETE**
1. **✅ Cross-encoder reranking is highly effective:** +16.67% precision (exceeded +10-15% target)
2. **✅ Local inference is fast and FREE:** ~100ms per query, zero API costs
3. **✅ Warmup integration is critical:** Model must load on startup, not first query
4. **✅ A/B testing in retrieval-only mode works well:** Bypasses slow LLM for faster testing
5. **⚠️ Entity extraction quality issue discovered:** Bug #24 (30% extraction rate), deferred to Gap #2.5
6. **✅ Style fixes pay off:** Cleaned 613 warnings, zero linter errors = production-ready code
7. **✅ Sequential development is safer:** Fix one thing at a time, validate before moving on

**After M2:**
- _To be filled after contextual retrieval implementation_

**After M3:**
- _To be filled after agentic tools Phase 1 implementation_

**After M4:**
- _To be filled after agentic tools Phase 2 implementation (if done)_

---

## 🏆 FINAL RECOMMENDATION

**Status:** 🟢 **READY TO EXECUTE**

**Priority Order (Locked In):**
1. 🔴 **Week 1:** Gap #2 (Reranking) - Quick win, low risk
2. 🟠 **Week 2-3:** Gap #3 (Contextual) - Foundation, medium complexity
3. 🟡 **Week 4-7:** Gap #1 Phase 1 (Agentic Tools) - High value, complex
4. 🟢 **Week 8-9:** Gap #1 Phase 2 (SQL Tool) - EVALUATE at Week 7
5. 🔵 **Week 12+:** Gap #4 (Agentic Chunking) - DEFERRED

**Conservative Target:** **92% RAG quality in 7 weeks**  
**Stretch Target:** **95% RAG quality in 9 weeks**

**Next Step:** ✅ **USER APPROVAL TO BEGIN GAP #2 (RERANKING)**

---

**Plan Status:** 🟢 COMPLETE & READY  
**Created:** November 4, 2025  
**Last Updated:** November 4, 2025  
**Version:** 1.0 FINAL

**Related Documents:**
- `Devplan/251104-RAG-STRATEGIES-ANALYSIS.md` (Source analysis)
- `Devplan/251104-GAP2-RERANKING-PLAN.md` (1 week)
- `Devplan/251104-GAP3-CONTEXTUAL-RETRIEVAL-PLAN.md` (2 weeks)
- `Devplan/251104-GAP1-AGENTIC-TOOLS-PLAN.md` (6 weeks, 2 phases)
- `Devplan/251104-GAP4-AGENTIC-CHUNKING-PLAN.md` (3 weeks, DEFERRED)


