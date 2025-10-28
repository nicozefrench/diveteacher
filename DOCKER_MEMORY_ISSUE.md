# ⚠️ IMPORTANT: Docker Memory Configuration Required

## Issue Discovered During Step 3

While implementing **Phase 1.0 - Step 3: Pull Qwen Model**, we discovered a critical Docker memory configuration issue.

### Current Status

✅ **Completed Steps:**
- Step 1: Docker configuration updated ✅
- Step 2: .env configuration documented ✅
- Step 3: Models downloaded ✅ (but cannot run)
- Step 4: Query API created ✅
- Step 5: Settings updated ✅

⚠️ **Current Blocker:**
- Docker memory allocation insufficient for Qwen models

### Problem Details

**Docker Memory Status:**
```
Total Docker Memory: 7.654 GiB
Available to Ollama: 4.5 GiB
```

**Qwen Model Requirements:**
- **Q8_0 (8-bit):** Requires 9.3 GiB ❌
- **Q5_K_M (5-bit):** Requires 6.9 GiB ❌
- **Q4_K_M (4-bit):** Requires ~5 GiB (might work)

**Error Message:**
```
model requires more system memory (6.9 GiB) than is available (4.5 GiB)
```

### Models Successfully Downloaded

Both models are downloaded and ready:
```bash
NAME                          SIZE      STATUS
qwen2.5:7b-instruct-q8_0      8.1 GB    ✅ Downloaded
qwen2.5:7b-instruct-q5_K_M    5.4 GB    ✅ Downloaded
```

### Solutions (Choose One)

#### Option 1: Increase Docker Memory (Recommended)

**Steps:**
1. Open **Docker Desktop**
2. Go to **Settings** → **Resources** → **Memory**
3. Increase memory limit to **12-16 GB**
4. Click **Apply & Restart**
5. Test Qwen Q5_K_M again

**Why Q5_K_M is good enough:**
- Quality: 95/100 (vs 98/100 for Q8_0)
- RAM: 6.9 GB (fits in 12GB allocation)
- Speed: 35-45 tok/s on Mac M1 Max CPU
- Excellent for RAG tasks

**System Context:**
- Mac M1 Max has 32GB RAM total
- Allocating 12-16GB to Docker leaves 16-20GB for macOS
- This is a safe and sustainable allocation

#### Option 2: Use Q4_K_M (Faster but Lower Quality)

If you prefer not to increase Docker memory:

```bash
# Pull Q4_K_M (smaller, faster)
docker exec rag-ollama ollama pull qwen2.5:7b-instruct-q4_K_M

# Update docker-compose default model
OLLAMA_MODEL=qwen2.5:7b-instruct-q4_K_M
```

**Q4_K_M Characteristics:**
- Quality: 90/100 (lower than Q5/Q8)
- RAM: ~5 GB (fits in current 7.6GB Docker allocation)
- Speed: 40-50 tok/s (faster than Q5/Q8)
- Still decent for RAG, but less precise

#### Option 3: Keep Q8_0 for Later GPU Deployment

If you plan to deploy to GPU soon (DigitalOcean/Modal):
- Keep Q8_0 downloaded
- Use it when you have GPU with 20GB VRAM
- For now, increase Docker memory and use Q5_K_M for development

### Recommendation

**For Mac M1 Max Development:**
1. Increase Docker memory to **12 GB**
2. Use **Q5_K_M** (best balance of quality/performance for CPU)
3. Keep Q8_0 for future GPU deployment

**Trade-offs:**
- Q5_K_M: 95% quality, good RAG performance
- Q4_K_M: 90% quality, faster but less accurate
- Q8_0: 98% quality, best for GPU production

### Next Steps

**After increasing Docker memory:**

```bash
# Test Q5_K_M
docker exec rag-ollama ollama run qwen2.5:7b-instruct-q5_K_M "What is 2+2?"

# If successful, update default model in docker-compose
# Already done: OLLAMA_MODEL=qwen2.5:7b-instruct-q8_0
# Change to: OLLAMA_MODEL=qwen2.5:7b-instruct-q5_K_M
```

**Then continue with:**
- Step 6: Create test script
- Step 7: Monitor performance
- Step 8: Update documentation

---

**Created:** October 28, 2025  
**Status:** ⚠️ AWAITING USER ACTION (Docker memory increase)  
**Next:** User increases Docker memory, then we continue testing

