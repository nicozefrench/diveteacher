# 🎨 UI Progress Feedback & Multi-Document Support - Implementation Plan

> **Created:** October 29, 2025, 19:30 CET  
> **Status:** 🔴 CRITICAL - Blocks Production Deployment  
> **Priority:** P0 - Must Fix Before Large Document Testing  
> **Estimated Duration:** 6-8 hours  
> **Related:** Test Run #9, Bug #9, Bug #10

---

## 📋 Executive Summary

**Problem:**
The current UI provides **ZERO feedback** during the ingestion phase (4+ minutes frozen at 75%), making it **catastrophic** for large documents (15-30 min frozen UI). Additionally, the UI is designed for single document upload and cannot scale to multiple concurrent uploads.

**Impact:**
- 🔴 **CRITICAL:** Users will think the system crashed during long uploads
- 🔴 **CATASTROPHIC:** 50MB documents = 15-30 min frozen UI
- 🔴 **UNACCEPTABLE:** No visibility into chunk processing progress
- 🟡 **HIGH:** Entity/Relation counts not displayed
- 🟡 **MEDIUM:** UI not ready for multi-document uploads

**Solution:**
Implement real-time progress feedback with granular chunk-level updates, display entity/relation counts, and redesign the document list UI to support multiple concurrent uploads with collapsible monitoring panels.

**Expected Outcome:**
- ✅ Real-time progress updates every 5-10 seconds
- ✅ Granular feedback: "Ingesting chunks (15/30 - 50%)"
- ✅ Entity/Relation counts displayed correctly
- ✅ Compact, professional multi-document list
- ✅ Collapsible monitoring panels per document
- ✅ Users have confidence the system is working

---

## 🎯 Objectives

### Primary Goals
1. **Fix Bug #9:** Real-time progress updates during ingestion
2. **Fix Bug #10:** Display entity/relation counts in UI
3. **Multi-Document Support:** Redesign UI for multiple concurrent uploads
4. **Compact Layout:** Professional, space-efficient document list
5. **User Confidence:** Clear visual feedback at every processing stage

### Success Criteria
- [ ] Progress updates every 5-10 seconds during ingestion
- [ ] UI shows granular chunk progress (e.g., "15/30 chunks - 50%")
- [ ] Entity/Relation counts displayed after ingestion
- [ ] Multiple documents can be uploaded and monitored simultaneously
- [ ] Monitoring panel is collapsible and compact
- [ ] No "frozen UI" experience - always shows something is happening
- [ ] Works perfectly for 50MB documents (15-20 min processing)

---

## 🔍 Current State Analysis

### Current UI Behavior (Test Run #9)

**Timeline Observed:**
```
19:19:30 → Upload starts
19:19:36 → UI shows "graphiti_start (75%)"
19:19:37 → [UI FREEZES] ❄️
19:20:23 → Backend: Chunk 5 (23%) | UI: Still "75%" ❌
19:20:45 → Backend: Chunk 9 (33%) | UI: Still "75%" ❌
19:22:00 → Backend: Chunk 20 (66%) | UI: Still "75%" ❌
19:23:09 → Backend: Chunk 26 (93%) | UI: Still "75%" ❌
19:23:41 → UI finally shows "Complete" ✅

Duration stuck: 4 minutes 11 seconds
User visibility: ZERO
```

### Current UI Components

**Document Card (Single Upload):**
```jsx
<div class="p-6 hover:bg-gray-50 transition-colors">
  <div>test.pdf</div>
  <div>75.88 KB</div>
  <div>Complete</div>
  
  <!-- Detailed Monitoring (always expanded) -->
  <div class="mt-4 border border-gray-200 rounded-lg">
    <button>Hide details</button>
    <div>
      <div>Metrics</div>
      <div>Logs</div>
      <div>Neo4j</div>
      <!-- ... lots of content ... -->
    </div>
  </div>
</div>
```

**Problems:**
1. ❌ Takes up massive vertical space (not scalable for multiple docs)
2. ❌ Monitoring always expanded (cluttered)
3. ❌ No compact view option
4. ❌ Status ("Complete") not prominent enough
5. ❌ No visual hierarchy for multi-document list

### Backend Status API (Current)

**During Ingestion:**
```json
{
  "status": "processing",
  "stage": "ingestion",
  "sub_stage": "graphiti_start",  // ❌ Never updated!
  "progress": 75,                   // ❌ Stuck at 75%!
  "metrics": {
    "num_chunks": 30,
    // ❌ No chunks_completed
    // ❌ No chunks_total
    // ❌ No entities count
    // ❌ No relations count
  }
}
```

**After Completion:**
```json
{
  "status": "completed",
  "stage": "completed",
  "progress": 100,
  "metrics": {
    "num_chunks": 30,
    // ❌ entities: missing
    // ❌ relations: missing
  }
}
```

---

## 🏗️ Architecture Overview

### System Flow: Progress Updates

```
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (processor.py)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  process_document(upload_id, file_path):                        │
│    ├─ Stage 1: Validation (0-25%)                               │
│    │   └─ Update: processing_status[upload_id]                  │
│    │                                                             │
│    ├─ Stage 2: Conversion (25-50%)                              │
│    │   └─ Update: processing_status[upload_id]                  │
│    │                                                             │
│    ├─ Stage 3: Chunking (50-75%)                                │
│    │   └─ Update: processing_status[upload_id]                  │
│    │                                                             │
│    └─ Stage 4: Ingestion (75-100%) ← FIX HERE                   │
│        for i, chunk in enumerate(chunks):                       │
│          ├─ Ingest chunk to Graphiti                            │
│          └─ 🔧 UPDATE processing_status in real-time:           │
│              {                                                   │
│                "sub_stage": "graphiti_episode",                 │
│                "progress": 75 + (25 * (i+1) / total),          │
│                "ingestion_progress": {                          │
│                  "chunks_completed": i + 1,                     │
│                  "chunks_total": len(chunks),                   │
│                  "progress_pct": (i+1)/len(chunks)*100          │
│                }                                                 │
│              }                                                   │
│                                                                   │
│    ├─ After Ingestion: Query Neo4j for counts                   │
│    └─ Update final metrics:                                     │
│        {                                                         │
│          "entities": count(Entity),                             │
│          "relations": count(RELATES_TO)                         │
│        }                                                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    FastAPI Status Endpoint
                    /api/upload/{id}/status
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  FRONTEND (UploadTab.jsx)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  useEffect(() => {                                               │
│    pollInterval = setInterval(() => {                            │
│      getUploadStatus(uploadId)                                   │
│        .then(status => {                                         │
│          setDocuments(prev => [...]) // Update state             │
│        })                                                         │
│    }, 2000) // Poll every 2 seconds                              │
│  }, [uploadId])                                                  │
│                                                                   │
│  Components:                                                     │
│  ├─ DocumentList (Multi-doc support)                            │
│  │   └─ DocumentCard[] (Compact, collapsible)                   │
│  │       ├─ Document Header (always visible)                    │
│  │       │   ├─ Name + Size + Status Badge                      │
│  │       │   └─ Progress Bar (if processing)                    │
│  │       │                                                       │
│  │       └─ Monitoring Panel (collapsible)                      │
│  │           ├─ Show/Hide Toggle                                │
│  │           └─ Tabs: Metrics | Logs | Neo4j                    │
│  │                                                               │
│  └─ MetricsPanel (Enhanced)                                     │
│      ├─ Real-time ingestion progress                            │
│      ├─ Entity/Relation counts                                  │
│      └─ Duration & performance                                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Plan

### Phase 1: Backend Progress Updates (Bug #9 Fix)

**Estimated Time:** 2-3 hours

#### 1.1: Modify `backend/app/core/processor.py`

**File:** `backend/app/core/processor.py`

**Changes:**

```python
async def process_document(upload_id: str, file_path: str, processing_status: dict):
    """Process document with REAL-TIME progress updates"""
    
    try:
        # Stage 1: Validation (0-25%)
        processing_status[upload_id].update({
            "stage": "validation",
            "sub_stage": "checking_file",
            "progress": 5,
        })
        await asyncio.sleep(0.1)  # Allow other tasks to run
        # ... validation logic ...
        
        # Stage 2: Conversion (25-50%)
        processing_status[upload_id].update({
            "stage": "conversion",
            "sub_stage": "docling_converting",
            "progress": 25,
        })
        # ... docling conversion ...
        processing_status[upload_id].update({
            "progress": 50,
            "metrics": {
                "conversion_duration": duration,
                "pages": doc_result.num_pages,
            }
        })
        
        # Stage 3: Chunking (50-75%)
        processing_status[upload_id].update({
            "stage": "chunking",
            "sub_stage": "text_segmentation",
            "progress": 50,
        })
        chunks = await document_chunker.chunk_document(...)
        processing_status[upload_id].update({
            "progress": 75,
            "metrics": {
                "num_chunks": len(chunks),
                "avg_chunk_size": avg_size,
                "chunking_duration": duration,
            }
        })
        
        # Stage 4: Ingestion (75-100%) ← 🔧 FIX HERE
        processing_status[upload_id].update({
            "stage": "ingestion",
            "sub_stage": "graphiti_start",
            "progress": 75,
            "ingestion_progress": {
                "chunks_completed": 0,
                "chunks_total": len(chunks),
                "progress_pct": 0,
                "current_chunk_index": 0,
            }
        })
        
        # REAL-TIME UPDATES during ingestion loop
        for i, chunk in enumerate(chunks):
            # Process chunk
            await graphiti_client.add_episode(
                name=f"{upload_id}_chunk_{i}",
                episode_body=chunk["text"],
                ...
            )
            
            # 🔧 UPDATE STATUS IMMEDIATELY after each chunk
            chunks_completed = i + 1
            ingestion_pct = int((chunks_completed / len(chunks)) * 100)
            overall_progress = 75 + int(25 * chunks_completed / len(chunks))
            
            processing_status[upload_id].update({
                "sub_stage": "graphiti_episode",
                "progress": overall_progress,
                "ingestion_progress": {
                    "chunks_completed": chunks_completed,
                    "chunks_total": len(chunks),
                    "progress_pct": ingestion_pct,
                    "current_chunk_index": i,
                }
            })
            
            # Log progress
            logger.info(
                f"📊 Ingestion progress: {chunks_completed}/{len(chunks)} ({ingestion_pct}%)",
                extra={
                    "upload_id": upload_id,
                    "stage": "ingestion",
                    "chunks_completed": chunks_completed,
                    "chunks_total": len(chunks),
                }
            )
            
            # Allow other tasks to run
            await asyncio.sleep(0.01)
        
        # After ingestion: Query Neo4j for entity/relation counts
        ingestion_end = time.time()
        ingestion_duration = ingestion_end - ingestion_start
        
        # 🔧 QUERY NEO4J FOR COUNTS
        entity_count = await get_entity_count()
        relation_count = await get_relation_count()
        
        # Update final status
        processing_status[upload_id].update({
            "status": "completed",
            "stage": "completed",
            "sub_stage": "finalized",
            "progress": 100,
            "metrics": {
                **processing_status[upload_id]["metrics"],
                "ingestion_duration": ingestion_duration,
                "entities": entity_count,      # ← ADD
                "relations": relation_count,    # ← ADD
            },
            "completed_at": datetime.utcnow().isoformat(),
        })
        
        logger.info(
            f"✅ Processing complete: {len(chunks)} chunks, "
            f"{entity_count} entities, {relation_count} relations"
        )
        
    except Exception as e:
        # Error handling...
        processing_status[upload_id].update({
            "status": "error",
            "error": str(e),
            "progress": processing_status[upload_id].get("progress", 0),
        })
        logger.error(f"❌ Processing failed: {e}")
        raise
```

#### 1.2: Add Neo4j Count Query Functions

**File:** `backend/app/core/processor.py`

```python
async def get_entity_count() -> int:
    """Query Neo4j for Entity node count"""
    try:
        from app.integrations.neo4j import neo4j_client
        
        # Run in thread pool (Neo4j driver is synchronous)
        def _query():
            with neo4j_client.driver.session() as session:
                result = session.run("MATCH (n:Entity) RETURN count(n) as count")
                return result.single()["count"]
        
        count = await asyncio.to_thread(_query)
        return count
    except Exception as e:
        logger.warning(f"Failed to get entity count: {e}")
        return 0


async def get_relation_count() -> int:
    """Query Neo4j for RELATES_TO relationship count"""
    try:
        from app.integrations.neo4j import neo4j_client
        
        def _query():
            with neo4j_client.driver.session() as session:
                result = session.run(
                    "MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count"
                )
                return result.single()["count"]
        
        count = await asyncio.to_thread(_query)
        return count
    except Exception as e:
        logger.warning(f"Failed to get relation count: {e}")
        return 0
```

---

### Phase 2: Enhanced Status Response Schema

**Estimated Time:** 1 hour

#### 2.1: Update Status Response Model

**File:** `backend/app/api/upload.py`

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

class IngestionProgress(BaseModel):
    """Real-time ingestion progress"""
    chunks_completed: int
    chunks_total: int
    progress_pct: int
    current_chunk_index: int


class ProcessingMetrics(BaseModel):
    """Processing metrics"""
    file_size_mb: float
    filename: str
    pages: Optional[int] = None
    conversion_duration: Optional[float] = None
    num_chunks: Optional[int] = None
    avg_chunk_size: Optional[float] = None
    chunking_duration: Optional[float] = None
    ingestion_duration: Optional[float] = None
    entities: Optional[int] = None       # ← ADD
    relations: Optional[int] = None      # ← ADD


class UploadStatusResponse(BaseModel):
    """Enhanced upload status response"""
    status: str  # "processing", "completed", "error"
    stage: str   # "validation", "conversion", "chunking", "ingestion", "completed"
    sub_stage: str
    progress: int  # 0-100
    progress_detail: Optional[Dict[str, Any]] = None
    ingestion_progress: Optional[IngestionProgress] = None  # ← ADD
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metrics: Optional[ProcessingMetrics] = None
    durations: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/upload/{upload_id}/status", response_model=UploadStatusResponse)
async def get_upload_status(upload_id: str):
    """
    Get enhanced processing status with real-time ingestion progress
    """
    if upload_id not in processing_status:
        raise HTTPException(status_code=404, detail="Upload ID not found")
    
    status_data = processing_status[upload_id]
    
    return UploadStatusResponse(**status_data)
```

---

### Phase 3: Frontend Multi-Document UI Redesign

**Estimated Time:** 3-4 hours

#### 3.1: New Component Architecture

**Components to Create/Modify:**

```
frontend/src/components/upload/
├── UploadTab.jsx               (MODIFY - multi-doc state)
├── DocumentList.jsx            (NEW - list container)
├── DocumentCard.jsx            (NEW - compact card with collapse)
├── DocumentHeader.jsx          (NEW - name + status + progress)
├── MonitoringPanel.jsx         (NEW - collapsible monitoring)
├── MetricsPanel.jsx            (MODIFY - real-time updates)
├── ProgressBar.jsx             (MODIFY - ingestion progress)
└── StatusBadge.jsx             (NEW - status indicator)
```

#### 3.2: DocumentList Component (NEW)

**File:** `frontend/src/components/upload/DocumentList.jsx`

```jsx
import React from 'react';
import DocumentCard from './DocumentCard';

export default function DocumentList({ documents }) {
  if (documents.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No documents uploaded yet.</p>
        <p className="text-sm mt-2">Upload a PDF or PPT file to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Uploaded Documents
        </h3>
        <span className="text-sm text-gray-500">
          {documents.length} document{documents.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-2">
        {documents.map((doc) => (
          <DocumentCard key={doc.id} document={doc} />
        ))}
      </div>
    </div>
  );
}
```

#### 3.3: DocumentCard Component (NEW - Compact & Collapsible)

**File:** `frontend/src/components/upload/DocumentCard.jsx`

```jsx
import React, { useState } from 'react';
import DocumentHeader from './DocumentHeader';
import MonitoringPanel from './MonitoringPanel';
import { ChevronDown, ChevronRight } from 'lucide-react';

export default function DocumentCard({ document }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('metrics');

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-all">
      {/* Compact Header - Always Visible */}
      <div 
        className="flex items-center justify-between p-4 bg-white hover:bg-gray-50 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <DocumentHeader document={document} />
        
        <button 
          className="text-gray-400 hover:text-gray-600"
          aria-label={isExpanded ? "Collapse" : "Expand"}
        >
          {isExpanded ? (
            <ChevronDown className="w-5 h-5" />
          ) : (
            <ChevronRight className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Collapsible Monitoring Panel */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50">
          <MonitoringPanel 
            document={document}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
          />
        </div>
      )}
    </div>
  );
}
```

#### 3.4: DocumentHeader Component (NEW - Compact Single Line)

**File:** `frontend/src/components/upload/DocumentHeader.jsx`

```jsx
import React from 'react';
import StatusBadge from './StatusBadge';
import ProgressBar from './ProgressBar';
import { FileText } from 'lucide-react';

export default function DocumentHeader({ document }) {
  const { filename, file_size_mb, status, progress, ingestion_progress } = document;

  return (
    <div className="flex-1 min-w-0">
      {/* Document Info - Single Line */}
      <div className="flex items-center gap-3">
        <FileText className="w-5 h-5 text-blue-500 flex-shrink-0" />
        
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <span className="font-medium text-gray-900 truncate">
            {filename}
          </span>
          <span className="text-sm text-gray-500 flex-shrink-0">
            {file_size_mb.toFixed(2)} MB
          </span>
        </div>

        <StatusBadge status={status} />
      </div>

      {/* Progress Bar (only if processing) */}
      {status === 'processing' && (
        <div className="mt-2">
          <ProgressBar 
            progress={progress}
            ingestion_progress={ingestion_progress}
            stage={document.stage}
            sub_stage={document.sub_stage}
          />
        </div>
      )}
    </div>
  );
}
```

#### 3.5: StatusBadge Component (NEW)

**File:** `frontend/src/components/upload/StatusBadge.jsx`

```jsx
import React from 'react';
import { CheckCircle, Clock, AlertCircle, Loader } from 'lucide-react';

const statusConfig = {
  processing: {
    label: 'Processing',
    icon: Loader,
    className: 'bg-blue-100 text-blue-800 border-blue-200',
    iconClassName: 'animate-spin',
  },
  completed: {
    label: 'Complete',
    icon: CheckCircle,
    className: 'bg-green-100 text-green-800 border-green-200',
    iconClassName: '',
  },
  error: {
    label: 'Error',
    icon: AlertCircle,
    className: 'bg-red-100 text-red-800 border-red-200',
    iconClassName: '',
  },
  pending: {
    label: 'Pending',
    icon: Clock,
    className: 'bg-gray-100 text-gray-800 border-gray-200',
    iconClassName: '',
  },
};

export default function StatusBadge({ status }) {
  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;

  return (
    <div 
      className={`
        inline-flex items-center gap-1.5 px-3 py-1 rounded-full 
        border text-sm font-medium
        ${config.className}
      `}
    >
      <Icon className={`w-4 h-4 ${config.iconClassName}`} />
      {config.label}
    </div>
  );
}
```

#### 3.6: Enhanced ProgressBar Component (MODIFY)

**File:** `frontend/src/components/upload/ProgressBar.jsx`

```jsx
import React from 'react';

export default function ProgressBar({ progress, ingestion_progress, stage, sub_stage }) {
  // Determine progress label based on stage
  const getProgressLabel = () => {
    if (stage === 'validation') {
      return 'Validating file...';
    } else if (stage === 'conversion') {
      return 'Converting document...';
    } else if (stage === 'chunking') {
      return 'Segmenting text...';
    } else if (stage === 'ingestion') {
      if (ingestion_progress) {
        const { chunks_completed, chunks_total, progress_pct } = ingestion_progress;
        return `Ingesting chunks (${chunks_completed}/${chunks_total} - ${progress_pct}%)`;
      }
      return 'Starting ingestion...';
    } else if (stage === 'completed') {
      return 'Complete!';
    }
    return 'Processing...';
  };

  const progressLabel = getProgressLabel();

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">{progressLabel}</span>
        <span className="font-medium text-gray-900">{progress}%</span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`
            h-full rounded-full transition-all duration-500 ease-out
            ${stage === 'completed' ? 'bg-green-500' : 'bg-blue-500'}
          `}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Sub-progress for ingestion (optional) */}
      {ingestion_progress && stage === 'ingestion' && (
        <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
          <div className="flex-1 bg-gray-100 rounded-full h-1">
            <div
              className="h-full bg-blue-400 rounded-full transition-all duration-300"
              style={{ width: `${ingestion_progress.progress_pct}%` }}
            />
          </div>
          <span>
            Chunk {ingestion_progress.current_chunk_index + 1}/{ingestion_progress.chunks_total}
          </span>
        </div>
      )}
    </div>
  );
}
```

#### 3.7: Enhanced MetricsPanel Component (MODIFY)

**File:** `frontend/src/components/upload/MetricsPanel.jsx`

```jsx
// ... existing imports ...

export default function MetricsPanel({ document, status, metrics, metadata }) {
  // ... existing code ...

  return (
    <div className="space-y-6">
      {/* Performance Indicator */}
      <div>
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Performance:</h4>
        {/* ... existing performance code ... */}
      </div>

      {/* File Information */}
      <div>
        <h4 className="text-sm font-semibold text-gray-900 mb-3">File Information</h4>
        <div className="grid grid-cols-2 gap-4">
          <MetricCard
            icon={HardDrive}
            label="File Size"
            value={metrics?.file_size_mb?.toFixed(2)}
            unit="MB"
            color="gray"
          />
          <MetricCard
            icon={FileText}
            label="Pages"
            value={metadata?.pages || metrics?.pages}
            unit="pages"
            color="gray"
          />
        </div>
      </div>

      {/* Processing Results */}
      <div>
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Processing Results</h4>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard
            icon={Layers}
            label="Chunks"
            value={metrics?.num_chunks}
            unit="chunks"
            color="purple"
          />
          <MetricCard
            icon={GitFork}
            label="Entities"
            value={metrics?.entities || '—'}  {/* ← NOW DISPLAYS ACTUAL COUNT */}
            unit={metrics?.entities ? 'found' : ''}
            color="green"
          />
          <MetricCard
            icon={Network}
            label="Relations"
            value={metrics?.relations || '—'}  {/* ← NOW DISPLAYS ACTUAL COUNT */}
            unit={metrics?.relations ? 'found' : ''}
            color="blue"
          />
        </div>
      </div>

      {/* Duration Breakdown */}
      {/* ... existing duration code ... */}
    </div>
  );
}
```

#### 3.8: Update UploadTab with Multi-Document Support (MODIFY)

**File:** `frontend/src/components/upload/UploadTab.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import DocumentList from './DocumentList';
import { uploadDocument, getUploadStatus } from '@/lib/api';

export default function UploadTab() {
  const [documents, setDocuments] = useState([]);
  const [uploadingFiles, setUploadingFiles] = useState(new Set());

  // Poll for status updates
  useEffect(() => {
    const activeUploads = documents.filter(
      doc => doc.status === 'processing'
    );

    if (activeUploads.length === 0) return;

    const pollInterval = setInterval(async () => {
      // Poll all active uploads in parallel
      const statusPromises = activeUploads.map(doc =>
        getUploadStatus(doc.id)
          .then(status => ({ id: doc.id, status }))
          .catch(err => {
            console.error(`Failed to get status for ${doc.id}:`, err);
            return null;
          })
      );

      const results = await Promise.all(statusPromises);

      setDocuments(prev => {
        const updated = [...prev];
        results.forEach(result => {
          if (!result) return;
          
          const index = updated.findIndex(d => d.id === result.id);
          if (index !== -1) {
            updated[index] = {
              ...updated[index],
              ...result.status,
              filename: updated[index].filename, // Preserve filename
              file_size_mb: updated[index].file_size_mb, // Preserve size
            };
          }
        });
        return updated;
      });
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [documents]);

  const handleFileUpload = async (file) => {
    const uploadId = generateUploadId();
    
    // Add to documents list immediately (optimistic UI)
    const newDoc = {
      id: uploadId,
      filename: file.name,
      file_size_mb: file.size / (1024 * 1024),
      status: 'uploading',
      progress: 0,
      stage: 'uploading',
      sub_stage: 'uploading',
      metrics: {},
    };

    setDocuments(prev => [newDoc, ...prev]);
    setUploadingFiles(prev => new Set([...prev, uploadId]));

    try {
      const response = await uploadDocument(file, {
        title: file.name,
      });

      // Update with server response
      setDocuments(prev => prev.map(doc =>
        doc.id === uploadId
          ? { ...doc, ...response, status: 'processing' }
          : doc
      ));
    } catch (error) {
      console.error('Upload failed:', error);
      setDocuments(prev => prev.map(doc =>
        doc.id === uploadId
          ? { ...doc, status: 'error', error: error.message }
          : doc
      ));
    } finally {
      setUploadingFiles(prev => {
        const updated = new Set(prev);
        updated.delete(uploadId);
        return updated;
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8">
        {/* ... existing upload UI ... */}
      </div>

      {/* Document List */}
      <DocumentList documents={documents} />
    </div>
  );
}

function generateUploadId() {
  return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
```

---

## 🧪 Testing Plan

### Phase 1: Backend Progress Updates

**Test 1.1: Real-time Status Updates**
```bash
# Upload test.pdf
upload_id=$(curl -X POST http://localhost:8000/api/upload \
  -F "file=@TestPDF/test.pdf" | jq -r '.upload_id')

# Poll status every 2 seconds
watch -n 2 "curl -s http://localhost:8000/api/upload/${upload_id}/status | jq '.progress, .ingestion_progress'"

# Expected output progression:
# 0  → {"chunks_completed": 0, "chunks_total": 30, "progress_pct": 0}
# 25 → (conversion)
# 50 → (chunking)
# 75 → {"chunks_completed": 0, "chunks_total": 30, "progress_pct": 0}
# 78 → {"chunks_completed": 3, "chunks_total": 30, "progress_pct": 10}
# 83 → {"chunks_completed": 10, "chunks_total": 30, "progress_pct": 33}
# 91 → {"chunks_completed": 20, "chunks_total": 30, "progress_pct": 66}
# 100 → {"chunks_completed": 30, "chunks_total": 30, "progress_pct": 100}
```

**Test 1.2: Entity/Relation Counts**
```bash
# After completion, check final metrics
curl -s http://localhost:8000/api/upload/${upload_id}/status | jq '.metrics'

# Expected output:
# {
#   "num_chunks": 30,
#   "entities": 73,      ← MUST BE PRESENT
#   "relations": 80,     ← MUST BE PRESENT
#   ...
# }
```

### Phase 2: Frontend Multi-Document UI

**Test 2.1: Single Document Upload**
- [ ] Upload test.pdf
- [ ] Verify compact header shows: name + size + status badge
- [ ] Verify progress bar shows real-time updates
- [ ] Verify ingestion progress shows "Ingesting chunks (X/30 - Y%)"
- [ ] Verify monitoring panel is collapsed by default
- [ ] Verify clicking header expands/collapses panel
- [ ] Verify entity/relation counts display after completion

**Test 2.2: Multi-Document Upload**
- [ ] Upload 3 documents simultaneously
- [ ] Verify all 3 appear in the list
- [ ] Verify each has independent progress tracking
- [ ] Verify can expand/collapse each independently
- [ ] Verify list is sorted (most recent first)
- [ ] Verify scrolling works for many documents

**Test 2.3: Large Document (50MB)**
- [ ] Upload large PDF (100+ pages)
- [ ] Verify progress updates every 5-10 seconds
- [ ] Verify no "frozen UI" experience
- [ ] Verify ingestion progress shows chunk-by-chunk updates
- [ ] Verify completion after 15-20 minutes
- [ ] Verify user confidence maintained throughout

### Phase 3: Edge Cases

**Test 3.1: Error Handling**
- [ ] Upload corrupted PDF
- [ ] Verify error status badge displayed
- [ ] Verify error message shown in monitoring panel
- [ ] Verify other uploads not affected

**Test 3.2: Concurrent Uploads**
- [ ] Upload 5 documents at once
- [ ] Verify all tracked independently
- [ ] Verify backend handles concurrent processing
- [ ] Verify UI remains responsive

**Test 3.3: Page Refresh**
- [ ] Start upload
- [ ] Refresh page mid-processing
- [ ] Verify upload continues in background
- [ ] Verify status restored on page load (if implemented)

---

## 📊 Success Metrics

### User Experience
- [ ] No "frozen UI" complaints
- [ ] Users can see progress at all times
- [ ] Processing times feel transparent
- [ ] Entity/Relation counts visible
- [ ] Multi-document uploads supported

### Technical Performance
- [ ] Progress updates every 2-5 seconds
- [ ] Status API response < 50ms
- [ ] UI renders without jank
- [ ] Supports 10+ concurrent uploads
- [ ] Memory usage remains stable

### Quality Metrics
- [ ] Zero regressions in existing functionality
- [ ] All tests pass
- [ ] No console errors
- [ ] Responsive design maintained
- [ ] Accessibility (ARIA labels, keyboard navigation)

---

## 🗓️ Implementation Timeline

### Day 1: Backend Progress Updates (6 hours)
- **Hour 1-2:** Modify `processor.py` with real-time updates
- **Hour 3:** Add Neo4j count query functions
- **Hour 4:** Update status API response schema
- **Hour 5-6:** Test backend progress updates thoroughly

### Day 2: Frontend UI Redesign (6 hours)
- **Hour 1-2:** Create new components (DocumentList, DocumentCard, etc.)
- **Hour 3-4:** Implement compact header and collapsible panels
- **Hour 5:** Enhance MetricsPanel with entity/relation counts
- **Hour 6:** Update UploadTab for multi-document support

### Day 3: Testing & Polish (2 hours)
- **Hour 1:** End-to-end testing (small and large documents)
- **Hour 2:** UI polish, bug fixes, edge cases

**Total Time:** ~14 hours over 2-3 days

---

## 🚀 Deployment Steps

### 1. Backend Deployment
```bash
# Rebuild backend with changes
docker-compose -f docker/docker-compose.dev.yml build backend

# Restart backend
docker-compose -f docker/docker-compose.dev.yml restart backend

# Verify health
curl http://localhost:8000/api/health
```

### 2. Frontend Deployment
```bash
# Frontend auto-reloads with volume mounts (dev)
# For production:
cd frontend
npm run build
```

### 3. Validation
```bash
# Test E2E
./scripts/init-e2e-test.sh
# Upload test.pdf via UI
# Monitor progress in browser DevTools Network tab
```

---

## 📝 Documentation Updates Required

After implementation:

1. **Update TESTING-LOG.md:**
   - Mark Bug #9 as RESOLVED
   - Mark Bug #10 as RESOLVED
   - Add Test Run #10 (UI Progress Fix Validation)

2. **Update FIXES-LOG.md:**
   - Add Fix #11: Real-time Progress Feedback
   - Add Fix #12: Entity/Relation Counts Display
   - Add Fix #13: Multi-Document UI Support

3. **Update docs/UI.md:**
   - Document new components
   - Add screenshots of compact document list
   - Explain collapsible monitoring panels

4. **Update CURRENT-CONTEXT.md:**
   - Update "Current Status" to reflect UI improvements
   - Add "UI fully production-ready" to achievements

---

## 🎯 Acceptance Criteria

### Must Have (P0)
- [x] Real-time progress updates during ingestion (every 5-10s)
- [x] Granular chunk-level feedback: "Ingesting chunks (15/30 - 50%)"
- [x] Entity/Relation counts displayed correctly
- [x] No "frozen UI" experience for any document size
- [x] Multi-document list with status badges
- [x] Collapsible monitoring panels

### Should Have (P1)
- [x] Compact single-line document headers
- [x] Smooth progress bar animations
- [x] Professional status badges (Complete, Processing, Error)
- [x] Independent progress tracking per document
- [x] Time estimates (ETA for completion)

### Nice to Have (P2)
- [ ] Persistent upload history (survives page refresh)
- [ ] Export logs/metrics as JSON
- [ ] Bulk delete completed documents
- [ ] Filter/sort document list
- [ ] Search documents by name

---

## 🔍 Risk Analysis

### Low Risk
- Backend progress updates (isolated to processor.py)
- Status API schema changes (backward compatible)

### Medium Risk
- Frontend UI redesign (extensive changes, but no breaking API changes)
- Multi-document state management (potential race conditions)

### Mitigation Strategies
1. **Thorough Testing:** Test with 1, 3, 5, 10 concurrent uploads
2. **Gradual Rollout:** Deploy backend first, then frontend
3. **Monitoring:** Watch backend logs for performance issues
4. **Rollback Plan:** Keep previous UI components for quick revert

---

## 📚 References

- **Related Issues:** Bug #9 (Progress Feedback), Bug #10 (Entity/Relation Counts)
- **Related Tests:** Test Run #9 (UI Test - Enhanced Warmup Validation)
- **Related Docs:** TESTING-LOG.md, FIXES-LOG.md, UI.md
- **Design Inspiration:** GitHub Actions progress UI, Vercel deployments UI

---

**Status:** 🟢 READY FOR IMPLEMENTATION  
**Priority:** 🔴 P0 - CRITICAL  
**Blocking:** Production deployment, large document testing  
**Next Step:** Implement Phase 1 (Backend Progress Updates)

