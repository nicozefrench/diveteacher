# 🔧 Docling Warm-up Fix - Plan de Test & Monitoring

**Date**: October 28, 2025, 19:25 CET  
**Problème**: Pipeline d'ingestion bloque après download Docling models  
**Root Cause**: Warm-up script ne matche pas la config réelle de DocumentConverter  
**Status**: 🔴 BLOQUANT - Aucun document ne peut être ingéré

---

## 📊 ANALYSE DÉTAILLÉE

### 🔍 Ce Qui Marche ✅

1. **Upload API** ✅
   - Endpoint `/api/upload` répond correctement
   - Fichier sauvé dans `/uploads/`
   - `upload_id` généré
   - Status 200 OK immédiat

2. **Background Task Creation** ✅
   ```
   [upload_id] Creating async background task...
   [upload_id] ✅ Processing task created (async)
   ```
   - `asyncio.create_task()` fonctionne
   - Wrapper démarre

3. **Wrapper Start** ✅
   ```
   [upload_id] 🚀 Starting background processing (async wrapper)...
   [upload_id] 🔍 DEBUG: About to call process_document()...
   ```
   - Wrapper atteint le `await process_document()`

4. **DOCLING_TIMEOUT** ✅
   - Valeur correcte: 900s (vérifié dans container)
   - `.env` mis à jour
   - Docker compose configuré

### ❌ Ce Qui Ne Marche PAS

1. **Docling Models Re-Download** ❌
   ```
   Fetching 9 files: 100%|██████████| 9/9 [00:14<00:00,  1.61s/it]
   ```
   - **PROBLÈME:** Models re-téléchargés à CHAQUE upload
   - **ATTENDU:** Models déjà en cache (warm-up)
   - **IMPACT:** Bloque `await process_document()` pendant 14s

2. **`process_document()` Never Starts** ❌
   - Après "About to call process_document()...", **SILENCE TOTAL**
   - **ATTENDU:** 
     ```
     [upload_id] ═══════════════════════════════════════
     [upload_id] Starting document processing
     [upload_id] Stage: initialization
     ```
   - **OBSERVÉ:** RIEN (0 logs de `process_document()`)

3. **Status Dict Never Initialized** ❌
   - Status endpoint retourne: `{"detail":"Not Found"}`
   - **CAUSE:** `processing_status[upload_id]` jamais créé
   - **SIGNIFICATION:** `process_document()` ligne 58 JAMAIS atteinte

---

## 🎯 ROOT CAUSE IDENTIFIÉE

### Le Warm-up Script NE FONCTIONNE PAS

**Fichier:** `backend/warmup_docling.py`

**Code actuel (ligne 39):**
```python
converter = DocumentConverter()  # ← Config VIDE!
```

**Problème:**
- Warm-up crée un `DocumentConverter()` SANS options
- `convert_document_to_docling()` crée un converter AVEC options spécifiques:
  - `do_ocr=True`
  - `do_table_structure=True`
  - `TableFormerMode.ACCURATE`
  - `PdfFormatOption(pipeline_options=...)`

**Résultat:**
- Warm-up télécharge modèles pour config "default"
- Processing nécessite modèles pour config "ACCURATE + OCR"
- → Re-téléchargement à chaque upload ❌

### Pourquoi `await process_document()` Bloque

**Hypothèse #1: Synchronous Blocking in Async Context**

Le téléchargement Docling (dans `_convert_sync()`) est **synchronous** et **CPU-bound**.

**Flow actuel:**
```
1. await process_document() appelé
2. → convert_document_to_docling() appelé
3. → await loop.run_in_executor(_docling_executor, _convert_sync, ...)
4. → _convert_sync() appelle DoclingSingleton.get_converter()
5. → DOWNLOAD happens HERE (synchronous, blocks thread)
6. [BLOQUE ICI - thread occupé, event loop attend]
```

**Problème:** Le download synchrone dans `get_converter()` bloque le thread de l'executor, ce qui empêche l'event loop de continuer.

**Evidence:**
- Warm-up logs: "Models are now cached and ready" ← FAUX (mauvaise config)
- Upload logs: "Fetching 9 files" ← Re-download
- Après download: SILENCE (event loop deadlock ou exception silencieuse)

---

## 📋 PLAN DE FIX

### Fix #1: Corriger le Warm-up Script ⭐⭐⭐

**Objectif:** Warm-up doit utiliser EXACTEMENT la même config que le processing

**Modifications:**

1. **`backend/warmup_docling.py`**
   ```python
   from docling.document_converter import DocumentConverter, PdfFormatOption
   from docling.datamodel.base_models import InputFormat
   from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
   
   def warmup_docling_models():
       logger.info("🔥 WARMING UP DOCLING MODELS")
       
       # ✅ SAME CONFIG as dockling.py
       pipeline_options = PdfPipelineOptions(
           do_ocr=True,                    # ✅ OCR enabled
           do_table_structure=True,        # ✅ Tables enabled
           artifacts_path=None,            # ✅ Auto-download
       )
       pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
       
       converter = DocumentConverter(
           format_options={
               InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
           }
       )
       
       logger.info("✅ DocumentConverter initialized - models cached!")
       return True
   ```

2. **Rebuild Backend**
   ```bash
   docker compose -f docker/docker-compose.dev.yml build backend --no-cache
   docker compose -f docker/docker-compose.dev.yml up -d backend
   ```

**Impact Attendu:**
- ✅ Models téléchargés pendant warm-up (10-15 min)
- ✅ Premier upload: PAS de re-download
- ✅ `await process_document()` continue normalement

---

### Fix #2: Ajouter Debug Prints dans `_convert_sync()` 🔍

**Objectif:** Comprendre où ça bloque EXACTEMENT

**Modifications:**

1. **`backend/app/integrations/dockling.py`** (ligne 139-153)
   ```python
   def _convert_sync(file_path: str) -> DoclingDocument:
       """Synchronous Docling conversion"""
       print(f"[_convert_sync] 🔄 START conversion: {Path(file_path).name}", flush=True)
       
       print(f"[_convert_sync] 📦 Getting converter singleton...", flush=True)
       converter = DoclingSingleton.get_converter()
       print(f"[_convert_sync] ✅ Converter obtained", flush=True)
       
       print(f"[_convert_sync] 🚀 Starting conversion...", flush=True)
       result = converter.convert(file_path)
       print(f"[_convert_sync] ✅ Conversion complete", flush=True)
       
       return result.document
   ```

**Impact Attendu:**
- Si warm-up fonctionne: Tous les prints apparaissent rapidement
- Si warm-up échoue: Block après "Getting converter singleton..."

---

### Fix #3: Ajouter Debug Prints dans `process_document()` 🔍

**Objectif:** Confirmer que `process_document()` est VRAIMENT appelé

**Modifications:**

1. **`backend/app/core/processor.py`** (ligne 54-67)
   ```python
   async def process_document(...):
       """Process uploaded document"""
       
       # CRITICAL DEBUG - AVANT status init
       print(f"[{upload_id}] 🎯 ENTERED process_document()", flush=True)
       print(f"[{upload_id}] 🎯 file_path={file_path}", flush=True)
       print(f"[{upload_id}] 🎯 Initializing status dict...", flush=True)
       
       # Initialize status dict
       processing_status[upload_id] = {
           "status": "processing",
           "stage": "initialization",
           "progress": 0,
           "error": None,
           "started_at": datetime.now().isoformat(),
       }
       
       print(f"[{upload_id}] ✅ Status dict initialized", flush=True)
       
       # ... rest of function
   ```

**Impact Attendu:**
- Si prints n'apparaissent PAS: `await process_document()` ne s'exécute jamais (event loop deadlock)
- Si prints apparaissent: Problem est ailleurs (dans conversion Docling)

---

## 🧪 PLAN DE TEST AVEC MONITORING

### Étape 1: Monitoring Setup

**Script:** `scripts/monitor_full_pipeline.sh`

```bash
#!/bin/bash
# Monitor complet du pipeline d'ingestion

UPLOAD_ID=$1

if [ -z "$UPLOAD_ID" ]; then
    echo "Usage: ./monitor_full_pipeline.sh <upload_id>"
    exit 1
fi

echo "🔍 MONITORING PIPELINE: $UPLOAD_ID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Follow logs avec filtres détaillés
docker logs -f rag-backend 2>&1 | grep --line-buffered -E "\[$UPLOAD_ID\]|_convert_sync|process_document|Fetching|✅|❌|DEBUG|ENTERED" | while read line; do
    # Colorize output
    if echo "$line" | grep -q "✅"; then
        echo -e "\033[0;32m${line}\033[0m"  # Green
    elif echo "$line" | grep -q "❌"; then
        echo -e "\033[0;31m${line}\033[0m"  # Red
    elif echo "$line" | grep -q "DEBUG\|ENTERED"; then
        echo -e "\033[1;33m${line}\033[0m"  # Yellow bold
    elif echo "$line" | grep -q "Fetching"; then
        echo -e "\033[0;36m${line}\033[0m"  # Cyan
    else
        echo "$line"
    fi
done
```

### Étape 2: Test Procedure

**Pre-test Checklist:**
- [ ] Backend rebuild avec warm-up fixé
- [ ] Container restart complet
- [ ] Warm-up logs vérifiés (models downloaded)
- [ ] Debug prints ajoutés

**Test Execution:**

1. **Clean start:**
   ```bash
   docker compose -f docker/docker-compose.dev.yml down -v
   docker compose -f docker/docker-compose.dev.yml build backend --no-cache
   docker compose -f docker/docker-compose.dev.yml up -d
   ```

2. **Watch warm-up:**
   ```bash
   docker logs -f rag-backend | grep -E "WARMING|models|Fetching"
   ```
   - **ATTENDU:** "Fetching 9 files" pendant warm-up
   - **ATTENDU:** "✅ DocumentConverter initialized"
   - **DURÉE:** 10-15 minutes

3. **Upload test document:**
   ```bash
   UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/upload \
     -F "file=@TestPDF/test.pdf")
   UPLOAD_ID=$(echo $UPLOAD_RESPONSE | jq -r '.upload_id')
   echo "Upload ID: $UPLOAD_ID"
   ```

4. **Start monitoring:**
   ```bash
   ./scripts/monitor_full_pipeline.sh "$UPLOAD_ID"
   ```

5. **Check status (every 30s):**
   ```bash
   watch -n 30 "curl -s http://localhost:8000/api/upload/$UPLOAD_ID/status | jq"
   ```

### Étape 3: Success Criteria

**✅ Warm-up Success:**
- [ ] "Fetching 9 files" apparaît SEULEMENT pendant warm-up
- [ ] "Models are now cached" après warm-up
- [ ] PAS de "Fetching" pendant upload

**✅ Processing Success:**
- [ ] `[upload_id] 🎯 ENTERED process_document()` apparaît
- [ ] `[upload_id] ✅ Status dict initialized` apparaît
- [ ] `[_convert_sync] 🔄 START conversion` apparaît
- [ ] `[_convert_sync] ✅ Converter obtained` apparaît RAPIDEMENT (< 1s)
- [ ] `[_convert_sync] ✅ Conversion complete` après 30-60s
- [ ] Status endpoint retourne `{"status": "processing", "stage": "conversion"}`

**✅ Final Success:**
- [ ] Status passe à `"completed"`
- [ ] Neo4j contient les episodes/entities
- [ ] Logs montrent ingestion Graphiti

---

## 📊 MONITORING METRICS

### Timeouts à Surveiller

| Phase | Timeout Actuel | Timeout Attendu | Metric |
|-------|----------------|-----------------|--------|
| Warm-up | N/A | 15 min (première fois) | Container startup time |
| Warm-up | N/A | 0s (cached) | Subsequent restarts |
| Upload API | 60s | < 1s | Response time |
| Wrapper start | N/A | < 0.1s | Task creation |
| Get converter | N/A | < 0.1s (cached) | Singleton access |
| Docling convert | 900s | 30-60s (test.pdf 2 pages) | Processing time |
| Status init | N/A | < 0.1s | Dict creation |

### Log Checkpoints

**Expected Log Sequence:**
```
1. [upload_id] Creating async background task...          ← Upload API
2. [upload_id] ✅ Processing task created (async)         ← Task created
3. [upload_id] 🚀 Starting background processing...       ← Wrapper starts
4. [upload_id] 🔍 DEBUG: About to call process_document() ← Before await
5. [upload_id] 🎯 ENTERED process_document()              ← Inside function
6. [upload_id] ✅ Status dict initialized                 ← Status created
7. [_convert_sync] 🔄 START conversion                    ← Docling starts
8. [_convert_sync] 📦 Getting converter singleton...      ← Get instance
9. [_convert_sync] ✅ Converter obtained                  ← Fast if cached!
10. [_convert_sync] 🚀 Starting conversion...             ← Convert starts
11. [_convert_sync] ✅ Conversion complete                ← Convert done
12. [upload_id] ✅ Conversion successful: test.pdf        ← Back to processor
13. [upload_id] Stage: chunking                           ← Next stage
14. ... (chunking + ingestion logs)
15. [upload_id] ✅ Processing complete                    ← Done!
```

**Current Failure Point:** Entre checkpoint 4 et 5 (ou 5 et 8)

---

## 🚨 FAILURE SCENARIOS

### Scenario A: Warm-up Ne Télécharge Rien
**Symptom:** "Fetching 9 files" pendant upload  
**Cause:** Warm-up script pas exécuté ou config incorrecte  
**Fix:** Vérifier `docker-entrypoint.sh` et rebuild

### Scenario B: `process_document()` Jamais Appelé
**Symptom:** Pas de "ENTERED process_document()"  
**Cause:** Event loop deadlock ou exception avant l'appel  
**Fix:** Investiguer exception dans wrapper

### Scenario C: `get_converter()` Bloque
**Symptom:** "Getting converter singleton..." mais pas "Converter obtained"  
**Cause:** Re-download dans singleton  
**Fix:** Vérifier warm-up config (doit matcher exactement)

### Scenario D: Conversion Bloque
**Symptom:** "Starting conversion..." mais pas "Conversion complete"  
**Cause:** Docling timeout ou crash  
**Fix:** Augmenter timeout ou vérifier fichier PDF

---

## 📁 FILES TO MODIFY

### Must Fix (Bloquant)
1. ✅ `backend/warmup_docling.py` - Fix config to match dockling.py
2. ✅ `backend/app/integrations/dockling.py` - Add debug prints in _convert_sync
3. ✅ `backend/app/core/processor.py` - Add debug prints at entry

### Nice to Have (Monitoring)
4. ⚪ `scripts/monitor_full_pipeline.sh` - New monitoring script
5. ⚪ `scripts/check_warmup_success.sh` - Verify warm-up worked

### Already Fixed
- ✅ `backend/app/core/config.py` - DOCLING_TIMEOUT=900
- ✅ `.env` - DOCLING_TIMEOUT=900
- ✅ `docker/docker-compose.dev.yml` - DOCLING_TIMEOUT=900 env var
- ✅ `backend/app/api/upload.py` - Debug prints in wrapper

---

## 🎯 NEXT ACTIONS

1. **Implémenter Fix #1** (warm-up config) ⭐⭐⭐ CRITIQUE
2. **Implémenter Fix #2** (debug _convert_sync) 🔍
3. **Implémenter Fix #3** (debug process_document) 🔍
4. **Rebuild backend** avec tous les fixes
5. **Test avec monitoring complet**
6. **Valider success criteria**
7. **Clean debug prints** une fois validé
8. **Update documentation** avec findings

---

**Status:** 📋 PLAN READY - Attente validation utilisateur avant implémentation

**Author:** AI Agent (Claude Sonnet 4.5)  
**Date:** October 28, 2025, 19:25 CET
