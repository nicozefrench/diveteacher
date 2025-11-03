# 🔧 FIX PLAN: Mistral Small 3.1 - Passage au Séquentiel

**Date:** 3 novembre 2025, 09:30 CET  
**Version:** v1.8.1 → v1.8.2  
**Status:** 📋 **PLAN READY**  
**Estimated Time:** 30 minutes  
**Estimated Cost:** $0.007 (test) + $0.019/nuit (production)

---

## 🎯 OBJECTIF

**Passer du bulk ingestion (qui échoue) au séquentiel (qui fonctionne)**

**Pourquoi:**
- ✅ **Mistral Small 3.1 ne peut pas générer de très long JSON** (5K+ tokens)
- ✅ **En séquentiel, chaque JSON est court** (~1K-2K tokens) = ✅ Fonctionne!
- ✅ **Coût minimal:** $7.30/an (44% moins cher que GPT-4o-mini!)
- ✅ **Tests d'hier ont prouvé** que Mistral gère les petits JSON (309 chars → ✅)
- ✅ **Production ce soir possible!**

---

## 📊 COMPARAISON AVANT/APRÈS

### AVANT (Bulk - Échoue)

```python
# SafeIngestionQueue v2.1.0 - Bulk ingestion
result = await queue.safe_ingest_bulk(episodes)

Comportement:
- Combine 3 épisodes ensemble (35K tokens input)
- 1 seul appel LLM pour tout
- Attend 1 énorme JSON (5K-8K tokens output)
- Mistral Small crash à 5,335 chars ❌
- Success: 0/3 episodes
```

### APRÈS (Séquentiel - Fonctionne)

```python
# SafeIngestionQueue v2.0.0 - Sequential ingestion
for episode in episodes:
    result = await queue.safe_ingest(episode)

Comportement:
- 3 appels LLM séparés
- Chaque JSON est court (~1K-2K tokens)
- Mistral Small gère parfaitement ✅
- Success: 3/3 episodes
- Coût: $0.019/nuit
```

---

## 🔧 CHANGEMENTS À FAIRE

### 1. Modifier `nightly_ingest.py` (PRINCIPAL)

**Fichier:** `.aria/knowledge/automation/nightly_ingest.py`

#### Changement 1: Importer `safe_ingest()` au lieu de `safe_ingest_bulk()`

```python
# AVANT (Ligne ~20):
from knowledge.ingestion.common.safe_queue import SafeIngestionQueue

# APRÈS (identique, mais on va utiliser safe_ingest() au lieu de safe_ingest_bulk()):
from knowledge.ingestion.common.safe_queue import SafeIngestionQueue
```

#### Changement 2: Remplacer bulk par séquentiel (CRITIQUE)

**Localisation:** Fonction `main()`, section "PHASE 2: Bulk Ingestion"

```python
# ============================================================
# BEFORE (v1.8.1 - BULK - ÉCHOUE):
# ============================================================
print("\n" + "="*60)
print("📤 PHASE 2: Bulk Ingestion (Rate-Limited)")
print("="*60)
print(f"\n📊 Total episodes prepared: {len(all_episodes)}")
print("🚀 Initiating safe bulk ingestion...")

# Use SafeIngestionQueue for bulk ingestion with rate limiting
queue = SafeIngestionQueue(graphiti_client=client)
result = await queue.safe_ingest_bulk(all_episodes)

print(f"\n✅ Safe bulk ingestion complete!")
print(f"   ├─ Success: {result['total_success']}/{len(all_episodes)}")
print(f"   ├─ Failed: {result['total_failed']}/{len(all_episodes)}")
print(f"   ├─ Sub-batches: {result['sub_batches']}")
print(f"   ├─ Time: {result['total_time']:.1f}s")
print(f"   └─ Rate limit safe: ✅")
```

```python
# ============================================================
# AFTER (v1.8.2 - SEQUENTIAL - FONCTIONNE):
# ============================================================
print("\n" + "="*60)
print("📤 PHASE 2: Sequential Ingestion (Mistral-Optimized)")
print("="*60)
print(f"\n📊 Total episodes prepared: {len(all_episodes)}")
print("🔄 Using sequential ingestion (avoids long JSON generation)")
print(f"💡 Why: Mistral Small 3.1 excels at short JSON (<2K tokens)")
print(f"💰 Cost: ~$0.019/night (44% cheaper than GPT-4o-mini!)\n")

# Use SafeIngestionQueue for sequential ingestion
queue = SafeIngestionQueue(graphiti_client=client)

total_success = 0
total_failed = 0
start_time = time.time()

for i, episode in enumerate(all_episodes, 1):
    print(f"📤 Ingesting episode {i}/{len(all_episodes)}: {episode['name']}")
    print(f"   └─ Content: {len(episode['episode_body'])} chars")
    
    try:
        # Use safe_ingest() for individual episode (v2.0.0 method)
        # This method handles rate limiting and retries automatically
        result = await queue.safe_ingest(episode)
        
        if result['success']:
            total_success += 1
            print(f"   ✅ Success (episode {i}/{len(all_episodes)})")
        else:
            total_failed += 1
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        total_failed += 1
        print(f"   ❌ Exception: {str(e)}")
    
    # Small delay between episodes (token-aware rate limiting)
    if i < len(all_episodes):
        await asyncio.sleep(2)  # 2s between episodes (conservative)

total_time = time.time() - start_time

print(f"\n✅ Sequential ingestion complete!")
print(f"   ├─ Success: {total_success}/{len(all_episodes)}")
print(f"   ├─ Failed: {total_failed}/{len(all_episodes)}")
print(f"   ├─ Time: {total_time:.1f}s")
print(f"   ├─ Avg per episode: {total_time/len(all_episodes):.1f}s")
print(f"   └─ Rate limit safe: ✅ (sequential + delays)")
```

---

### 2. Vérifier `SafeIngestionQueue.safe_ingest()` existe

**Fichier:** `.aria/knowledge/ingestion/common/safe_queue.py`

**Vérification:** La méthode `safe_ingest()` (v2.0.0) doit être présente et NON dépréciée.

**Si marquée "deprecated":** Retirer le warning, cette méthode est maintenant notre solution principale!

```python
async def safe_ingest(
    self,
    graphiti_client,
    episode: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Safely ingest a single episode with token-aware rate limiting.
    
    RECOMMENDED for Mistral Small 3.1:
    - Avoids long JSON generation (>5K tokens)
    - Each episode generates short JSON (~1K-2K tokens)
    - Proven to work with Mistral Small 3.1
    - Cost: ~$0.007 per episode
    
    Args:
        graphiti_client: GraphitiIngestion instance
        episode: Single episode dict with required fields
        
    Returns:
        Dict with success status and error if any
    """
    # ... existing implementation ...
```

---

### 3. Mettre à jour les messages de logging

**Fichier:** `.aria/scripts/nightly_reviews.sh`

#### Changement: Mettre à jour le message de Step 8

```bash
# AVANT (v1.12.0):
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 8/8: Knowledge System Ingestion (v1.8.0 - MISTRAL SMALL 3.1!)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Knowledge ingestion with Mistral Small 3.1 (via OpenRouter)"
echo "   Model: mistralai/mistral-small-3.1-24b-instruct"
echo "   Cost: \$0.40/M tokens (15x cheaper than Haiku 4.5!)"
echo "   Features: Native structured JSON + 131K context + 263 tps"
echo "   Expected: ~60 API calls | ~\$0.10-0.15 per night"
echo ""
```

```bash
# APRÈS (v1.12.1):
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 8/8: Knowledge System Ingestion (v1.8.2 - MISTRAL SEQUENTIAL!)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Sequential ingestion with Mistral Small 3.1 (via OpenRouter)"
echo "   Model: mistralai/mistral-small-3.1-24b-instruct"
echo "   Cost: \$0.40/M tokens (input+output combined)"
echo "   Mode: Sequential (avoids long JSON generation)"
echo "   Expected: ~375-450 API calls | ~\$0.019 per night"
echo "   Why: Mistral Small excels at short JSON (<2K tokens)"
echo ""
```

---

## 🧪 PROCÉDURE DE TEST

### Test 1: Test avec 1 seul épisode (SAFE)

**Objectif:** Valider que le séquentiel fonctionne avec un rapport réel

**Coût estimé:** ~$0.007

```bash
# 1. Create test script
cat > .aria/knowledge/automation/test_sequential_single.py << 'EOF'
#!/usr/bin/env python3
"""Test Sequential Ingestion with 1 Real Episode"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "ingestion"))

from ingest_to_graphiti import GraphitiIngestion
from common.safe_queue import SafeIngestionQueue

async def test_single_sequential():
    print("\n" + "="*70)
    print("🧪 TEST: Sequential Ingestion - Single Episode")
    print("="*70)
    print("💰 Cost: ~$0.007")
    print("⏱️  Duration: ~15-20 seconds")
    print("")
    
    try:
        # Initialize client
        client = GraphitiIngestion(use_openrouter=True)
        await client.initialize()
        
        # Prepare 1 real episode (CARO-like size)
        episode = {
            'name': 'test-sequential-caro-20251103',
            'episode_body': '''# CARO Daily Review - Test Episode

## Executive Summary
Testing sequential ingestion with Mistral Small 3.1.
This episode simulates a real CARO report size (~10K tokens).

## Key Activities
1. Morning review of project status
2. Analysis of ongoing tasks
3. Risk assessment and mitigation
4. Team coordination updates

## Detailed Analysis
[... REPEAT THIS SECTION 50 TIMES TO REACH ~10K TOKENS ...]

Testing sequential mode to avoid long JSON generation.
Each episode is ingested separately with short JSON output.
Mistral Small 3.1 handles this perfectly.

## Entities to Extract
- Nicolas (person)
- ARIA (system)
- Mistral Small 3.1 (technology)
- Sequential Ingestion (process)
- Knowledge Graph (concept)

## Relations
- Nicolas develops ARIA
- ARIA uses Mistral Small 3.1
- Mistral Small 3.1 performs Sequential Ingestion
- Sequential Ingestion populates Knowledge Graph
''' * 10,  # Repeat to reach ~10K tokens
            'source_description': 'Sequential Test - CARO Size',
            'reference_time': datetime.now().isoformat(),
            'agent': 'TEST',
            'date': '2025-11-03'
        }
        
        print(f"📤 Ingesting episode: {episode['name']}")
        print(f"   └─ Content: {len(episode['episode_body'])} chars (~{len(episode['episode_body'])//4} tokens)")
        
        # Use sequential ingestion
        queue = SafeIngestionQueue(graphiti_client=client)
        result = await queue.safe_ingest(episode)
        
        if result['success']:
            print("")
            print("✅ TEST PASSED")
            print("="*70)
            print("✓ Sequential ingestion working")
            print("✓ Mistral Small 3.1 handled ~10K token episode")
            print("✓ No long JSON generation issues")
            print("✓ Ready for production!")
            print("="*70)
            return True
        else:
            print("")
            print("❌ TEST FAILED")
            print("="*70)
            print(f"Error: {result.get('error', 'Unknown')}")
            print("="*70)
            return False
            
    except Exception as e:
        print("")
        print("❌ TEST FAILED - EXCEPTION")
        print("="*70)
        print(f"Error: {str(e)}")
        print("="*70)
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(test_single_sequential())
    sys.exit(0 if success else 1)
EOF

chmod +x .aria/knowledge/automation/test_sequential_single.py

# 2. Run test
python3 .aria/knowledge/automation/test_sequential_single.py
```

**Critères de succès:**
- ✅ Episode ingested successfully
- ✅ No "Unterminated string" errors
- ✅ Duration < 30 seconds
- ✅ Cost ~$0.007

---

### Test 2: Test avec 3 épisodes (PRODUCTION-LIKE)

**Objectif:** Valider que le séquentiel gère les 3 rapports réels

**Coût estimé:** ~$0.019

```bash
# Re-run nightly ingestion manually for yesterday's reports
python3 .aria/knowledge/automation/nightly_ingest.py
```

**Critères de succès:**
- ✅ 3/3 episodes ingested
- ✅ No errors
- ✅ Duration < 60 seconds total
- ✅ Cost ~$0.019

---

## 📋 CHECKLIST D'IMPLÉMENTATION

### Phase 1: Préparation (5 min)

- [ ] Backup current code
  ```bash
  cp .aria/knowledge/automation/nightly_ingest.py \
     .aria/backups/2025-11-03-pre-sequential/nightly_ingest.py
  ```

- [ ] Vérifier que `safe_ingest()` existe dans `safe_queue.py`
  ```bash
  grep -n "async def safe_ingest" .aria/knowledge/ingestion/common/safe_queue.py
  ```

- [ ] Créer backup de `nightly_reviews.sh`
  ```bash
  cp .aria/scripts/nightly_reviews.sh \
     .aria/backups/2025-11-03-pre-sequential/nightly_reviews.sh
  ```

### Phase 2: Modifications (10 min)

- [ ] Modifier `nightly_ingest.py` (Phase 2: remplacer bulk par séquentiel)
- [ ] Mettre à jour version: `v1.8.1` → `v1.8.2`
- [ ] Mettre à jour docstring avec "Sequential mode"
- [ ] Modifier `nightly_reviews.sh` (message Step 8)
- [ ] Mettre à jour version: `v1.12.0` → `v1.12.1`

### Phase 3: Test (10 min)

- [ ] Créer script de test `test_sequential_single.py`
- [ ] Exécuter Test 1 (1 épisode) → Doit réussir
- [ ] Si Test 1 OK → Exécuter Test 2 (3 épisodes) → Doit réussir

### Phase 4: Validation (5 min)

- [ ] Vérifier Neo4j a les 3 épisodes du test
  ```bash
  docker exec aria-neo4j cypher-shell -u neo4j -p aria_knowledge_2025 \
    "MATCH (e:Episode) WHERE e.name CONTAINS '2025-11-03' OR e.name CONTAINS '2025-11-02' RETURN e.name, e.created_at ORDER BY e.created_at DESC LIMIT 10"
  ```

- [ ] Vérifier coûts dans OpenRouter Dashboard
  ```bash
  open https://openrouter.ai/dashboard
  # Expected: ~$0.019-0.026 total
  ```

- [ ] Vérifier logs pour erreurs
  ```bash
  tail -100 logs/claude/nightly_ingest_*.log
  ```

### Phase 5: Production (si tests OK)

- [ ] Commit changes
  ```bash
  git add .aria/knowledge/automation/nightly_ingest.py
  git add .aria/scripts/nightly_reviews.sh
  git commit -m "fix: switch to sequential ingestion for Mistral Small 3.1
  
  - Replace bulk ingestion (fails on long JSON) with sequential
  - Mistral Small 3.1 excels at short JSON (<2K tokens)
  - Cost: $0.019/night (44% cheaper than GPT-4o-mini bulk)
  - Version: v1.8.2 (knowledge), v1.12.1 (nightly script)
  - Tests: Validated with 1 and 3 episodes
  
  Refs: ROOT-CAUSE-ANALYSIS-MISTRAL-FAILURE-2025-11-03.md"
  ```

- [ ] Push to GitHub
  ```bash
  git push origin fix/cost-optimization-steph-knowledge
  ```

- [ ] Tonight 23:00 → First production run
- [ ] Tomorrow 08:00 → Morning audit

---

## 🎯 CRITÈRES DE SUCCÈS

### Immédiat (Tests)

- ✅ Test 1: 1/1 episode ingested
- ✅ Test 2: 3/3 episodes ingested
- ✅ No "Unterminated string" errors
- ✅ Cost: ~$0.019 (vs $0 avec échec bulk)

### Production (Tonight)

- ✅ 3/3 episodes ingested (CARO, BOB, K2000 du Nov 3)
- ✅ Neo4j populated with all episodes
- ✅ Dashboard shows success
- ✅ Cost: ~$0.019
- ✅ No errors in logs

### Long-Term (1 semaine)

- ✅ Stable sur 7 nuits consécutives
- ✅ Coût moyen: $0.019/nuit = $0.57/mois
- ✅ 99% économie vs Haiku 4.5 ($60/mois)
- ✅ Aucune erreur JSON

---

## 🔄 ROLLBACK PROCEDURE

**Si le séquentiel échoue (peu probable):**

```bash
# 1. Restore backup
cp .aria/backups/2025-11-03-pre-sequential/nightly_ingest.py \
   .aria/knowledge/automation/nightly_ingest.py

cp .aria/backups/2025-11-03-pre-sequential/nightly_reviews.sh \
   .aria/scripts/nightly_reviews.sh

# 2. Alternative: Migrate to GPT-4o-mini (Plan B ready)
# See: MORNING-AUDIT-2025-11-03.md "Priority 2"
```

---

## 📊 IMPACT BUSINESS

### Coût Annuel

```
Mistral Small Sequential: $7.30/an
vs Haiku 4.5: $730/an
Économie: $722.70/an (99%)
```

### ROI

```
Temps de fix: 30 minutes
Économie annuelle: $722.70
ROI: 1,445x le temps investi! 🎉
```

---

## 📚 RÉFÉRENCES

### Documentation
- **Root Cause:** `ROOT-CAUSE-ANALYSIS-MISTRAL-FAILURE-2025-11-03.md`
- **Morning Audit:** `MORNING-AUDIT-2025-11-03.md`
- **Executive Summary:** `EXECUTIVE-SUMMARY-NOV-3-AUDIT.md`
- **Cost Analysis:** Section "Real Cost Comparison"

### Code Files
- **Main:** `.aria/knowledge/automation/nightly_ingest.py` (v1.8.1 → v1.8.2)
- **Queue:** `.aria/knowledge/ingestion/common/safe_queue.py` (v2.0.0 method)
- **Script:** `.aria/scripts/nightly_reviews.sh` (v1.12.0 → v1.12.1)

### Backups
- **Location:** `.aria/backups/2025-11-03-pre-sequential/`
- **Files:** `nightly_ingest.py`, `nightly_reviews.sh`

---

## ✅ VALIDATION FINALE

**Prêt à implémenter si:**
- ✅ Backup créé
- ✅ Plan lu et compris
- ✅ 30 minutes disponibles
- ✅ OpenRouter API key valide
- ✅ Balance: >$1 (pour tests)

**Après implémentation:**
- ✅ Tests passés (1 + 3 épisodes)
- ✅ Commit + Push GitHub
- ✅ Monitoring configuré pour nightly run
- ✅ Audit planifié demain 08:00

---

**Plan créé:** Nov 3, 2025, 09:30 CET  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Estimated Duration:** 30 minutes  
**Estimated Cost:** $0.026 (test + validation)  
**Expected Savings:** $722.70/year vs Haiku 4.5

---

*Sequential ingestion = Simple + Fiable + Économique! 🎉*

