# 🧪 Phase 1.2 - Frontend Testing Guide

**Status:** ✅ READY FOR TESTING  
**Created:** October 28, 2025

---

## ✅ What Has Been Implemented

### Phase 1.2.1: Project Setup ✅
- ✅ Created folder structure (`config/`, `lib/`, `components/ui/`, `components/upload/`, `components/query/`, `components/layout/`)
- ✅ Configured DiveTeacher ocean theme (`diveteacher-theme.css`)
- ✅ Created reusable UI components (Card, Button, Badge, ProgressBar, Spinner)
- ✅ Set up utility functions (`utils.js`, `api.js`)
- ✅ Updated Tailwind config with DiveTeacher colors

### Phase 1.2.2: Document Upload Tab ✅
- ✅ `DocumentUpload.jsx` - Drag-and-drop with react-dropzone
- ✅ `DocumentList.jsx` - Lists all uploaded documents
- ✅ `DocumentItem.jsx` - Per-document card with status
- ✅ `StageProgress.jsx` - 4-stage progress indicator (Validation, Conversion, Chunking, Ingestion)
- ✅ `UploadTab.jsx` - Main container with real-time polling (1s interval)

### Phase 1.2.3: RAG Query Tab ✅
- ✅ `MessageItem.jsx` - User/assistant messages with markdown
- ✅ `MessageList.jsx` - Scrollable message history with auto-scroll
- ✅ `InputBar.jsx` - Query input (Enter to send, Shift+Enter for newline)
- ✅ `ContextDisplay.jsx` - Shows retrieved facts from knowledge graph
- ✅ `ChatInterface.jsx` - Main chat UI with SSE streaming integration

### Phase 1.2.4: Navigation & Layout ✅
- ✅ `Header.jsx` - DiveTeacher branding with ocean theme
- ✅ `TabNavigation.jsx` - Upload | Query tabs
- ✅ `Footer.jsx` - System status with health check
- ✅ `App.jsx` - Main application with tab state management

### Phase 1.2.5: Styling & Theme System ✅
- ✅ CSS variables for ocean theme (deep blue, aqua, cyan)
- ✅ Semantic component classes (`.dive-card`, `.dive-button`, etc.)
- ✅ Tailwind config with custom colors
- ✅ Mobile-responsive breakpoints

---

## 🚀 How to Test

### Prerequisites

1. **Backend must be running:**
```bash
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker-compose -f docker/docker-compose.dev.yml up -d
```

2. **Frontend dev server is running:**
```bash
cd frontend
npm run dev
# Opens at http://localhost:5173
```

### Test Scenarios

#### ✅ Test 1: Upload Tab - Document Upload

1. Open http://localhost:5173
2. Verify you're on the "Document Upload" tab
3. Drag a PDF file onto the dropzone (or click to select)
4. Expected:
   - ✅ File uploads to `/api/upload`
   - ✅ Document appears in the list on the right
   - ✅ 4-stage progress bar updates in real-time (Validation → Conversion → Chunking → Ingestion)
   - ✅ Progress percentage shows (0% → 100%)
   - ✅ Status badge changes (Processing → Completed)
   - ✅ Metadata shows (chunks, entities, relations)

**Known Behaviors:**
- Polling happens every 1 second while `status === 'processing'`
- Polling stops when `status === 'completed'` or `status === 'failed'`
- Multiple uploads are tracked independently

#### ✅ Test 2: Upload Tab - Error Handling

1. Try uploading an invalid file (e.g., `.txt`, `.jpg`)
2. Expected:
   - ✅ Error message: "Invalid file type. Only PDF, PPT, and PPTX are supported."

3. Try uploading a file > 50MB
4. Expected:
   - ✅ Error message: "File is too large. Maximum size is 50MB."

#### ✅ Test 3: Query Tab - Basic Chat

1. Click "RAG Query" tab
2. Type a question in the input box (e.g., "What is the maximum depth for recreational diving?")
3. Press Enter
4. Expected:
   - ✅ User message appears immediately
   - ✅ Assistant message appears with streaming indicator (spinning loader)
   - ✅ Tokens stream in real-time (visible typing effect)
   - ✅ When complete: streaming stops, stats show (tokens, tok/s, duration)
   - ✅ Markdown rendering works (bold, lists, code blocks)

**Known Behaviors:**
- SSE streaming from `/api/query/stream`
- Auto-scroll to bottom as messages arrive
- Input disabled while streaming

#### ✅ Test 4: Query Tab - Context Display

1. Ask a question that retrieves facts from the knowledge graph
2. Expected:
   - ✅ Context facts display above the message list (if available)
   - ✅ Facts shown in blue badges
   - ✅ Message includes context in metadata

**Note:** If knowledge graph is empty, assistant may say "I don't have enough information"

#### ✅ Test 5: Navigation & Tabs

1. Switch between "Document Upload" and "RAG Query" tabs
2. Expected:
   - ✅ Active tab is visually distinct (blue underline)
   - ✅ Tab content switches instantly
   - ✅ State persists (uploaded documents don't disappear, messages stay)

#### ✅ Test 6: Mobile Responsive

1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test on:
   - iPhone SE (375px)
   - iPad (768px)
   - Desktop (1280px)

Expected:
- ✅ Layout adapts to screen size
- ✅ Upload/List stacks vertically on mobile
- ✅ Tabs work on mobile
- ✅ Chat input resizes properly

#### ✅ Test 7: System Health Check

1. Check the footer (bottom of page)
2. Expected:
   - ✅ Shows "System Operational" (green) if backend healthy
   - ✅ Shows "System Unavailable" (red) if backend down
   - ✅ Updates every 30 seconds

---

## 🐛 Known Issues / Limitations (Expected)

### In-Memory Storage (Phase 1.2)
- ❌ **Messages and uploads NOT persisted**
  - Page refresh = all data lost
  - This is by design for Phase 1.2
  - ✅ Fixed in Phase 1.3 (Supabase integration)

### No Authentication (Phase 1.2)
- ❌ **No login/signup**
  - Anyone can access the UI
  - This is by design for Phase 1.2
  - ✅ Fixed in Phase 1.3 (Supabase Auth)

### SSE Edge Cases
- ⚠️ **Network interruption may cause incomplete responses**
  - Error handling implemented but not perfect
  - User should retry if stream fails

---

## 🔧 Troubleshooting

### Issue: Upload not working

**Check:**
1. Backend running? `docker ps | grep backend`
2. API proxy working? Check browser DevTools Network tab
3. CORS errors? Check browser console

**Solution:**
```bash
# Restart backend
docker-compose -f docker/docker-compose.dev.yml restart backend

# Check backend logs
docker logs rag-backend-1 --tail 50
```

### Issue: Query streaming not working

**Check:**
1. Ollama running? `docker ps | grep ollama`
2. Backend `/api/query/health` returns 200?
   ```bash
   curl http://localhost:8000/api/query/health
   ```

**Solution:**
```bash
# Check Ollama logs
docker logs rag-ollama --tail 50

# Restart Ollama
docker-compose -f docker/docker-compose.dev.yml restart ollama
```

### Issue: Frontend not loading

**Check:**
1. Vite dev server running on port 5173?
2. Check terminal for errors

**Solution:**
```bash
cd frontend
npm install  # Reinstall dependencies
npm run dev  # Restart dev server
```

---

## ✅ Success Criteria (Phase 1.2)

### Upload Tab:
- ✅ Document dropzone accepts PDF/PPT/PPTX
- ✅ Upload triggers `/api/upload` successfully
- ✅ Status polling shows 4 stages in real-time
- ✅ Progress bar updates (0-100%)
- ✅ Document list shows all uploads
- ✅ Completed uploads show ✅ badge
- ✅ Failed uploads show ❌ with retry button
- ✅ Error messages display correctly

### Query Tab:
- ✅ Chat interface clean and functional
- ✅ Input accepts text and sends to `/api/query/stream`
- ✅ SSE streaming works (tokens appear incrementally)
- ✅ Messages display user/assistant correctly
- ✅ Markdown rendering works
- ✅ Empty knowledge graph shows helpful message
- ✅ Context facts display when available
- ✅ Loading states show during streaming

### UI/UX:
- ✅ Tab navigation works (Upload | Query)
- ✅ Active tab visually distinct
- ✅ DiveTeacher ocean theme applied everywhere
- ✅ Semantic CSS classes used
- ✅ Mobile responsive (works on 375px+)
- ✅ No console errors
- ✅ Smooth animations and transitions

---

## 📊 Test Results

| Test | Status | Notes |
|------|--------|-------|
| Upload Tab - Basic Upload | ⏳ Pending | User to test |
| Upload Tab - Error Handling | ⏳ Pending | User to test |
| Query Tab - Basic Chat | ⏳ Pending | User to test |
| Query Tab - Context Display | ⏳ Pending | User to test |
| Navigation & Tabs | ⏳ Pending | User to test |
| Mobile Responsive | ⏳ Pending | User to test |
| System Health Check | ⏳ Pending | User to test |

---

## 🎯 Next Steps After Testing

**If all tests pass:**
1. ✅ Mark Phase 1.2 as COMPLETE
2. ✅ Update CURRENT-CONTEXT.md
3. ✅ Commit to Git
4. ✅ Move to Phase 1.3: Supabase Auth + Conversation Persistence

**If bugs found:**
1. Report bug details (which test, expected vs actual)
2. Agent will fix bugs
3. Retest
4. Repeat until all tests pass

---

## 📝 Notes for User

- **Local dev only:** No production deployment in Phase 1.2
- **In-memory storage:** Data lost on refresh (expected)
- **Backend required:** Make sure Docker containers are running
- **Browser:** Chrome/Firefox recommended for testing
- **DevTools:** Keep browser console open to catch any errors

---

**Ready to test? Open http://localhost:5173 and follow the test scenarios above!** 🚀

