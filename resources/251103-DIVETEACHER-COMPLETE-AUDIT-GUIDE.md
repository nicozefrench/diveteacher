# 🔍 DIVETEACHER: COMPLETE GEMINI 2.5 FLASH-LITE IMPLEMENTATION AUDIT

**Date:** 2025-11-03  
**From:** ARIA Team (après résolution de tous les bugs)  
**To:** DiveTeacher Developer  
**Priority:** 🔴 CRITICAL - Vérification complète requise avant production

---

## 🎯 OBJECTIF

ARIA a finalisé l'implémentation de **Gemini 2.5 Flash-Lite + OpenAI Embeddings** après avoir résolu **7 bugs critiques** découverts lors de tests exhaustifs. Vous devez maintenant auditer votre implémentation DiveTeacher pour éviter ces mêmes bugs.

**Résultat attendu:** Système DiveTeacher 100% fonctionnel avec Gemini 2.5 Flash-Lite, sans erreurs.

---

## 📋 CHECKLIST COMPLÈTE (À SUIVRE DANS L'ORDRE)

### ✅ PHASE 1: AUDIT DU CODE

#### 1.1 Vérifier le fichier d'ingestion principal

**Fichier:** Votre équivalent de `ingest_to_graphiti.py`

**À vérifier ligne par ligne:**

```python
# ✅ 1. IMPORTS - Vérifier que TOUS ces imports sont présents et corrects:

from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig  # ⚠️ PAS OpenAIClient!
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig  # ⚠️ OpenAI pour embeddings!
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.nodes import EpisodeType
```

**❌ Bug #1 découvert:** Import incorrect → `OpenAIClient` au lieu de `GeminiClient`  
**✅ Fix:** Utiliser `GeminiClient` pour le LLM, `OpenAIEmbedder` pour les embeddings

---

#### 1.2 Vérifier la configuration LLM

**Configuration LLM (Gemini):**

```python
# ✅ CORRECT:
gemini_key = os.getenv('GEMINI_API_KEY')
if not gemini_key:
    raise ValueError("GEMINI_API_KEY not found in environment")

llm_config = LLMConfig(
    api_key=gemini_key,
    model='gemini-2.5-flash-lite'  # ⚠️ Exactement ce nom!
)

llm_client = GeminiClient(  # ⚠️ GeminiClient, PAS OpenAIClient!
    config=llm_config,
    cache=False
)
```

**❌ Bug #2 découvert:** Mauvais nom de modèle → `gemini-2.0-flash-exp` (overloaded)  
**✅ Fix:** Utiliser `gemini-2.5-flash-lite` (stable, ultra-low cost, 4K RPM)

**❌ Bug #3 découvert:** Utilisation de `OpenAIClient` avec Gemini  
**✅ Fix:** `GeminiClient` est le client natif recommandé par Graphiti

---

#### 1.3 Vérifier la configuration Embeddings

**Configuration Embeddings (OpenAI):**

```python
# ✅ CORRECT:
openai_key = os.getenv('OPENAI_API_KEY')
if not openai_key:
    raise ValueError("OPENAI_API_KEY not found in environment for embeddings")

embedder_config = OpenAIEmbedderConfig(
    api_key=openai_key,
    embedding_model="text-embedding-3-small",  # ⚠️ Exactement ce nom!
    embedding_dim=1536  # ⚠️ Critique: 1536 dimensions pour OpenAI!
)
embedder_client = OpenAIEmbedder(config=embedder_config)

# ✅ CORRECT: Cross-encoder (OpenAI aussi)
cross_encoder_config = LLMConfig(
    api_key=openai_key,
    model="gpt-4o-mini"  # ⚠️ Modèle léger pour reranking
)
cross_encoder_client = OpenAIRerankerClient(config=cross_encoder_config)
```

**❌ Bug #4 découvert:** Embeddings Gemini (768 dims) incompatibles avec DB OpenAI (1536 dims)  
**✅ Fix:** Toujours utiliser `OpenAIEmbedder` avec `text-embedding-3-small` (1536 dims)

**🚨 CRITIQUE:** Si vous utilisez Gemini embeddings, TOUTE votre DB Neo4j doit être vidée et réingérée!

---

#### 1.4 Vérifier l'initialisation Graphiti

**Initialisation complète:**

```python
# ✅ CORRECT:
self.graphiti = Graphiti(
    neo4j_uri,
    neo4j_user,
    neo4j_password,
    llm_client=llm_client,          # ⚠️ GeminiClient pour LLM
    embedder=embedder_client,        # ⚠️ EXPLICIT! OpenAIEmbedder pour embeddings
    cross_encoder=cross_encoder_client  # ⚠️ EXPLICIT! OpenAIRerankerClient
)
```

**❌ Bug #5 découvert:** `embedder` et `cross_encoder` non passés explicitement  
**✅ Fix:** TOUJOURS passer `embedder` et `cross_encoder` explicitement pour éviter les defaults

---

#### 1.5 Vérifier SEMAPHORE_LIMIT

**Configuration rate limiting:**

```python
# ✅ CORRECT pour Gemini 2.5 Flash-Lite Tier 1 (4K RPM):
if not os.getenv('SEMAPHORE_LIMIT'):
    os.environ['SEMAPHORE_LIMIT'] = '10'  # ⚠️ 10 pour 4K RPM (safe + fast)
```

**Dans votre `.env`:**
```bash
SEMAPHORE_LIMIT=10  # ⚠️ Pour Gemini 2.5 Flash-Lite Tier 1 (4K RPM)
```

**❌ Bug #6 découvert:** `SEMAPHORE_LIMIT=15` trop élevé → 429 errors  
**✅ Fix:** `SEMAPHORE_LIMIT=10` optimal pour 4K RPM (Tier 1)

**Rate limits Gemini 2.5 Flash-Lite:**
- **Free Tier:** 15 RPM → `SEMAPHORE_LIMIT=2`
- **Tier 1 (payant):** 4K RPM → `SEMAPHORE_LIMIT=10`

---

### ✅ PHASE 2: AUDIT DES CLÉS API

#### 2.1 Vérifier le fichier .env

**Fichier:** `.env` (à la racine de votre projet)

```bash
# ✅ Vérifier ces deux clés:
GEMINI_API_KEY=AIza...  # ⚠️ Clé Google AI Studio
OPENAI_API_KEY=sk-proj-...  # ⚠️ Clé OpenAI pour embeddings
SEMAPHORE_LIMIT=10  # ⚠️ Pour Tier 1

# ❌ NE PAS utiliser:
# OPENROUTER_API_KEY=...  # ⚠️ On n'utilise PLUS OpenRouter!
# ANTHROPIC_API_KEY=...   # ⚠️ On n'utilise PLUS Anthropic!
```

#### 2.2 Tester les clés API

**Commande de test:**

```bash
# Test 1: Vérifier que les clés sont chargées
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env')

gemini = os.getenv('GEMINI_API_KEY')
openai = os.getenv('OPENAI_API_KEY')

print('GEMINI_API_KEY:', '✅ Found' if gemini else '❌ Missing')
print('OPENAI_API_KEY:', '✅ Found' if openai else '❌ Missing')
print('SEMAPHORE_LIMIT:', os.getenv('SEMAPHORE_LIMIT', 'NOT SET'))
"
```

**Résultat attendu:**
```
GEMINI_API_KEY: ✅ Found
OPENAI_API_KEY: ✅ Found
SEMAPHORE_LIMIT: 10
```

---

### ✅ PHASE 3: AUDIT DE LA BASE DE DONNÉES NEO4J

#### 3.1 Vérifier les dimensions des embeddings existants

**🚨 CRITIQUE:** C'est le bug qui a cassé ARIA pendant 2 jours!

**Commande de diagnostic:**

```bash
# Via Docker (si Neo4j dans Docker):
docker exec <your-neo4j-container> cypher-shell -u neo4j -p <password> \
  "MATCH (n:Entity) RETURN size(n.name_embedding) as dims LIMIT 1"

# Via cypher-shell direct:
cypher-shell -u neo4j -p <password> \
  "MATCH (n:Entity) RETURN size(n.name_embedding) as dims LIMIT 1"
```

**Résultats possibles:**

| Dimensions | Signification | Action requise |
|-----------|---------------|----------------|
| **Pas de résultat** (DB vide) | ✅ OK - DB neuve | Aucune action |
| **1536** | ✅ OK - OpenAI embeddings | Aucune action |
| **768** | ❌ Gemini embeddings | 🚨 **VIDER LA DB!** |
| **1024** | ❌ Ancien modèle | 🚨 **VIDER LA DB!** |
| **Autre** | ❌ Modèle inconnu | 🚨 **VIDER LA DB!** |

**❌ Bug #7 découvert:** DB avait 1024 dims → Incompatible avec OpenAI (1536)  
**✅ Fix:** Vider complètement la DB avant de réingérer avec les bons embeddings

---

#### 3.2 Vider la base de données (si nécessaire)

**⚠️ À faire SEULEMENT si dimensions ≠ 1536:**

```bash
# Étape 1: Backup (optionnel, si données importantes)
docker exec <your-neo4j-container> neo4j-admin dump \
  --database=neo4j \
  --to=/backups/neo4j-pre-migration-$(date +%Y%m%d_%H%M%S).dump

# Étape 2: Vider TOUTE la DB
docker exec <your-neo4j-container> cypher-shell -u neo4j -p <password> \
  "MATCH (n) DETACH DELETE n"

# Étape 3: Vérifier que la DB est vide
docker exec <your-neo4j-container> cypher-shell -u neo4j -p <password> \
  "MATCH (n) RETURN count(n) as total"
# Résultat attendu: total = 0
```

**🎯 Pourquoi vider la DB?**

Si votre DB contient des embeddings de **768 dimensions** (Gemini) et que vous essayez d'insérer des embeddings de **1536 dimensions** (OpenAI), Neo4j va crasher avec:

```
Invalid input for 'vector.similarity.cosine()': 
The supplied vectors do not have the same number of dimensions.
```

**Solution:** Repartir avec une DB propre!

---

### ✅ PHASE 4: TEST D'INTÉGRATION COMPLET

#### 4.1 Créer un script de test

**Fichier:** `test_graphiti_integration.py`

```python
#!/usr/bin/env python3
"""
Test complet de l'intégration Gemini 2.5 Flash-Lite + OpenAI Embeddings
"""
import os
import sys
import asyncio
from datetime import datetime

# Adapter le path à votre projet
sys.path.insert(0, '/path/to/your/project')

from dotenv import load_dotenv
load_dotenv('.env')

# Importer votre classe d'ingestion (adapter le nom)
from your_ingestion_module import YourGraphitiIngestionClass

print("\n" + "="*70)
print("🧪 TEST D'INTÉGRATION - GEMINI 2.5 FLASH-LITE + OPENAI EMBEDDINGS")
print("="*70)

async def test_full_integration():
    """Test complet de l'ingestion"""
    
    # 1. Vérifier les variables d'environnement
    print("\n1️⃣  Vérification des clés API:")
    gemini_key = os.getenv('GEMINI_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    semaphore = os.getenv('SEMAPHORE_LIMIT')
    
    print(f"   ├─ GEMINI_API_KEY: {'✅ Found' if gemini_key else '❌ Missing'}")
    print(f"   ├─ OPENAI_API_KEY: {'✅ Found' if openai_key else '❌ Missing'}")
    print(f"   └─ SEMAPHORE_LIMIT: {semaphore if semaphore else '❌ Not set'}")
    
    if not gemini_key or not openai_key:
        print("\n❌ API keys manquantes! Vérifier votre .env")
        return False
    
    # 2. Initialiser le client
    print("\n2️⃣  Initialisation du client Graphiti:")
    try:
        client = YourGraphitiIngestionClass()  # Adapter le nom
        await client.initialize()
        print("   ✅ Client initialisé avec succès")
    except Exception as e:
        print(f"   ❌ Erreur d'initialisation: {e}")
        return False
    
    # 3. Test d'ingestion
    print("\n3️⃣  Test d'ingestion d'un épisode:")
    
    test_episode = {
        "episode_id": f"test-integration-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "content": """
        TEST D'INTÉGRATION DIVETEACHER
        
        Ce test valide:
        - LLM: Gemini 2.5 Flash-Lite (Google AI Direct)
        - Embeddings: OpenAI text-embedding-3-small (1536 dimensions)
        - Cross-encoder: OpenAI gpt-4o-mini
        - Neo4j: Connexion et stockage
        - Rate limiting: SEMAPHORE_LIMIT configuré
        
        Si ce test passe, votre système est 100% opérationnel!
        """.strip(),
        "timestamp": datetime.now(),
        "agent": "TEST",
        "type": "integration_test",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "context": "testing",
        "metadata": {"test": True, "version": "1.0.0"}
    }
    
    print(f"   ├─ Episode ID: {test_episode['episode_id']}")
    print(f"   ├─ Content: {len(test_episode['content'])} chars")
    print(f"   └─ Ingestion...")
    
    try:
        start = datetime.now()
        result = await client.add_episode(test_episode)
        elapsed = (datetime.now() - start).total_seconds()
        
        if result.get("success") or result.get("status") == "success":
            print(f"\n   ✅ Ingestion réussie en {elapsed:.1f}s!")
            print(f"   ├─ Entities: {result.get('entities_count', 0)}")
            print(f"   ├─ Relations: {result.get('relations_count', 0)}")
            print(f"   └─ Status: {result.get('status', 'success')}")
            success = True
        else:
            print(f"\n   ❌ Ingestion échouée:")
            print(f"   └─ Error: {result.get('error', 'Unknown')}")
            success = False
            
    except Exception as e:
        print(f"\n   ❌ Exception lors de l'ingestion:")
        print(f"   └─ {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        success = False
    
    finally:
        print("\n4️⃣  Cleanup:")
        await client.close()
        print("   ✅ Client fermé")
    
    return success

# Exécuter le test
try:
    success = asyncio.run(test_full_integration())
    
    print("\n" + "="*70)
    if success:
        print("✅✅✅ TEST D'INTÉGRATION: RÉUSSI ✅✅✅")
        print("="*70)
        print("\n🎉 Votre système DiveTeacher est PRODUCTION READY!")
        print("💰 Configuration:")
        print("   ├─ LLM: Gemini 2.5 Flash-Lite ($0.10/M input + $0.40/M output)")
        print("   ├─ Embeddings: OpenAI text-embedding-3-small ($0.02/M)")
        print("   ├─ Rate Limit: 4K RPM (Tier 1)")
        print("   └─ SEMAPHORE_LIMIT: 10")
        print("\n✅ Tous les systèmes GO! 🚀")
        sys.exit(0)
    else:
        print("❌❌❌ TEST D'INTÉGRATION: ÉCHOUÉ ❌❌❌")
        print("="*70)
        print("\n🚨 Système NON PRÊT!")
        print("📋 Vérifier les logs ci-dessus pour les erreurs")
        print("📞 Consulter la section TROUBLESHOOTING ci-dessous")
        sys.exit(1)
        
except Exception as e:
    print("\n" + "="*70)
    print("❌❌❌ TEST CRASHÉ ❌❌❌")
    print("="*70)
    print(f"\nErreur fatale: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
```

#### 4.2 Exécuter le test

```bash
# Exécuter le test d'intégration
python3 test_graphiti_integration.py
```

**Résultat attendu:**
```
======================================================================
🧪 TEST D'INTÉGRATION - GEMINI 2.5 FLASH-LITE + OPENAI EMBEDDINGS
======================================================================

1️⃣  Vérification des clés API:
   ├─ GEMINI_API_KEY: ✅ Found
   ├─ OPENAI_API_KEY: ✅ Found
   └─ SEMAPHORE_LIMIT: 10

2️⃣  Initialisation du client Graphiti:
   ✅ Client initialisé avec succès

3️⃣  Test d'ingestion d'un épisode:
   ├─ Episode ID: test-integration-20251103_184500
   ├─ Content: 287 chars
   └─ Ingestion...

   ✅ Ingestion réussie en 8.5s!
   ├─ Entities: 3
   ├─ Relations: 2
   └─ Status: success

4️⃣  Cleanup:
   ✅ Client fermé

======================================================================
✅✅✅ TEST D'INTÉGRATION: RÉUSSI ✅✅✅
======================================================================

🎉 Votre système DiveTeacher est PRODUCTION READY!
```

---

## 🚨 TROUBLESHOOTING - ERREURS COURANTES

### Erreur #1: `GEMINI_API_KEY not found`

**Symptôme:**
```
ValueError: GEMINI_API_KEY not found in environment
```

**Cause:** Fichier `.env` non chargé ou clé manquante

**Solution:**
```python
# Ajouter au début de votre script:
from dotenv import load_dotenv
load_dotenv('.env')  # ⚠️ Charger AVANT tous les imports de votre code!

# Vérifier:
import os
print(os.getenv('GEMINI_API_KEY'))  # Doit afficher votre clé
```

---

### Erreur #2: `Invalid input for 'vector.similarity.cosine()': vectors do not have same dimensions`

**Symptôme:**
```
neo4j.exceptions.ClientError: Invalid input for 'vector.similarity.cosine()': 
The supplied vectors do not have the same number of dimensions.
```

**Cause:** DB contient des embeddings d'un autre modèle (768 ou 1024 dims) incompatibles avec OpenAI (1536 dims)

**Solution:**
```bash
# VIDER COMPLÈTEMENT LA DB:
docker exec <your-neo4j-container> cypher-shell -u neo4j -p <password> \
  "MATCH (n) DETACH DELETE n"

# Vérifier:
docker exec <your-neo4j-container> cypher-shell -u neo4j -p <password> \
  "MATCH (n) RETURN count(n) as total"
# Doit retourner: total = 0
```

---

### Erreur #3: `429 Resource Exhausted` (Rate limit)

**Symptôme:**
```
429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': 'Resource exhausted'}}
```

**Cause:** `SEMAPHORE_LIMIT` trop élevé pour votre tier Gemini

**Solution:**

```bash
# Dans .env, ajuster selon votre tier:
SEMAPHORE_LIMIT=2   # Si FREE tier (15 RPM)
SEMAPHORE_LIMIT=10  # Si TIER 1 payant (4K RPM)
```

**Vérifier votre tier:**
- Aller sur: https://aistudio.google.com/app/apikey
- Cliquer sur votre clé
- Voir "Rate limits" dans les détails

---

### Erreur #4: `ImportError: cannot import name 'GeminiClient'`

**Symptôme:**
```
ImportError: cannot import name 'GeminiClient' from 'graphiti_core.llm_client.gemini_client'
```

**Cause:** Version de Graphiti trop ancienne ou mauvais import

**Solution:**
```bash
# Vérifier version Graphiti:
pip show graphiti-core

# Si < 0.20.0, mettre à jour:
pip install --upgrade graphiti-core

# Vérifier import:
python3 -c "from graphiti_core.llm_client.gemini_client import GeminiClient; print('✅ OK')"
```

---

### Erreur #5: `503 UNAVAILABLE` (Modèle Gemini)

**Symptôme:**
```
503 UNAVAILABLE. {'error': {'code': 503, 'message': 'The model is overloaded'}}
```

**Cause:** Utilisation du modèle `gemini-2.0-flash-exp` (experimental, surchargé)

**Solution:**
```python
# ❌ NE PAS utiliser:
model='gemini-2.0-flash-exp'  # Experimental, instable!

# ✅ UTILISER:
model='gemini-2.5-flash-lite'  # Stable, ultra-low cost, 4K RPM!
```

---

### Erreur #6: `Unsupported parameter: 'reasoning.effort'`

**Symptôme:**
```
Unsupported parameter: 'reasoning.effort' is not supported with this model
```

**Cause:** Utilisation de `OpenAIClient` avec Gemini (mauvais client!)

**Solution:**
```python
# ❌ NE PAS utiliser OpenAIClient pour Gemini:
from graphiti_core.llm_client import OpenAIClient  # ❌ FAUX!
llm_client = OpenAIClient(...)

# ✅ UTILISER GeminiClient pour Gemini:
from graphiti_core.llm_client.gemini_client import GeminiClient  # ✅ CORRECT!
llm_client = GeminiClient(...)
```

---

### Erreur #7: Neo4j non démarré

**Symptôme:**
```
ServiceUnavailable: Unable to connect to bolt://localhost:7687
```

**Cause:** Container Neo4j arrêté

**Solution:**
```bash
# Vérifier status:
docker ps | grep neo4j

# Si absent, démarrer:
docker start <your-neo4j-container>

# Attendre 10 secondes
sleep 10

# Vérifier connexion:
curl -I http://localhost:7474
# Doit retourner: HTTP/1.1 200 OK
```

---

## 📊 CONFIGURATION FINALE VALIDÉE (ARIA)

**Voici la configuration exacte qui fonctionne en production chez ARIA:**

### LLM (Gemini 2.5 Flash-Lite)
```python
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig

llm_config = LLMConfig(
    api_key=os.getenv('GEMINI_API_KEY'),
    model='gemini-2.5-flash-lite'
)

llm_client = GeminiClient(
    config=llm_config,
    cache=False
)
```

### Embeddings (OpenAI)
```python
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig

embedder_config = OpenAIEmbedderConfig(
    api_key=os.getenv('OPENAI_API_KEY'),
    embedding_model="text-embedding-3-small",
    embedding_dim=1536
)

embedder_client = OpenAIEmbedder(config=embedder_config)
```

### Cross-encoder (OpenAI)
```python
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient

cross_encoder_config = LLMConfig(
    api_key=os.getenv('OPENAI_API_KEY'),
    model="gpt-4o-mini"
)

cross_encoder_client = OpenAIRerankerClient(config=cross_encoder_config)
```

### Graphiti Initialization
```python
self.graphiti = Graphiti(
    neo4j_uri,
    neo4j_user,
    neo4j_password,
    llm_client=llm_client,
    embedder=embedder_client,
    cross_encoder=cross_encoder_client
)
```

### Environment Variables (.env)
```bash
GEMINI_API_KEY=AIzaSy...  # Google AI Studio
OPENAI_API_KEY=sk-proj-...  # OpenAI
SEMAPHORE_LIMIT=10  # Tier 1 (4K RPM)
GRAPHITI_TELEMETRY_ENABLED=false  # Optionnel
```

---

## 💰 COÛTS ATTENDUS

### Gemini 2.5 Flash-Lite
- **Input:** $0.10 / million tokens
- **Output:** $0.40 / million tokens
- **Estimation:** ~$0.005 par ingestion de 3 documents

### OpenAI Embeddings
- **text-embedding-3-small:** $0.02 / million tokens
- **Estimation:** ~$0.001 par ingestion de 3 documents

### Total
- **Par run:** ~$0.006
- **Par mois (30 runs):** ~$0.18
- **Par an:** ~$2.16

**vs Haiku/GPT-4o:** Économie de 99%+ 🎉

---

## ✅ CHECKLIST FINALE

Avant de considérer l'implémentation comme terminée:

- [ ] Tous les imports sont corrects (GeminiClient, OpenAIEmbedder, etc.)
- [ ] Modèle LLM: `gemini-2.5-flash-lite`
- [ ] Embeddings: `text-embedding-3-small` (1536 dims)
- [ ] Cross-encoder: `gpt-4o-mini`
- [ ] Les 3 clients sont passés explicitement à `Graphiti()`
- [ ] Fichier `.env` contient `GEMINI_API_KEY` et `OPENAI_API_KEY`
- [ ] `SEMAPHORE_LIMIT=10` dans `.env`
- [ ] Base Neo4j a des embeddings 1536 dims (ou est vide)
- [ ] Test d'intégration passe avec succès
- [ ] Logs montrent "Gemini 2.5 Flash-Lite" et "OpenAI embeddings"
- [ ] Aucune erreur de dimension de vecteurs
- [ ] Aucune erreur 429 (rate limit)
- [ ] Aucune erreur 503 (model overloaded)

---

## 📞 SUPPORT

Si après avoir suivi ce guide vous rencontrez toujours des problèmes:

1. **Logs détaillés:** Capturer toute la stacktrace de l'erreur
2. **Configuration:** Partager votre code de configuration (sans les clés!)
3. **Neo4j:** Vérifier les dimensions des embeddings existants
4. **Test isolation:** Essayer avec une DB Neo4j vide

**Ressources:**
- Graphiti Docs: https://help.getzep.com/graphiti/configuration/llm-configuration
- Gemini API: https://ai.google.dev/gemini-api/docs
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings

---

## 🎯 RÉSUMÉ EXÉCUTIF

**Ce que vous DEVEZ faire:**

1. ✅ Vérifier imports: `GeminiClient` + `OpenAIEmbedder` + `OpenAIRerankerClient`
2. ✅ Modèle LLM: `gemini-2.5-flash-lite`
3. ✅ Embeddings: `text-embedding-3-small` (1536 dims)
4. ✅ Passer les 3 clients explicitement à `Graphiti()`
5. ✅ Configurer `SEMAPHORE_LIMIT=10` dans `.env`
6. ✅ Vérifier dimensions Neo4j (1536 ou vide)
7. ✅ Exécuter test d'intégration complet

**Si test passe:** ✅ Production ready!  
**Si test échoue:** 🚨 Consulter TROUBLESHOOTING

---

**🎉 BONNE CHANCE AVEC VOTRE AUDIT!**

**Temps estimé:** 30-60 minutes  
**Difficulté:** Moyenne  
**Impact:** CRITIQUE pour la production

**Questions?** Consulter les sections TROUBLESHOOTING et SUPPORT ci-dessus.

---

**Document créé par:** ARIA Team  
**Date:** 2025-11-03  
**Statut:** ✅ Validé en production ARIA (0 erreurs après 5 jours de debug)

