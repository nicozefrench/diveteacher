# 🎨 PHASE 1.2 - Frontend Admin UI Redevelopment

**Document Version:** 1.2 (Implementation Complete)  
**Target AI Agent:** Claude Sonnet 4.5  
**Created:** October 28, 2025  
**Updated:** October 28, 2025  
**Status:** ✅ IMPLEMENTATION COMPLETE - READY FOR TESTING  
**Reference:** ARIA Frontend Development Guide (Production-Proven Patterns)

**🎯 SCOPE CLARIFICATION:**
- ✅ **LOCAL DEVELOPMENT ONLY** - No Vercel deployment in Phase 1.2
- ✅ **IN-MEMORY STORAGE** - React state only (no persistence yet)
- ⏸️ **Supabase Integration** - Deferred to Phase 1.3 (Auth + Conversations)
- ⏸️ **Production Deployment** - Deferred to Phase 9 (after all local testing)

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Gap Analysis (ARIA vs Current)](#gap-analysis)
4. [Target Architecture](#target-architecture)
5. [Implementation Plan](#implementation-plan)
6. [Technical Specifications](#technical-specifications)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Plan](#deployment-plan)
9. [Success Criteria](#success-criteria)

---

## Executive Summary

### Objective

Redevelop the DiveTeacher frontend UI to be a **production-ready, full-featured admin interface** based on ARIA's proven patterns, with two main tabs:
1. **Document Upload & Processing** - Monitor ingestion pipeline step-by-step
2. **RAG Query Interface** - Chat with the LLM using knowledge graph context

### Why This Matters

**Current Issues:**
- ❌ UI not connected to backend ingestion pipeline
- ❌ Chat not connected to Ollama LLM
- ❌ No real-time status monitoring for document processing
- ❌ No proper navigation (tabs)
- ❌ No styling system (pure Tailwind = unmaintainable)
- ❌ No error handling or retry logic
- ❌ Not production-ready for Vercel deployment

**Target State (ARIA-Inspired):**
- ✅ Two-tab navigation (Upload | Query)
- ✅ Real-time document processing monitoring (4 stages)
- ✅ Connected to `/api/upload` and `/api/query/stream`
- ✅ Semantic CSS classes + Tailwind for layout
- ✅ Production-ready build for Vercel
- ✅ Mobile-responsive (PWA-ready)
- ✅ Error handling with retry
- ✅ Health checks and status indicators

### Timeline

**Estimated:** 2-3 days (14-18 hours) - **LOCAL DEVELOPMENT ONLY**
- Day 1: Architecture + Document Upload Tab (7h)
- Day 2: RAG Query Tab + Integration (7h)
- Day 3: Testing + Polish (2-4h)

**⏸️ DEFERRED TO LATER PHASES:**
- Phase 1.3: Supabase integration (auth + conversation persistence)
- Phase 9: Vercel production deployment

---

## Current State Analysis

### Existing Tech Stack

**Good (Keep These):**
```json
{
  "react": "^18.3.1",           // ✅ Latest stable
  "react-dom": "^18.3.1",
  "vite": "^6.0.1",              // ✅ Fast builds
  "tailwindcss": "^3.4.15",     // ✅ Stable v3
  "lucide-react": "^0.460.0",   // ✅ Icons
  "react-markdown": "^9.0.1"    // ✅ For chat
}
```

**Missing (Need to Add):**
```json
{
  "react-router-dom": "^6.8.1",  // For tabs/navigation
  "clsx": "^2.1.1",              // Already present
  "tailwind-merge": "^2.5.4"     // Already present
}
```

### File Structure (Current)

```
frontend/
├── src/
│   ├── App.jsx                 # ❌ Single-page, no routing
│   ├── components/
│   │   ├── FileUpload.jsx      # ⚠️ Basic, needs real-time status
│   │   └── Chat.jsx            # ❌ Not connected to /api/query/stream
│   ├── index.css               # ⚠️ Pure Tailwind (hard to maintain)
│   └── main.jsx
├── package.json
├── vite.config.js              # ✅ Has proxy setup
└── tailwind.config.js
```

### Current Issues (Detailed)

**1. App.jsx:**
- ❌ No tabs/navigation
- ❌ Split-screen layout (not scalable)
- ❌ No route management
- ⚠️ Basic state management (OK for MVP)

**2. FileUpload.jsx:**
- ⚠️ Polls `/api/upload/status/{id}` (OK)
- ❌ Doesn't show 4-stage pipeline (validation, conversion, chunking, ingestion)
- ❌ No detailed progress for each stage
- ❌ No document list with per-document status
- ❌ No error retry mechanism

**3. Chat.jsx:**
- ❌ Queries `/api/query?question=` (wrong endpoint)
- ❌ Should use `/api/query/stream` (SSE format)
- ❌ Doesn't parse SSE format correctly (`data: {...}`)
- ❌ No context display (sources, facts)
- ❌ No loading states per message

**4. Styling:**
- ❌ 100% inline Tailwind classes
- ❌ No semantic CSS classes
- ❌ No theme variables (hard to rebrand)
- ❌ No DiveTeacher branding (ocean theme)

**5. Vite Config:**
- ✅ Proxy `/api` → `http://localhost:8000` (GOOD)
- ❌ No environment loading for production URLs
- ❌ No production build optimizations

---

## Gap Analysis (ARIA vs Current)

| Feature | ARIA UI | DiveTeacher Current | Gap | Priority |
|---------|---------|---------------------|-----|----------|
| **Navigation** | Tab-based routing | Single page | Need tabs | 🔴 CRITICAL |
| **Document Upload** | Real-time status | Basic upload | Need 4-stage monitor | 🔴 CRITICAL |
| **Chat Interface** | SSE streaming | Wrong endpoint | Need SSE connection | 🔴 CRITICAL |
| **Styling System** | Hybrid CSS+Tailwind | Pure Tailwind | Need semantic classes | 🟡 HIGH |
| **Error Handling** | Comprehensive | Basic try-catch | Need retry logic | 🟡 HIGH |
| **Mobile Responsive** | PWA-ready | Desktop-only | Need breakpoints | 🟢 MEDIUM |
| **Health Checks** | Built-in | None | Need indicators | 🟢 MEDIUM |
| **Theme System** | CSS variables | Hardcoded | Need ocean theme | 🟢 MEDIUM |

### ARIA Patterns to Adopt

**1. Hybrid Styling (CRITICAL):**
```css
/* Semantic component class */
.document-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

/* In JSX: */
<div className="document-card">...</div>
```

**2. Tab-Based Navigation:**
```jsx
// ARIA pattern: Simple tab state
const [activeTab, setActiveTab] = useState('upload');
```

**3. Real-Time Status Monitoring:**
```jsx
// Poll backend, update per-stage progress
useEffect(() => {
  const interval = setInterval(() => {
    fetchStatus(uploadId);
  }, 1000);
  return () => clearInterval(interval);
}, [uploadId]);
```

**4. SSE Streaming:**
```jsx
// Correct SSE handling
const response = await fetch('/api/query/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question, ... })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      // Handle data.token, data.done, etc.
    }
  }
}
```

---

## Target Architecture

### New File Structure

```
frontend/
├── src/
│   ├── main.jsx                   # Entry point
│   ├── App.jsx                    # Root with tab navigation
│   ├── components/
│   │   ├── upload/                # Upload tab feature
│   │   │   ├── DocumentUpload.jsx      # Upload dropzone
│   │   │   ├── DocumentList.jsx        # List with status
│   │   │   ├── DocumentItem.jsx        # Single doc card
│   │   │   └── StageProgress.jsx       # 4-stage progress bar
│   │   ├── query/                 # Query tab feature
│   │   │   ├── ChatInterface.jsx       # Main chat UI
│   │   │   ├── MessageList.jsx         # Message display
│   │   │   ├── MessageItem.jsx         # Single message
│   │   │   ├── InputBar.jsx            # Query input
│   │   │   └── ContextDisplay.jsx      # Show retrieved facts
│   │   ├── ui/                    # Reusable UI components
│   │   │   ├── Card.jsx
│   │   │   ├── Button.jsx
│   │   │   ├── Badge.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   └── Spinner.jsx
│   │   └── layout/                # Layout components
│   │       ├── Header.jsx              # Top header
│   │       ├── TabNavigation.jsx       # Tabs
│   │       └── Footer.jsx
│   ├── lib/
│   │   ├── utils.js                    # Helper functions (cn, etc.)
│   │   └── api.js                      # API client functions
│   ├── config/
│   │   └── brand.js                    # DiveTeacher branding
│   ├── styles/
│   │   └── diveteacher-theme.css       # Ocean theme CSS
│   └── index.css                       # Global styles + Tailwind
├── public/
│   ├── icons/                          # PWA icons
│   ├── manifest.json                   # PWA manifest
│   └── favicon.svg
├── .env.example                        # Environment template
├── package.json
├── vite.config.js
└── tailwind.config.js
```

### Component Hierarchy

```
App.jsx
├── Header (DiveTeacher branding)
├── TabNavigation (Upload | Query)
├── Tab Content:
│   ├── Upload Tab:
│   │   ├── DocumentUpload (dropzone)
│   │   └── DocumentList
│   │       └── DocumentItem (per doc)
│   │           └── StageProgress (4 stages)
│   └── Query Tab:
│       └── ChatInterface
│           ├── MessageList
│           │   └── MessageItem
│           ├── ContextDisplay (show facts)
│           └── InputBar
└── Footer
```

---

## Implementation Plan

### Phase 1.2.1: Project Setup & Architecture (2h)

**Tasks:**
1. ✅ Install dependencies
2. ✅ Create new folder structure
3. ✅ Set up CSS theme system
4. ✅ Create reusable UI components
5. ✅ Configure Vite for production

**Files to Create (8):**
- `src/config/brand.js`
- `src/styles/diveteacher-theme.css`
- `src/lib/utils.js`
- `src/lib/api.js`
- `src/components/ui/Card.jsx`
- `src/components/ui/Button.jsx`
- `src/components/ui/Badge.jsx`
- `src/components/ui/ProgressBar.jsx`

**Deliverables:**
- ✅ Theme system working (ocean blue colors)
- ✅ Reusable UI components styled with semantic classes
- ✅ Vite config updated for production

---

### Phase 1.2.2: Document Upload Tab (6h)

**Objective:** Real-time document processing monitoring with 4-stage pipeline.

**Tasks:**
1. Create `DocumentUpload.jsx` (dropzone)
2. Create `DocumentList.jsx` (list of uploads)
3. Create `DocumentItem.jsx` (per-document card)
4. Create `StageProgress.jsx` (4-stage progress indicator)
5. Integrate with `/api/upload` and `/api/upload/{id}/status`
6. Implement polling for real-time updates
7. Add error handling and retry

**API Integration:**

**POST /api/upload:**
```javascript
const formData = new FormData();
formData.append('file', file);

const response = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});

const { upload_id, filename } = await response.json();
```

**GET /api/upload/{id}/status:**
```javascript
const response = await fetch(`/api/upload/${upload_id}/status`);
const status = await response.json();

// Expected format:
{
  "status": "processing",       // pending, processing, completed, failed
  "stage": "ingestion",         // validation, conversion, chunking, ingestion
  "progress": 75,               // 0-100
  "started_at": "2025-10-28T...",
  "completed_at": null,
  "error": null,
  "filename": "Nitrox.pdf",
  "file_size": 1234567,
  "metadata": {
    "chunks": 72,
    "entities": 45,
    "relations": 120
  }
}
```

**Stage Mapping (4 Stages):**
```javascript
const stages = [
  { key: 'validation', label: 'Validation', progress: 0-25 },
  { key: 'conversion', label: 'Conversion', progress: 25-50 },
  { key: 'chunking', label: 'Chunking', progress: 50-75 },
  { key: 'ingestion', label: 'Ingestion', progress: 75-100 }
];
```

**Real-Time Status Polling:**
```jsx
useEffect(() => {
  if (status === 'processing') {
    const interval = setInterval(() => {
      fetchStatus(uploadId);
    }, 1000); // Poll every 1 second
    
    return () => clearInterval(interval);
  }
}, [uploadId, status]);
```

**Files to Create (5):**
- `src/components/upload/DocumentUpload.jsx` (150 lines)
- `src/components/upload/DocumentList.jsx` (80 lines)
- `src/components/upload/DocumentItem.jsx` (120 lines)
- `src/components/upload/StageProgress.jsx` (100 lines)
- `src/lib/api.js` - `uploadDocument()`, `getUploadStatus()` (50 lines)

**Deliverables:**
- ✅ Document upload dropzone functional
- ✅ Document list shows all uploads
- ✅ Per-document card shows 4-stage progress
- ✅ Real-time status updates (polling)
- ✅ Error handling with retry button

---

### Phase 1.2.3: RAG Query Tab (6h)

**Objective:** Chat interface connected to `/api/query/stream` with SSE streaming.

**Tasks:**
1. Create `ChatInterface.jsx` (main container)
2. Create `MessageList.jsx` (display messages)
3. Create `MessageItem.jsx` (user/assistant message)
4. Create `InputBar.jsx` (query input)
5. Create `ContextDisplay.jsx` (show retrieved facts)
6. Integrate with `/api/query/stream` (SSE)
7. Parse SSE format correctly
8. Display streaming tokens in real-time

**API Integration:**

**POST /api/query/stream:**
```javascript
const response = await fetch('/api/query/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "What is the maximum depth for recreational diving?",
    temperature: 0.7,
    max_tokens: 2000
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();
let buffer = '';

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split('\n');
  
  // Process all complete lines
  buffer = lines.pop(); // Keep incomplete line in buffer
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      
      if (data.token) {
        // Append token to message
        updateMessage(data.token);
      } else if (data.done) {
        // Streaming complete
        finalizeMessage(data);
      } else if (data.error) {
        // Handle error
        handleError(data.error);
      }
    }
  }
}
```

**SSE Data Format:**
```javascript
// Token event
data: {"token": "The", "index": 1}

// Token event
data: {"token": " maximum", "index": 2}

// Done event
data: {"done": true, "token_count": 150, "duration_seconds": 12.5, "tokens_per_second": 12.0}

// Special signal
data: [DONE]
```

**Message State Management:**
```jsx
const [messages, setMessages] = useState([]);

// Add user message
setMessages(prev => [...prev, {
  id: Date.now(),
  role: 'user',
  content: question,
  timestamp: Date.now()
}]);

// Add assistant message (initially empty)
const assistantId = Date.now();
setMessages(prev => [...prev, {
  id: assistantId,
  role: 'assistant',
  content: '',
  streaming: true,
  timestamp: Date.now()
}]);

// Update assistant message as tokens arrive
setMessages(prev => prev.map(msg => 
  msg.id === assistantId 
    ? { ...msg, content: msg.content + token }
    : msg
));

// Finalize when done
setMessages(prev => prev.map(msg => 
  msg.id === assistantId 
    ? { ...msg, streaming: false, stats: data }
    : msg
));
```

**Files to Create (5):**
- `src/components/query/ChatInterface.jsx` (120 lines)
- `src/components/query/MessageList.jsx` (60 lines)
- `src/components/query/MessageItem.jsx` (100 lines)
- `src/components/query/InputBar.jsx` (80 lines)
- `src/components/query/ContextDisplay.jsx` (60 lines)
- `src/lib/api.js` - `streamQuery()` (80 lines)

**Deliverables:**
- ✅ Chat interface working with SSE streaming
- ✅ Messages display user/assistant correctly
- ✅ Tokens stream in real-time (visible typing)
- ✅ Context facts displayed (when available)
- ✅ Loading states and error handling

---

### Phase 1.2.4: Navigation & Layout (2h)

**Objective:** Tab-based navigation between Upload and Query.

**Tasks:**
1. Create `Header.jsx` (DiveTeacher branding)
2. Create `TabNavigation.jsx` (Upload | Query tabs)
3. Create `Footer.jsx` (system info)
4. Update `App.jsx` with tab state
5. Style tabs with active/inactive states

**Tab State Management:**
```jsx
function App() {
  const [activeTab, setActiveTab] = useState('upload');
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <TabNavigation activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1">
        {activeTab === 'upload' && <UploadTab />}
        {activeTab === 'query' && <QueryTab />}
      </main>
      
      <Footer />
    </div>
  );
}
```

**Files to Create (3):**
- `src/components/layout/Header.jsx` (60 lines)
- `src/components/layout/TabNavigation.jsx` (70 lines)
- `src/components/layout/Footer.jsx` (40 lines)

**Deliverables:**
- ✅ Header with DiveTeacher branding
- ✅ Tab navigation working (Upload | Query)
- ✅ Active tab visually distinct
- ✅ Footer with system info

---

### Phase 1.2.5: Styling & Theme System (2h)

**Objective:** Implement DiveTeacher ocean theme with semantic CSS classes.

**Tasks:**
1. Define CSS variables for ocean theme
2. Create semantic component classes
3. Update Tailwind config with custom colors
4. Apply theme to all components
5. Ensure dark mode compatibility (future)

**Theme System:**

**src/styles/diveteacher-theme.css:**
```css
:root {
  /* DiveTeacher Ocean Theme */
  --dive-primary: #0077BE;      /* Deep ocean blue */
  --dive-secondary: #00A8E8;    /* Bright aqua */
  --dive-accent: #00C9FF;       /* Light cyan */
  --dive-dark: #003D5B;         /* Dark navy */
  
  /* Backgrounds */
  --bg-primary: #ffffff;
  --bg-secondary: #f0f9ff;      /* Light blue tint */
  --bg-card: #ffffff;
  
  /* Text */
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  
  /* Borders */
  --border-color: #e2e8f0;
  --border-active: #0077BE;
  
  /* Status colors */
  --status-success: #10b981;
  --status-warning: #f59e0b;
  --status-error: #ef4444;
  --status-info: #3b82f6;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 119, 190, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 119, 190, 0.2);
}

/* Semantic Component Classes */

.dive-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease;
}

.dive-card:hover {
  box-shadow: var(--shadow-md);
}

.dive-button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.dive-button-primary {
  background: var(--dive-primary);
  color: white;
}

.dive-button-primary:hover {
  background: var(--dive-dark);
}

.dive-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.dive-badge-success {
  background: #d1fae5;
  color: #065f46;
}

.dive-badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.dive-badge-error {
  background: #fee2e2;
  color: #991b1b;
}

.dive-progress-bar {
  width: 100%;
  height: 0.5rem;
  background: #e2e8f0;
  border-radius: 9999px;
  overflow: hidden;
}

.dive-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--dive-primary), var(--dive-secondary));
  transition: width 0.3s ease;
}

.dive-tab {
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dive-tab:hover {
  color: var(--dive-primary);
}

.dive-tab-active {
  color: var(--dive-primary);
  border-bottom-color: var(--dive-primary);
}
```

**tailwind.config.js:**
```javascript
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        dive: {
          primary: '#0077BE',
          secondary: '#00A8E8',
          accent: '#00C9FF',
          dark: '#003D5B',
        }
      }
    }
  }
}
```

**Files to Modify:**
- `src/styles/diveteacher-theme.css` (NEW, 200 lines)
- `tailwind.config.js` (UPDATE)
- `src/index.css` (IMPORT theme)

**Deliverables:**
- ✅ Ocean theme CSS variables defined
- ✅ Semantic component classes created
- ✅ Tailwind config updated
- ✅ All components using semantic classes

---

### Phase 1.2.6: Testing & Polish (2-4h)

**Objective:** End-to-end testing, bug fixes, and UX polish.

**⚠️ SCOPE: LOCAL TESTING ONLY (No production deployment)**

**Tasks:**
1. Test document upload with real PDFs
2. Test all 4 stages of processing
3. Test error handling and retries
4. Test RAG query with streaming
5. Test SSE parsing edge cases
6. Test mobile responsive breakpoints
7. Fix any bugs found
8. Polish animations and transitions
9. Add loading skeletons

**Test Cases:**

**Upload Tab:**
- [ ] Upload PDF → See 4 stages progress
- [ ] Upload invalid file → See error
- [ ] Cancel upload → Clean state
- [ ] Retry failed upload → Works
- [ ] Multiple uploads → Each tracked independently
- [ ] Poll interval stops when complete

**Query Tab:**
- [ ] Send question → See streaming response
- [ ] Empty knowledge graph → See "no context" message
- [ ] Long response → Scrolls automatically
- [ ] Network error → Shows error message
- [ ] Markdown rendering → Works (bold, lists, code)
- [ ] Context display → Shows facts (if available)

**Mobile Responsive:**
- [ ] Works on 375px (iPhone SE)
- [ ] Works on 768px (iPad)
- [ ] Works on 1024px (desktop)
- [ ] Tabs stack vertically on mobile
- [ ] Chat input resizes properly

**Deliverables:**
- ✅ All test cases passing
- ✅ No console errors
- ✅ Smooth animations
- ✅ Loading states everywhere

---

### ~~Phase 1.2.7: Vercel Deployment Setup~~ ⏸️ DEFERRED

**⚠️ THIS PHASE IS DEFERRED TO PHASE 9**

**Rationale:**
- Phase 1.2 focuses on **local development and testing only**
- No production deployment until entire system is validated locally (Phases 1-8)
- Vercel deployment will be part of Phase 9 when:
  - ✅ All features tested locally
  - ✅ Backend deployed to DigitalOcean GPU
  - ✅ Supabase auth configured
  - ✅ Custom domains ready

**What we'll do in Phase 9 instead:**
1. Create `vercel.json` config
2. Configure production environment variables
3. Set up custom domain `diveteacher.io`
4. Deploy to Vercel with backend integration
5. Test end-to-end in production

**For now (Phase 1.2):**
- ✅ Use `npm run dev` (local Vite server)
- ✅ Proxy to `http://localhost:8000`
- ✅ No production build needed

---

---

## Conversation Storage Strategy

### Decision: Supabase PostgreSQL (Not SQLite)

**Context:**
- ARIA used SQLite because it was a **local, single-user application**
- DiveTeacher is a **multi-user SaaS** requiring centralized storage

**Why Supabase over SQLite:**

| Factor | SQLite (ARIA) | Supabase (DiveTeacher) |
|--------|---------------|------------------------|
| **Users** | Single local user | Multi-user SaaS |
| **Location** | Local filesystem | Cloud PostgreSQL |
| **Auth** | None | Integrated (auth.users) |
| **Security** | Not needed | RLS (Row-Level Security) |
| **Sync** | Not needed | Automatic across devices |
| **Cost** | Free | Free < 50k users |
| **Scalability** | ❌ Limited | ✅ Production-ready |

**Architecture:**

```sql
-- Supabase Schema (Phase 1.3+)

-- Auth is built-in (Supabase provides auth.users)

-- Application tables
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  context_facts JSONB,  -- Retrieved facts from RAG
  metadata JSONB,       -- Stats (tokens, duration, etc.)
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies (each user sees only their data)
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can CRUD own sessions" ON chat_sessions
  FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can CRUD own messages" ON chat_messages
  FOR ALL USING (
    session_id IN (
      SELECT id FROM chat_sessions WHERE user_id = auth.uid()
    )
  );
```

**Implementation Timeline:**

**Phase 1.2 (Current - Local MVP):**
```javascript
// Frontend: In-memory storage only
const [messages, setMessages] = useState([]);

// Messages lost on page refresh → OK for MVP testing
```

**Phase 1.3 (Supabase Integration):**
```javascript
// Frontend: Save to Supabase after each message
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

// Save user message
const { data, error } = await supabase
  .from('chat_messages')
  .insert({
    session_id: currentSessionId,
    role: 'user',
    content: message,
  });

// Load conversation history
const { data: history } = await supabase
  .from('chat_messages')
  .select('*')
  .eq('session_id', sessionId)
  .order('timestamp', { ascending: true });
```

**Why NOT SQLite for DiveTeacher:**
- ❌ No multi-user support
- ❌ Requires backend persistence layer
- ❌ No RLS (security issue)
- ❌ Complex sync between frontend/backend
- ❌ Not suitable for SaaS

**Benefits of Supabase:**
- ✅ Multi-user from day 1
- ✅ RLS = automatic data isolation
- ✅ Realtime subscriptions (future)
- ✅ No backend persistence code needed
- ✅ MCP tools available for setup
- ✅ Free tier generous (500MB DB, 50k users)

---

## Technical Specifications

### API Client (src/lib/api.js)

**Complete API client for all backend endpoints:**

```javascript
/**
 * DiveTeacher API Client
 * Handles all communication with FastAPI backend
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Upload a document
 */
export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }
  
  return response.json(); // { upload_id, filename }
}

/**
 * Get upload status (for polling)
 */
export async function getUploadStatus(uploadId) {
  const response = await fetch(`${API_BASE}/api/upload/${uploadId}/status`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch status');
  }
  
  return response.json();
}

/**
 * Stream a RAG query (SSE)
 * Returns an async generator for tokens
 */
export async function* streamQuery(question, options = {}) {
  const response = await fetch(`${API_BASE}/api/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      temperature: options.temperature || 0.7,
      max_tokens: options.max_tokens || 2000
    })
  });
  
  if (!response.ok) {
    throw new Error('Query failed');
  }
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep incomplete line
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        yield data; // Yield each SSE event
      }
    }
  }
}

/**
 * Check backend health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/query/health`);
  return response.json();
}
```

---

### Component Specifications

#### 1. StageProgress.jsx

**4-Stage Visual Progress Indicator:**

```jsx
/**
 * StageProgress.jsx
 * 
 * Displays 4-stage pipeline progress:
 * 1. Validation (0-25%)
 * 2. Conversion (25-50%)
 * 3. Chunking (50-75%)
 * 4. Ingestion (75-100%)
 */

const STAGES = [
  { key: 'validation', label: 'Validation', icon: CheckCircle },
  { key: 'conversion', label: 'Conversion', icon: FileText },
  { key: 'chunking', label: 'Chunking', icon: Scissors },
  { key: 'ingestion', label: 'Ingestion', icon: Database }
];

function StageProgress({ currentStage, progress, status }) {
  const currentIndex = STAGES.findIndex(s => s.key === currentStage);
  
  return (
    <div className="dive-stage-progress">
      {STAGES.map((stage, index) => {
        const isActive = index === currentIndex;
        const isComplete = index < currentIndex || status === 'completed';
        const isFailed = status === 'failed' && index === currentIndex;
        
        return (
          <div key={stage.key} className={`stage ${
            isActive ? 'active' :
            isComplete ? 'complete' :
            isFailed ? 'failed' : 'pending'
          }`}>
            <div className="stage-icon">
              <stage.icon size={20} />
            </div>
            <div className="stage-label">{stage.label}</div>
            {isActive && (
              <div className="stage-progress">
                {Math.round(progress)}%
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
```

**CSS:**
```css
.dive-stage-progress {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
}

.stage {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.stage.active,
.stage.complete {
  opacity: 1;
}

.stage-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e2e8f0;
  color: #64748b;
  transition: all 0.3s ease;
}

.stage.active .stage-icon {
  background: var(--dive-primary);
  color: white;
  animation: pulse 2s infinite;
}

.stage.complete .stage-icon {
  background: var(--status-success);
  color: white;
}

.stage.failed .stage-icon {
  background: var(--status-error);
  color: white;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```

---

#### 2. MessageItem.jsx

**Individual Chat Message with Streaming Support:**

```jsx
/**
 * MessageItem.jsx
 * 
 * Displays a single chat message (user or assistant)
 * Supports:
 * - Markdown rendering (assistant)
 * - Streaming indicator
 * - Context facts display
 */

import ReactMarkdown from 'react-markdown';
import { User, Bot, Loader } from 'lucide-react';

function MessageItem({ message }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message-item ${isUser ? 'user' : 'assistant'}`}>
      {/* Avatar */}
      <div className="message-avatar">
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>
      
      {/* Content */}
      <div className="message-content">
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <>
            <ReactMarkdown>{message.content}</ReactMarkdown>
            {message.streaming && (
              <Loader className="inline-block ml-2 animate-spin" size={16} />
            )}
          </>
        )}
        
        {/* Context facts (if any) */}
        {!isUser && message.context && (
          <div className="message-context">
            <p className="text-sm text-gray-600 mb-2">
              📚 Retrieved {message.context.length} facts
            </p>
            {message.context.map((fact, idx) => (
              <div key={idx} className="dive-badge dive-badge-info mb-1">
                {fact}
              </div>
            ))}
          </div>
        )}
        
        {/* Stats (if done) */}
        {!isUser && message.stats && (
          <div className="message-stats">
            <span className="text-xs text-gray-500">
              {message.stats.token_count} tokens · {message.stats.tokens_per_second} tok/s
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
```

**CSS:**
```css
.message-item {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-item.user .message-avatar {
  background: var(--dive-primary);
  color: white;
}

.message-item.assistant .message-avatar {
  background: #e2e8f0;
  color: #64748b;
}

.message-content {
  flex: 1;
  background: white;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.message-item.user .message-content {
  background: var(--dive-primary);
  color: white;
}

.message-context {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.message-stats {
  margin-top: 0.5rem;
  opacity: 0.7;
}
```

---

### Mobile Responsive Breakpoints

**Tailwind Breakpoints:**
```javascript
// tailwind.config.js
export default {
  theme: {
    screens: {
      'sm': '640px',   // Mobile landscape
      'md': '768px',   // Tablet
      'lg': '1024px',  // Desktop
      'xl': '1280px'   // Large desktop
    }
  }
}
```

**Responsive Layout:**
```jsx
// App.jsx - Responsive grid
<main className="
  px-4 sm:px-6 lg:px-8 
  max-w-7xl mx-auto
  py-6 sm:py-8
">
  {activeTab === 'upload' && (
    <div className="
      grid 
      grid-cols-1 
      lg:grid-cols-2 
      gap-6
    ">
      <DocumentUpload />
      <DocumentList />
    </div>
  )}
</main>
```

---

## Testing Strategy

### Unit Tests (Optional for MVP)

**Not required for Phase 1.2, but good for future:**
```bash
npm install -D vitest @testing-library/react
```

### Manual Testing Checklist

**Pre-Deployment:**
- [ ] Upload 3 PDFs → All show 4 stages
- [ ] Upload invalid file → Error displays
- [ ] Query with empty graph → Shows message
- [ ] Query with context → Shows facts
- [ ] Stream 10+ messages → No memory leaks
- [ ] Resize browser → UI adapts
- [ ] Open on iPhone → Tabs work
- [ ] Refresh during upload → State lost (expected)
- [ ] Network offline → Error handling works

**Post-Deployment (Vercel):**
- [ ] Frontend loads from Vercel
- [ ] API calls reach backend (CORS OK)
- [ ] Upload works end-to-end
- [ ] Query streaming works
- [ ] HTTPS certificate valid
- [ ] Custom domain resolves

---

### Deployment Plan

**Phase 1.2: Local Development Only**

**1. Start Backend:**
```bash
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker-compose -f docker/docker-compose.dev.yml up -d
```

**2. Start Frontend:**
```bash
cd frontend
npm run dev
# Open http://localhost:5173
```

**3. Test End-to-End:**
- ✅ Upload Tab → Upload PDF → Monitor 4 stages
- ✅ Query Tab → Ask question → See streaming response
- ✅ All interactions stay in browser (in-memory)

**What We're NOT Doing (Yet):**
- ❌ Production build (`npm run build`)
- ❌ Vercel deployment
- ❌ Custom domain setup
- ❌ Supabase integration
- ❌ Conversation persistence

**Future Phases:**
- **Phase 1.3:** Add Supabase (auth + conversation persistence)
- **Phase 9:** Deploy to production (Vercel + DigitalOcean GPU)

---

## Success Criteria

### Phase 1.2 Complete When:

**Upload Tab:**
- ✅ Document dropzone accepts PDF/PPT/PPTX
- ✅ Upload triggers `/api/upload` successfully
- ✅ Status polling shows 4 stages (validation, conversion, chunking, ingestion)
- ✅ Progress bar updates in real-time (0-100%)
- ✅ Document list shows all uploads with current stage
- ✅ Completed uploads show ✅ badge
- ✅ Failed uploads show ❌ with retry button
- ✅ Error messages display correctly

**Query Tab:**
- ✅ Chat interface clean and functional
- ✅ Input accepts text and sends to `/api/query/stream`
- ✅ SSE streaming works (tokens appear incrementally)
- ✅ Messages display user/assistant correctly
- ✅ Markdown rendering works (bold, lists, code)
- ✅ Empty knowledge graph shows helpful message
- ✅ Context facts display when available
- ✅ Loading states show during streaming

**UI/UX:**
- ✅ Tab navigation works (Upload | Query)
- ✅ Active tab visually distinct
- ✅ DiveTeacher ocean theme applied everywhere
- ✅ Semantic CSS classes used (not inline Tailwind)
- ✅ Mobile responsive (works on 375px+)
- ✅ No console errors
- ✅ Smooth animations and transitions

**Production:**
- ✅ Runs locally with `npm run dev`
- ✅ Backend proxy working (`http://localhost:8000`)
- ✅ No console errors
- ✅ Mobile responsive (tested in browser DevTools)
- ⏸️ Production build - Deferred to Phase 9
- ⏸️ Vercel deployment - Deferred to Phase 9
- ⏸️ Custom domain - Deferred to Phase 9

**Not Required for Phase 1.2:**
- ❌ Conversation persistence (Phase 1.3 - Supabase)
- ❌ User authentication (Phase 1.3 - Supabase)
- ❌ Production deployment (Phase 9)
- ❌ HTTPS/SSL certificates (Phase 9)

---

## Risk Mitigation

### Risk 1: SSE Parsing Complexity

**Risk:** SSE format parsing is error-prone (buffering, incomplete lines)

**Mitigation:**
- Use ARIA's proven SSE parser pattern
- Buffer incomplete lines properly
- Add extensive error handling
- Test with long responses (>1000 tokens)
- Log SSE events for debugging

### Risk 2: Real-Time Status Polling

**Risk:** Polling every 1s may be inefficient or miss updates

**Mitigation:**
- Use 1s interval (acceptable for MVP)
- Stop polling when status is `completed` or `failed`
- Implement exponential backoff for errors
- Future: Replace with WebSocket for production

### Risk 3: Vercel CORS Issues

**Risk:** Frontend on Vercel may have CORS issues with backend

**Mitigation:**
- Backend already has CORS configured (`backend/app/main.py`)
- Add Vercel domain to allowed origins:
  ```python
  CORS_ORIGINS = "https://diveteacher.io,https://diveteacher-*.vercel.app"
  ```
- Test with Vercel preview URL before production

### Risk 4: Build Size Too Large

**Risk:** React + Tailwind + dependencies may produce large bundle

**Mitigation:**
- Use Vite code splitting (`manualChunks`)
- Lazy load query tab (only load when accessed)
- Disable sourcemaps in production
- Target: < 500KB gzipped (acceptable)

---

## Timeline Summary

| Phase | Task | Duration | Deliverables |
|-------|------|----------|--------------|
| **1.2.1** | Project Setup | 2h | Theme system, UI components |
| **1.2.2** | Upload Tab | 5h | Document upload + 4-stage monitoring |
| **1.2.3** | Query Tab | 5h | Chat interface + SSE streaming |
| **1.2.4** | Navigation | 2h | Tab system + layout |
| **1.2.5** | Styling | 2h | Ocean theme + semantic classes |
| **1.2.6** | Testing | 2-4h | End-to-end tests + bug fixes |
| ~~**1.2.7**~~ | ~~Vercel Deploy~~ | ~~Deferred~~ | ⏸️ Moved to Phase 9 |
| **Total** | | **18-20h** | Local dev UI fully functional |

**Calendar Estimate:**
- **Day 1:** 7 hours → Phases 1.2.1, 1.2.2
- **Day 2:** 7 hours → Phases 1.2.3, 1.2.4
- **Day 3:** 4-6 hours → Phases 1.2.5, 1.2.6

**⏸️ Deferred to Later:**
- Phase 1.3: Supabase conversation persistence
- Phase 9: Vercel production deployment

---

## Next Steps After Phase 1.2

**Phase 1.3: User Authentication (Supabase)**
- Login/Signup UI
- Protected routes
- User roles (admin, instructor, student)

**Phase 2.0: Multi-Conversation Management**
- Conversation history
- Save/load conversations
- Conversation sidebar

**Phase 3.0: Advanced Features**
- Knowledge graph visualization
- Document preview
- Bulk upload
- Export conversations

---

## References

**ARIA Frontend Guide:**
- Location: `resources/251028-FRONTEND-DEVELOPMENT-GUIDE-FOR-AI-AGENTS.md`
- Key patterns: Hybrid styling, SSE streaming, production deployment

**API Documentation:**
- Upload API: `docs/API.md` (POST /api/upload, GET /api/upload/{id}/status)
- Query API: `docs/API.md` (POST /api/query/stream, GET /api/query/health)

**Backend Code:**
- Upload endpoint: `backend/app/api/upload.py`
- Query endpoint: `backend/app/api/query.py`
- RAG logic: `backend/app/core/rag.py`

---

## Appendix: File Checklist

### New Files to Create (25)

**Config & Styles (3):**
- [ ] `src/config/brand.js`
- [ ] `src/styles/diveteacher-theme.css`
- [ ] `src/index.css` (UPDATE)

**Lib (2):**
- [ ] `src/lib/utils.js`
- [ ] `src/lib/api.js`

**UI Components (4):**
- [ ] `src/components/ui/Card.jsx`
- [ ] `src/components/ui/Button.jsx`
- [ ] `src/components/ui/Badge.jsx`
- [ ] `src/components/ui/ProgressBar.jsx`

**Layout Components (3):**
- [ ] `src/components/layout/Header.jsx`
- [ ] `src/components/layout/TabNavigation.jsx`
- [ ] `src/components/layout/Footer.jsx`

**Upload Components (4):**
- [ ] `src/components/upload/DocumentUpload.jsx`
- [ ] `src/components/upload/DocumentList.jsx`
- [ ] `src/components/upload/DocumentItem.jsx`
- [ ] `src/components/upload/StageProgress.jsx`

**Query Components (5):**
- [ ] `src/components/query/ChatInterface.jsx`
- [ ] `src/components/query/MessageList.jsx`
- [ ] `src/components/query/MessageItem.jsx`
- [ ] `src/components/query/InputBar.jsx`
- [ ] `src/components/query/ContextDisplay.jsx`

**Root (1):**
- [ ] `src/App.jsx` (MAJOR UPDATE)

**Deployment (3):**
- [ ] `vercel.json`
- [ ] `.env.example`
- [ ] `docs/VERCEL-DEPLOYMENT.md`

---

## Conclusion

This plan provides a **complete, production-ready admin UI** based on ARIA's proven patterns. The implementation follows best practices:
- ✅ Semantic CSS classes (not inline Tailwind)
- ✅ Real-time status monitoring (4-stage pipeline)
- ✅ SSE streaming correctly implemented
- ✅ Mobile-responsive and PWA-ready
- ✅ Vercel deployment configured

**Estimated Timeline:** 2-3 days (16-24 hours)  
**Priority:** 🔴 CRITICAL for end-to-end testing

---

**Document Status:** 📋 READY FOR REVIEW  
**Next Action:** Review plan → Approve → Start implementation Phase 1.2.1

