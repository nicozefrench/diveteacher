# 🔄 MIGRATION PLAN: Haiku 4.5 → OpenRouter DeepSeek R1 (FREE)

**Date:** Nov 2, 2025, 17:00 CET  
**Version:** Migration Plan v1.0  
**Status:** 📋 PLAN COMPLET - Ready for execution

---

## 🎯 OBJECTIF

**Migrer le Knowledge Graph ARIA de Claude Haiku 4.5 (coûteux) vers DeepSeek R1 (gratuit via OpenRouter)**

### Stratégie

| Système | Provider | Modèle | Coût | Statut |
|---------|----------|--------|------|--------|
| **Agents** (ARIA, CARO, BOB, etc.) | Anthropic Direct | Sonnet 4.5 | $3/$15/M tokens | ✅ **INCHANGÉ** |
| **Knowledge Graph** (Graphiti) | OpenRouter | DeepSeek R1 Free | **$0** | 🔄 **À MIGRER** |

**Raison:** Le Knowledge Graph avec Haiku 4.5 coûte trop cher (~$1-2/nuit minimum), même après optimisation. DeepSeek R1 via OpenRouter est **gratuit** et suffisant pour entity extraction.

---

## 📊 AUDIT COMPLET

### ✅ Clés API Disponibles

**Vérifié dans `.aria/.env` :**
```bash
OPENAI_API_KEY=sk-proj-...        # ✅ Présent (embeddings)
ANTHROPIC_API_KEY=sk-ant-api03-...# ✅ Présent (agents)
OPENROUTER_API_KEY=sk-or-v1-...   # ✅ Présent (nouveau!)
```

### 📁 Fichiers Identifiés pour Migration

**1. Code Principal (2 fichiers) :**
- `.aria/knowledge/ingestion/ingest_to_graphiti.py` (lignes 20-162)
  - Import `AnthropicClient` → `OpenAIGenericClient`
  - Configuration Haiku 4.5 → DeepSeek R1 + OpenRouter
  - Monkey-patch Anthropic metadata → À retirer (non applicable)
  - Print messages → Mettre à jour

**2. Tests (2 fichiers) :**
- `.aria/knowledge/tests/test_anthropic_graphiti.py`
  - Renommer en `test_deepseek_graphiti.py`
  - Adapter configuration
- `.aria/knowledge/tests/test_haiku_ingestion.py`
  - Adapter ou renommer

**3. MCP Server (1 fichier) :**
- `.aria/knowledge/mcp_servers/graphiti_mcp_server.py`
  - Aucun changement nécessaire (utilise `GraphitiIngestion()`)

**4. Docker (1 fichier) :**
- `.aria/knowledge/zep/docker-compose.yml`
  - Ligne 28: `ZEP_LLM_SERVICE=anthropic` → Peut rester (service Zep indépendant)
  - Ligne 54: `ANTHROPIC_API_KEY` → Peut rester (pour Zep)

**5. Configuration MCP (1 fichier) :**
- `.aria/knowledge/mcp_servers/aria-graphiti-mcp-config.json`
  - Ligne 10: `ANTHROPIC_API_KEY` exposée → Mettre `OPENROUTER_API_KEY`

**6. Documentation (1 fichier principal) :**
- `.aria/knowledge/README.md`
  - Mettre à jour "Architecture" (ligne 6, 119-130)
  - Mettre à jour "LLM Provider" (ligne 7)

### 🔍 Compatibilité Graphiti

**✅ Graphiti supporte OpenRouter via `OpenAIGenericClient` !**

**Preuve :**
```python
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.llm_client import LLMConfig

config = LLMConfig(
    api_key="sk-or-v1-...",          # OpenRouter API key
    base_url="https://openrouter.ai/api/v1",  # Custom base URL
    model="deepseek/deepseek-r1:free",
    max_tokens=2048,
    temperature=0.0
)
client = OpenAIGenericClient(config=config)
```

**Avantages :**
- ✅ Compatible API OpenAI (OpenRouter suit le standard)
- ✅ Support `base_url` custom
- ✅ Pas de monkey-patch nécessaire
- ✅ Plus simple que AnthropicClient

---

## 🔧 PLAN DE MIGRATION DÉTAILLÉ

### Phase 1: Backup (5 min)

**Actions :**
1. Créer backup du code actuel
   ```bash
   mkdir -p .aria/backups/2025-11-02-pre-openrouter
   cp .aria/knowledge/ingestion/ingest_to_graphiti.py .aria/backups/2025-11-02-pre-openrouter/
   cp .aria/knowledge/README.md .aria/backups/2025-11-02-pre-openrouter/
   ```

2. Commit état actuel (si nécessaire)
   ```bash
   git add -A
   git commit -m "backup: Before OpenRouter DeepSeek R1 migration"
   ```

**Validation :**
- ✅ Backups créés
- ✅ Git propre

---

### Phase 2: Mise à jour Code Principal (20 min)

**Fichier:** `.aria/knowledge/ingestion/ingest_to_graphiti.py`

#### 2.1. Imports (lignes 20-24)

**AVANT:**
```python
from graphiti_core.llm_client.anthropic_client import AnthropicClient
import sentry_sdk
from sentry_sdk.integrations.anthropic import AnthropicIntegration
```

**APRÈS:**
```python
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
import sentry_sdk
# Anthropic integration removed (not needed for OpenRouter)
```

#### 2.2. Docstring Classe (ligne 37)

**AVANT:**
```python
"""Ingest reports into Graphiti knowledge graph using Claude Haiku 4.5."""
```

**APRÈS:**
```python
"""Ingest reports into Graphiti knowledge graph using DeepSeek R1 (via OpenRouter)."""
```

#### 2.3. Paramètre __init__ (ligne 44)

**AVANT:**
```python
use_anthropic: bool = True  # NEW: Use Claude Haiku 4.5 by default
```

**APRÈS:**
```python
use_openrouter: bool = True  # NEW: Use DeepSeek R1 via OpenRouter by default
```

#### 2.4. Méthode initialize() (lignes 63-115)

**AVANT:**
```python
async def initialize(self):
    """Initialize Graphiti client with Claude Haiku 4.5 (async)."""
    if self.graphiti is None:
        # Configure LLM client with metadata support
        llm_client = None
        if self.use_anthropic:
            # Use Claude Haiku 4.5 for LLM operations
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            
            llm_config = LLMConfig(
                api_key=anthropic_key,
                model='claude-haiku-4-5-20251001',  # Haiku 4.5 official model ID
                max_tokens=2048,       # Production Guide Line 351
                temperature=0.0        # Production Guide Line 352
            )
            llm_client = AnthropicClient(config=llm_config, cache=False)
            
            # ⭐ MONKEY-PATCH: Inject metadata into Anthropic API calls
            self._patch_anthropic_client(llm_client)
            
            print("🤖 Using Claude Haiku 4.5 for LLM operations (v1.5.0)")
            print("📊 Anthropic Usage API tracking enabled (metadata injection)")
        else:
            print("🤖 Using OpenAI (default) for LLM operations")
```

**APRÈS:**
```python
async def initialize(self):
    """Initialize Graphiti client with DeepSeek R1 via OpenRouter (async)."""
    if self.graphiti is None:
        # Configure LLM client
        llm_client = None
        if self.use_openrouter:
            # Use DeepSeek R1 (FREE) via OpenRouter for LLM operations
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            if not openrouter_key:
                raise ValueError("OPENROUTER_API_KEY not found in environment")
            
            llm_config = LLMConfig(
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",  # OpenRouter endpoint
                model='deepseek/deepseek-r1:free',        # DeepSeek R1 FREE model
                max_tokens=2048,       # Keep same config (Production Guide)
                temperature=0.0        # Deterministic extraction
            )
            llm_client = OpenAIGenericClient(config=llm_config, cache=False)
            
            print("🤖 Using DeepSeek R1 for LLM operations (via OpenRouter) - FREE! 🎉")
            print("💰 Cost: $0/night (was $1-2 with Haiku 4.5)")
            print("🌐 Provider: OpenRouter (https://openrouter.ai)")
        else:
            print("🤖 Using OpenAI (default) for LLM operations")
```

#### 2.5. SEMAPHORE_LIMIT (lignes 90-102)

**AVANT:**
```python
# Set SEMAPHORE_LIMIT based on production guide recommendations (Priority 4B)
# Production Guide Line 337-341:
# - Default: 10 (safe for most providers)
# - Anthropic Claude: 15-20 (higher rate limits)
# - Lower to 5-8 only if hitting 429 errors
#
# RECOMMENDATION: Set SEMAPHORE_LIMIT=15 in .env for optimal throughput
# Default to 15 if not set (Anthropic handles this well)
if not os.getenv('SEMAPHORE_LIMIT'):
    os.environ['SEMAPHORE_LIMIT'] = '15'
    print("🔧 Set SEMAPHORE_LIMIT=15 (default for Anthropic Claude)")
else:
    print(f"🔧 SEMAPHORE_LIMIT={os.getenv('SEMAPHORE_LIMIT')} (from .env)")
```

**APRÈS:**
```python
# Set SEMAPHORE_LIMIT for OpenRouter DeepSeek R1
# OpenRouter free tier has rate limits, so we use conservative value
# - DeepSeek R1 Free: Start with 5 concurrent calls
# - Can increase to 8-10 if no 429 errors observed
# - Lower to 3 if hitting rate limits
#
# RECOMMENDATION: Set SEMAPHORE_LIMIT=5 in .env for free tier
# Default to 5 if not set (conservative for free tier)
if not os.getenv('SEMAPHORE_LIMIT'):
    os.environ['SEMAPHORE_LIMIT'] = '5'
    print("🔧 Set SEMAPHORE_LIMIT=5 (default for OpenRouter free tier)")
else:
    print(f"🔧 SEMAPHORE_LIMIT={os.getenv('SEMAPHORE_LIMIT')} (from .env)")
```

#### 2.6. Print Message (ligne 115)

**AVANT:**
```python
print("✅ Graphiti initialized (LLM: Claude Haiku 4.5, Embeddings: OpenAI)")
```

**APRÈS:**
```python
print("✅ Graphiti initialized (LLM: DeepSeek R1 FREE via OpenRouter, Embeddings: OpenAI)")
```

#### 2.7. Retirer Monkey-Patch (lignes 117-162)

**AVANT:**
```python
def _patch_anthropic_client(self, client: AnthropicClient):
    """
    Monkey-patch Anthropic client to inject metadata into API calls.
    ... (60 lignes)
    """
    # ... code complet ...
```

**APRÈS:**
```python
# Monkey-patch removed - not needed for OpenRouter
# OpenRouter uses standard OpenAI API format (no metadata injection needed)
```

#### 2.8. Méthode _build_description_metadata (ligne 164-197)

**AVANT:**
```python
def _build_description_metadata(self, report_data: Dict[str, Any]) -> str:
    """Build description for Anthropic Usage API tracking."""
    # ... code ...
```

**APRÈS:**
```python
# Metadata tracking removed - not applicable to OpenRouter free tier
# Cost is $0, so no need to track per-agent consumption
```

**Validation Phase 2 :**
- ✅ Imports mis à jour
- ✅ Configuration OpenRouter implémentée
- ✅ Monkey-patch retiré
- ✅ SEMAPHORE_LIMIT adapté (5)
- ✅ Messages mis à jour

---

### Phase 3: Mise à jour Tests (15 min)

#### 3.1. Renommer test principal

**Action:**
```bash
cd .aria/knowledge/tests
mv test_anthropic_graphiti.py test_deepseek_graphiti.py
```

#### 3.2. Adapter `test_deepseek_graphiti.py`

**Changements:**
- Import: `AnthropicClient` → `OpenAIGenericClient`
- Variable: `ANTHROPIC_API_KEY` → `OPENROUTER_API_KEY`
- Model: `claude-haiku-4-5-20251001` → `deepseek/deepseek-r1:free`
- Config: Ajouter `base_url="https://openrouter.ai/api/v1"`
- Messages: Adapter les prints

#### 3.3. Adapter `test_haiku_ingestion.py`

**Option 1:** Renommer en `test_deepseek_ingestion.py` et adapter
**Option 2:** Laisser tel quel (test générique)

**Validation Phase 3 :**
- ✅ Tests renommés
- ✅ Configuration adaptée
- ✅ Tests prêts à exécuter

---

### Phase 4: Configuration MCP (5 min)

**Fichier:** `.aria/knowledge/mcp_servers/aria-graphiti-mcp-config.json`

**AVANT (ligne 10):**
```json
"ANTHROPIC_API_KEY": "sk-ant-api03-..."
```

**APRÈS:**
```json
"OPENROUTER_API_KEY": "sk-or-v1-..."
```

**Note:** Le serveur MCP utilise `GraphitiIngestion()` qui lira automatiquement `OPENROUTER_API_KEY`.

**Validation Phase 4 :**
- ✅ MCP config mis à jour

---

### Phase 5: Documentation (10 min)

**Fichier:** `.aria/knowledge/README.md`

#### 5.1. Header (lignes 1-11)

**AVANT:**
```markdown
**Architecture:** Graphiti + Neo4j Community Edition + **Claude Haiku 4.5** 🚀  
**LLM Provider:** **Claude Haiku 4.5** (near-frontier intelligence) ✅ IN PRODUCTION  
**Monitoring:** ✅ Sentry integrated  
**Rate Limit Protection:** ✅ Safe Ingestion Queue + Zero OpenAI LLM rate limits ✅
```

**APRÈS:**
```markdown
**Architecture:** Graphiti + Neo4j Community Edition + **DeepSeek R1 (FREE via OpenRouter)** 💰  
**LLM Provider:** **DeepSeek R1** (via OpenRouter) - **$0 cost!** ✅ IN PRODUCTION  
**Monitoring:** ✅ Sentry integrated  
**Rate Limit Protection:** ✅ Safe Ingestion Queue + Conservative SEMAPHORE_LIMIT=5
```

#### 5.2. Key Features (lignes 18-32)

**AVANT:**
```markdown
- 🤖 **Near-Frontier Intelligence** - Claude Haiku 4.5 = Sonnet 4 performance (v1.4.0) 🚀
- ⚡ **2× Faster Processing** - Claude Haiku 4.5 speed advantage (v1.4.0)
- 💰 **Cost Optimized** - $1/$5 per million tokens (v1.4.0)
```

**APRÈS:**
```markdown
- 🤖 **Free Tier LLM** - DeepSeek R1 via OpenRouter (v1.7.0) 💰
- ⚡ **Zero Cost** - $0/night for knowledge graph operations! 🎉
- 💰 **Budget Friendly** - Free tier = unlimited nightly runs
```

#### 5.3. Technology Stack (lignes 118-131)

**AVANT:**
```markdown
### Technology Stack
- **Claude Haiku 4.5** - Near-frontier intelligence for LLM operations (v1.4.0) 🚀
  - Model: `claude-haiku-4-5-20251001`
  - Performance: Equals Sonnet 4 intelligence
  - Speed: 2× faster than Sonnet 4
  - Cost: $1 input / $5 output per million tokens
```

**APRÈS:**
```markdown
### Technology Stack
- **DeepSeek R1** - Free tier LLM via OpenRouter (v1.7.0) 💰
  - Model: `deepseek/deepseek-r1:free`
  - Provider: OpenRouter (https://openrouter.ai)
  - Performance: Sufficient for entity extraction
  - Speed: Good for nightly batch processing
  - Cost: **$0** (free tier!)
```

#### 5.4. Version History (ligne 98)

**Ajouter:**
```markdown
- v1.7.0 (Nov 2): **MIGRATION TO OPENROUTER DEEPSEEK R1 (FREE)** 💰
  * BREAKING: Replaced Claude Haiku 4.5 with DeepSeek R1 via OpenRouter
  * Cost: $1-2/night → **$0/night** (100% reduction!)
  * Reason: Knowledge Graph too expensive with Anthropic
  * Provider: OpenRouter (https://openrouter.ai)
  * Model: deepseek/deepseek-r1:free
  * Config: SEMAPHORE_LIMIT=5 (conservative for free tier)
  * Status: Agents still use Sonnet 4.5 (Anthropic direct)
  * Impact: Unlimited nightly runs, zero knowledge graph costs
```

**Validation Phase 5 :**
- ✅ README.md mis à jour
- ✅ Version history complété
- ✅ Architecture documentée

---

### Phase 6: Variables d'Environnement (2 min)

**Fichier:** `.aria/.env`

**Vérifier présence de:**
```bash
OPENROUTER_API_KEY=sk-or-v1-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**⚠️ SECURITY NOTE:** The actual API key was removed from this document for security reasons. Use the key from your `.env` file.

**Optionnel - Ajuster SEMAPHORE_LIMIT:**
```bash
# Add or update:
SEMAPHORE_LIMIT=5  # Conservative for OpenRouter free tier
```

**Validation Phase 6 :**
- ✅ OPENROUTER_API_KEY présent
- ✅ SEMAPHORE_LIMIT configuré

---

### Phase 7: Test Validation (20 min)

#### 7.1. Test Unitaire

```bash
cd .aria/knowledge/tests
pytest test_deepseek_graphiti.py -v
```

**Attendu:**
- ✅ Connexion OpenRouter réussie
- ✅ Graphiti initialisé
- ✅ Episode ingesté
- ✅ Entity extraction fonctionnelle

#### 7.2. Test d'Intégration

```bash
cd .aria/knowledge/automation
python3 test_single_episode.py
```

**Attendu:**
- ✅ GraphitiIngestion initialisé avec DeepSeek R1
- ✅ Episode ingesté via OpenRouter
- ✅ Coût = $0
- ✅ Pas d'erreur 429

#### 7.3. Test Complet (Micro-Batch)

**Créer:** `.aria/knowledge/automation/test_deepseek_micro.py`
```python
"""Test DeepSeek R1 avec 3 micro episodes"""
import asyncio
from ingest_to_graphiti import GraphitiIngestion

async def test_deepseek_micro():
    print("🧪 Testing DeepSeek R1 via OpenRouter...")
    
    client = GraphitiIngestion(use_openrouter=True)
    await client.initialize()
    
    # Test 3 micro episodes
    for i in range(3):
        episode = {
            'name': f'test-deepseek-{i}',
            'episode_body': f'Test episode {i} for DeepSeek R1 validation.',
            'source_description': 'Test',
            'reference_time': '2025-11-02T17:00:00'
        }
        await client.ingest_report(episode)
        print(f"✅ Episode {i} ingested")
    
    print("🎉 DeepSeek R1 validation complete!")

if __name__ == '__main__':
    asyncio.run(test_deepseek_micro())
```

**Exécuter:**
```bash
python3 .aria/knowledge/automation/test_deepseek_micro.py
```

**Attendu:**
- ✅ 3/3 episodes ingested
- ✅ Cost: $0
- ✅ No rate limit errors
- ✅ < 30 seconds execution

**Validation Phase 7 :**
- ✅ Tests unitaires passent
- ✅ Test intégration passe
- ✅ Micro-batch validé
- ✅ Coût confirmé $0

---

### Phase 8: Commit & Documentation (10 min)

#### 8.1. Commit Changes

```bash
cd /Users/nicozefrench/Obsidian

git add .aria/knowledge/ingestion/ingest_to_graphiti.py
git add .aria/knowledge/README.md
git add .aria/knowledge/tests/test_deepseek_graphiti.py
git add .aria/knowledge/mcp_servers/aria-graphiti-mcp-config.json
git add .aria/docs/deployment/OPENROUTER-DEEPSEEK-MIGRATION-PLAN-2025-11-02.md

git commit -m "feat: Migrate Knowledge Graph from Haiku 4.5 to DeepSeek R1 (OpenRouter FREE)

🔄 MAJOR MIGRATION: Knowledge Graph LLM Provider Change

Migrated ARIA Knowledge Graph from Claude Haiku 4.5 (Anthropic, costly)
to DeepSeek R1 via OpenRouter (FREE tier).

🎯 Motivation:
- Knowledge Graph with Haiku 4.5 costs \$1-2/night minimum (even optimized)
- DeepSeek R1 via OpenRouter is FREE
- Entity extraction doesn't require frontier intelligence
- Agents (ARIA, CARO, BOB, etc.) still use Sonnet 4.5 (Anthropic direct)

💰 Cost Impact:
- Before: \$1-2/night (Knowledge Graph alone)
- After: \$0/night (100% reduction!)
- Annual Savings: \$365-730 saved!

🔧 Changes:
- Replaced AnthropicClient with OpenAIGenericClient
- Updated model: claude-haiku-4-5-20251001 → deepseek/deepseek-r1:free
- Added OpenRouter config: base_url, OPENROUTER_API_KEY
- Removed Anthropic metadata injection (not applicable)
- Updated SEMAPHORE_LIMIT: 15 → 5 (conservative for free tier)
- Updated documentation: README.md, version history

📁 Files Modified:
- .aria/knowledge/ingestion/ingest_to_graphiti.py (v1.5.0 → v1.7.0)
- .aria/knowledge/README.md (v1.6.0 → v1.7.0)
- .aria/knowledge/tests/test_anthropic_graphiti.py → test_deepseek_graphiti.py
- .aria/knowledge/mcp_servers/aria-graphiti-mcp-config.json

✅ Validation:
- Unit tests passed (test_deepseek_graphiti.py)
- Integration test passed (test_single_episode.py)
- Micro-batch test passed (3 episodes, \$0 cost)
- No rate limit errors
- Graphiti operational with OpenRouter

🌐 OpenRouter:
- Provider: https://openrouter.ai
- Model: deepseek/deepseek-r1:free
- Cost: \$0 (free tier)
- API Key: OPENROUTER_API_KEY (from .env)

🎉 Knowledge Graph is now FREE forever!

Refs: OPENROUTER-DEEPSEEK-MIGRATION-PLAN-2025-11-02.md"
```

#### 8.2. Push to GitHub

```bash
git push origin fix/cost-optimization-steph-knowledge
```

#### 8.3. Créer Implementation Report

**Fichier:** `.aria/docs/deployment/OPENROUTER-MIGRATION-COMPLETE-2025-11-02.md`
- Résumé de la migration
- Résultats des tests
- Comparaison avant/après
- Leçons apprises

**Validation Phase 8 :**
- ✅ Commits créés
- ✅ Pushed to GitHub
- ✅ Implementation report créé

---

### Phase 9: Production Validation (Tonight 23:00)

**Test en production lors du nightly run :**

#### 9.1. Monitoring

**Vérifier dans les logs (`automation/logs/nightly_reviews_*.log`) :**
```
🤖 Using DeepSeek R1 for LLM operations (via OpenRouter) - FREE! 🎉
💰 Cost: $0/night (was $1-2 with Haiku 4.5)
🌐 Provider: OpenRouter (https://openrouter.ai)
🔧 Set SEMAPHORE_LIMIT=5 (default for OpenRouter free tier)
✅ Graphiti initialized (LLM: DeepSeek R1 FREE via OpenRouter, Embeddings: OpenAI)
```

#### 9.2. Métriques

**Comparer avant/après :**
| Métrique | Haiku 4.5 (Avant) | DeepSeek R1 (Après) |
|----------|-------------------|---------------------|
| Coût/nuit | $1-2 | **$0** ✅ |
| Rate limits | Possibles | Moins probables |
| SEMAPHORE_LIMIT | 15 | 5 |
| Duration | ~2-3 min | ~3-5 min (acceptable) |

#### 9.3. Rollback Plan (si échec)

**Si problème critique en production :**

```bash
# 1. Restaurer backup
cp .aria/backups/2025-11-02-pre-openrouter/ingest_to_graphiti.py \
   .aria/knowledge/ingestion/ingest_to_graphiti.py

# 2. Commit rollback
git add .aria/knowledge/ingestion/ingest_to_graphiti.py
git commit -m "revert: Rollback to Haiku 4.5 (OpenRouter issues)"
git push origin fix/cost-optimization-steph-knowledge

# 3. Redémarrer services si nécessaire
```

**Validation Phase 9 :**
- ⏰ Attendre nightly run (23:00)
- 🌅 Audit demain matin
- ✅ Valider $0 cost
- ✅ Valider fonctionnement

---

## 📊 RÉSUMÉ COMPARATIF

### Avant Migration (Haiku 4.5)

| Aspect | Valeur |
|--------|--------|
| **Provider** | Anthropic (direct) |
| **Modèle** | claude-haiku-4-5-20251001 |
| **Coût Input** | $1/M tokens |
| **Coût Output** | $5/M tokens |
| **Coût/nuit** | **$1-2** (Knowledge Graph) |
| **Coût/an** | **$365-730** |
| **Metadata** | Tracking via Usage API |
| **SEMAPHORE_LIMIT** | 15 |
| **Rate Limits** | 4M tokens/min (Tier 4) |

### Après Migration (DeepSeek R1)

| Aspect | Valeur |
|--------|--------|
| **Provider** | OpenRouter |
| **Modèle** | deepseek/deepseek-r1:free |
| **Coût Input** | **$0** |
| **Coût Output** | **$0** |
| **Coût/nuit** | **$0** ✅ |
| **Coût/an** | **$0** ✅ |
| **Metadata** | N/A (coût $0) |
| **SEMAPHORE_LIMIT** | 5 (conservatif) |
| **Rate Limits** | Free tier limits (TBD) |

### Agents (INCHANGÉS)

| Agent | Provider | Modèle | Coût |
|-------|----------|--------|------|
| ARIA | Anthropic | Sonnet 4.5 | $3/$15/M |
| CARO | Anthropic | Sonnet 4.5 | $3/$15/M |
| BOB | Anthropic | Sonnet 4.5 | $3/$15/M |
| STEPH | Anthropic | Sonnet 4.5 | $3/$15/M |
| PEPPER | Anthropic | Sonnet 4.5 | $3/$15/M |
| K2000 | Anthropic | Sonnet 4.5 | $3/$15/M |

**Note:** Les agents continuent d'utiliser Sonnet 4.5 (Anthropic direct) car ils nécessitent frontier intelligence.

---

## ⚠️ RISQUES & MITIGATION

### Risque 1: Qualité Entity Extraction

**Risque:** DeepSeek R1 moins performant que Haiku 4.5 pour entity extraction

**Mitigation:**
- ✅ Test validation avant production
- ✅ Comparer qualité entities extraites
- ✅ Rollback plan prêt si qualité insuffisante
- ✅ DeepSeek R1 suffisant pour structured extraction

**Probabilité:** Faible (DeepSeek est capable)

### Risque 2: Rate Limits Free Tier

**Risque:** OpenRouter free tier peut avoir rate limits stricts

**Mitigation:**
- ✅ SEMAPHORE_LIMIT=5 (conservatif)
- ✅ SafeIngestionQueue delays (5 min entre steps)
- ✅ Nightly run = batch processing (pas real-time)
- ✅ Monitoring via logs

**Probabilité:** Moyenne (mais mitigation efficace)

### Risque 3: Stabilité OpenRouter

**Risque:** Service OpenRouter peut être instable

**Mitigation:**
- ✅ Retry logic dans SafeIngestionQueue
- ✅ Exponential backoff implémenté
- ✅ Backup vers Haiku 4.5 disponible
- ✅ OpenRouter = production-ready service

**Probabilité:** Faible

### Risque 4: Changement Free Tier

**Risque:** OpenRouter peut changer/retirer free tier DeepSeek R1

**Mitigation:**
- ✅ Migration facile vers autre provider
- ✅ OpenAIGenericClient supporte n'importe quel provider OpenAI-compatible
- ✅ Alternative: DeepSeek R1 paid tier ($0.55/$2.19/M tokens)
- ✅ Alternative 2: Rollback Haiku 4.5

**Probabilité:** Faible à moyen terme

---

## ✅ SUCCESS CRITERIA

**Migration considérée réussie si :**

1. ✅ **Coût $0** pour Knowledge Graph (vérifié dans Anthropic console)
2. ✅ **Nightly run complète** sans erreur
3. ✅ **Entities extraites** correctement (qualité acceptable)
4. ✅ **Pas de rate limit 429** errors
5. ✅ **MCP tools fonctionnels** (search, facts, etc.)
6. ✅ **Duration acceptable** (< 10 min pour ingestion)
7. ✅ **Agents INCHANGÉS** (toujours Sonnet 4.5)

**Si tous les critères OK → Migration permanente**  
**Si échec → Rollback vers Haiku 4.5**

---

## 🎯 TIMELINE

| Phase | Durée | Status |
|-------|-------|--------|
| Phase 1: Backup | 5 min | ⏳ Pending |
| Phase 2: Code Principal | 20 min | ⏳ Pending |
| Phase 3: Tests | 15 min | ⏳ Pending |
| Phase 4: Config MCP | 5 min | ⏳ Pending |
| Phase 5: Documentation | 10 min | ⏳ Pending |
| Phase 6: Env Variables | 2 min | ⏳ Pending |
| Phase 7: Test Validation | 20 min | ⏳ Pending |
| Phase 8: Commit & Docs | 10 min | ⏳ Pending |
| Phase 9: Production | Ce soir 23:00 | ⏳ Pending |
| **TOTAL** | **~90 minutes** | ⏳ Ready to execute |

---

## 📚 RÉFÉRENCES

### Documentation OpenRouter
- Site: https://openrouter.ai
- Docs: https://openrouter.ai/docs
- Models: https://openrouter.ai/models
- DeepSeek R1: https://openrouter.ai/models/deepseek/deepseek-r1

### Documentation Graphiti
- OpenAIGenericClient: `graphiti_core.llm_client.openai_generic_client`
- LLMConfig: `graphiti_core.llm_client.config`
- Graphiti: `graphiti_core.Graphiti`

### Fichiers Modifiés
- `.aria/knowledge/ingestion/ingest_to_graphiti.py` (principal)
- `.aria/knowledge/README.md` (documentation)
- `.aria/knowledge/tests/test_deepseek_graphiti.py` (tests)
- `.aria/knowledge/mcp_servers/aria-graphiti-mcp-config.json` (config)

### Backups
- `.aria/backups/2025-11-02-pre-openrouter/` (rollback)

---

**Plan créé:** Nov 2, 2025, 17:00 CET  
**Status:** 📋 **COMPLET - Ready for execution**  
**Durée estimée:** 90 minutes  
**Next:** Exécuter Phase 1 (Backup)

---

*Ce plan permet de migrer le Knowledge Graph vers OpenRouter DeepSeek R1 (gratuit) tout en conservant les agents sur Sonnet 4.5 (Anthropic). Économies annuelles : $365-730 !* 🎉

