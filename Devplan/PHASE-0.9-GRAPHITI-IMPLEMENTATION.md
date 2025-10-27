# 🔗 Phase 0.9 - Graphiti Knowledge Graph Implementation

> **Objectif:** Finaliser l'intégration Graphiti avec Docling et Neo4j pour un knowledge graph temporel fonctionnel  
> **Durée Estimée:** 3-4 heures (réduite grâce à OpenAI)  
> **Priorité:** CRITIQUE (bloque Phase 1)  
> **Date:** Octobre 27, 2025

> **🎯 Architecture LLM:**  
> - **Graphiti (Knowledge Graph):** OpenAI **GPT-5-nano** + text-embedding-3-small  
> - **RAG (User Queries):** Ollama Mistral 7b (local)  
> - **Séparation totale:** Pas de mélange entre les deux stacks!  
> - **Performance:** 2M tokens/min (rate limit maximal OpenAI) - Ultra rapide!

---

## 📋 Table des Matières

- [Vue d'Ensemble](#vue-densemble)
- [Audit de l'Implémentation Actuelle](#audit-de-limplémentation-actuelle)
- [Problèmes Identifiés](#problèmes-identifiés)
- [Architecture Cible](#architecture-cible)
- [Plan d'Implémentation Détaillé](#plan-dimplémentation-détaillé)
- [Tests de Validation](#tests-de-validation)
- [Métriques de Succès](#métriques-de-succès)

---

## Vue d'Ensemble

### Contexte

**État Actuel (Phase 0.8 Complete):**
- ✅ Docling 2.5.1 + HierarchicalChunker opérationnel (436 chunks pour 35 pages)
- ✅ Neo4j 5.25.1 + RAG indexes (fulltext, entity, hybrid search)
- ⚠️  Graphiti 0.3.7 partiellement intégré (ingestion OK, recherche non optimale)

**Objectif Phase 0.9:**
- 🎯 Mise à jour Graphiti vers version 0.17.x
- 🎯 Configuration LLM **OpenAI GPT-5-nano** pour Graphiti (extraction entities/relations + embeddings)
  - ⚡ **2M tokens/min** - Le plus rapide et moins cher disponible!
- 🎯 **Mistral 7b (Ollama)** reste pour RAG/User queries (pas de mélange!)
- 🎯 Utilisation native `graphiti.search()` pour RAG
- 🎯 Optimisation community building (périodique, pas à chaque upload)
- 🎯 Tests E2E complets: PDF → Docling → Graphiti → Neo4j → RAG Query

### Valeur Ajoutée

**Sans Graphiti optimisé:**
- Recherche limitée à full-text (BM25) + regex entities
- Pas de relations sémantiques entre concepts
- Pas de résolution temporelle des contradictions

**Avec Graphiti complet:**
- ✅ Extraction automatique entités + relations via LLM
- ✅ Recherche hybride (semantic + BM25 + graph traversal)
- ✅ Knowledge graph évolutif (ajout incrémental sans recomputation)
- ✅ Temporal awareness (valid_at, invalid_at pour contradictions)

---

## Audit de l'Implémentation Actuelle

### ✅ Points Forts

**1. Architecture Singleton Correcte**
```python
# backend/app/integrations/graphiti.py
_graphiti_client: Optional[Graphiti] = None
_indices_built: bool = False

async def get_graphiti_client() -> Graphiti:
    global _graphiti_client, _indices_built
    
    if _graphiti_client is None:
        _graphiti_client = Graphiti(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )
    
    if not _indices_built:
        await _graphiti_client.build_indices_and_constraints()
        _indices_built = True
    
    return _graphiti_client
```
✅ **Correct:** Initialisation unique, indices built une seule fois

**2. Paramètres `add_episode()` Conformes**
```python
await client.add_episode(
    name=f"{metadata['filename']} - Chunk {chunk_index}",
    episode_body=chunk_text,
    source=EpisodeType.text,  # ✅ 'source' pas 'episode_type'
    source_description=f"Document: {metadata['filename']}...",
    reference_time=datetime.now(timezone.utc),  # ✅ datetime object
)
```
✅ **Correct:** Aligné avec API Graphiti 0.17.x

**3. Intégration Pipeline**
```python
# backend/app/core/processor.py
await ingest_chunks_to_graph(chunks=chunks, metadata=enriched_metadata)
```
✅ **Correct:** Chunking → Graphiti ingestion

**4. Cleanup Proper**
```python
# backend/app/main.py
await close_graphiti_client()
```
✅ **Correct:** Fermeture propre dans shutdown event

### ❌ Problèmes Identifiés

#### Problème 1: Version Graphiti Obsolète ⚠️ CRITIQUE

**État Actuel:**
```txt
# backend/requirements.txt
graphiti-core==0.3.7
```

**Conséquence:**
- API instable (version très ancienne, 0.17.x est la stable actuelle)
- Fonctionnalités manquantes (SearchConfig, reranking, custom entities)
- Bugs potentiels corrigés dans versions récentes

**Solution:**
```txt
graphiti-core==0.17.0  # Version stable octobre 2025
```

---

#### Problème 2: LLM Non Configuré pour Graphiti ⚠️ BLOQUANT

**État Actuel:**
```python
# backend/app/integrations/graphiti.py
_graphiti_client = Graphiti(
    uri=settings.NEO4J_URI,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD
    # ❌ Pas de llm_client, embedder, cross_encoder
)
```

**Conséquence:**
- Graphiti utilise OpenAI par défaut (appels API qui échouent si pas de clé configurée)
- Pas d'extraction d'entités/relations fonctionnelle
- Ingestion échoue silencieusement ou avec erreurs API

**Solution: Utiliser OpenAI GPT-5-nano pour Graphiti (OPTIMAL)**

✅ **Architecture Choisie:**
- **Graphiti:** OpenAI **GPT-5-nano** (extraction entities/relations) + text-embedding-3-small (embeddings)
- **RAG/User:** Mistral 7b sur Ollama (queries utilisateur)
- **Séparation claire:** Pas de mélange entre les deux!

**Pourquoi GPT-5-nano pour Graphiti?**
- ✅ **Performance maximale:** 2M tokens/min (rate limit le plus élevé disponible)
- ✅ **Coût minimal:** Le moins cher de la gamme OpenAI
- ✅ **Qualité extraction:** Supérieure à Mistral 7b pour entity extraction
- ✅ Embeddings optimisés (text-embedding-3-small, 1536 dim)
- ✅ Latence ultra-faible (~0.5-1s par chunk avec 2M TPM)
- ✅ Support natif Graphiti (pas besoin d'adapter)

```python
from graphiti_core import Graphiti

# Configuration simple: Graphiti utilise OpenAI par défaut
_graphiti_client = Graphiti(
    uri=settings.NEO4J_URI,
    user=settings.NEO4J_USER,
    password=settings.NEO4J_PASSWORD
    # ✅ Pas besoin de llm_client custom: utilise OpenAI nativement
    # Nécessite juste OPENAI_API_KEY dans settings
)
```

---

#### Problème 3: Recherche Graphiti Native Non Utilisée ⚠️ SOUS-OPTIMAL

**État Actuel:**
```python
# backend/app/integrations/neo4j.py
def query_context_fulltext(question: str):
    # ❌ Queries Cypher manuelles
    records = self.driver.execute_query(
        "CALL db.index.fulltext.queryNodes('episode_content', $search_text)..."
    )
```

**Conséquence:**
- On n'utilise pas les capacités de recherche hybride de Graphiti (semantic + BM25 + RRF)
- Pas de reranking intelligent
- Queries manuelles fragiles et difficiles à maintenir

**Solution:**
Utiliser `graphiti.search()` directement:
```python
# backend/app/integrations/graphiti.py
async def search_knowledge_graph(
    query: str,
    num_results: int = 10,
    search_config: Optional[SearchConfig] = None
) -> List[EntityEdge]:
    """
    Search knowledge graph using Graphiti's native hybrid search
    
    Returns:
        List of EntityEdges (facts) with source/target entities
    """
    client = await get_graphiti_client()
    
    results = await client.search(
        query=query,
        num_results=num_results,
        search_config=search_config or EDGE_HYBRID_SEARCH_RRF
    )
    
    return results
```

---

#### Problème 4: `build_communities()` Appelé Trop Fréquemment ⚠️ PERFORMANCE

**État Actuel:**
```python
# backend/app/integrations/graphiti.py (ligne 136-143)
if successful > 0:
    try:
        logger.info("🏘️  Building communities...")
        await client.build_communities()  # ❌ Après CHAQUE upload!
        logger.info("✅ Communities built")
    except Exception as e:
        logger.warning(f"⚠️  Community building failed: {e}")
```

**Conséquence:**
- Coût computationnel élevé (Louvain algorithm sur tout le graphe)
- Ralentit chaque upload (436 chunks → attente community building)
- Pas nécessaire après chaque document (communautés évoluent lentement)

**Solution:**
Community building périodique:
```python
# 1. Supprimer de ingest_chunks_to_graph()

# 2. Ajouter endpoint dédié
@router.post("/graph/build-communities")
async def build_communities_endpoint():
    """
    Build communities (call manually or via cron)
    
    Frequency: 
    - Dev: After every 5-10 documents
    - Prod: Daily cron job
    """
    client = await get_graphiti_client()
    await client.build_communities()
    return {"status": "completed"}
```

---

#### Problème 5: Pas de `group_ids` ⚠️ MULTI-TENANT

**État Actuel:**
```python
await client.add_episode(
    name=f"{metadata['filename']} - Chunk {chunk_index}",
    episode_body=chunk_text,
    source=EpisodeType.text,
    source_description=f"...",
    reference_time=reference_time,
    # ❌ Pas de group_id
)
```

**Conséquence:**
- Tous les documents dans le même namespace
- Phase 1+ (multi-user): Impossible d'isoler données par utilisateur
- Queries ramènent données de tous les users

**Solution:**
```python
await client.add_episode(
    name=f"{metadata['filename']} - Chunk {chunk_index}",
    episode_body=chunk_text,
    source=EpisodeType.text,
    source_description=f"...",
    reference_time=reference_time,
    group_id=metadata.get("user_id", "default")  # ✅ Isolation multi-tenant
)
```

---

#### Problème 6: Conflit Potentiel Indexes Neo4j ⚠️ STABILITÉ

**État Actuel:**
```python
# backend/app/integrations/neo4j_indexes.py
create_rag_indexes(driver)
# Crée: episode_content (FULLTEXT), entity_name_idx, episode_date_idx

# backend/app/integrations/graphiti.py
await graphiti.build_indices_and_constraints()
# Crée aussi des indices (uuid, embeddings, etc.)
```

**Conséquence:**
- Risque de doublons ou conflits
- Ordre de création important

**Solution:**
```python
# 1. Graphiti indices FIRST (au startup)
await graphiti.build_indices_and_constraints()

# 2. PUIS custom RAG indices (si nécessaire)
# Note: Graphiti crée déjà des indices vectoriels optimaux
# Nos indices custom peuvent être redondants
```

---

## Architecture Cible

### 🎯 Séparation LLMs: OpenAI vs Ollama

**IMPORTANT: Pas de mélange entre les deux stacks!**

```
┌─────────────────────────────────────────────────────────────┐
│                    GRAPHITI STACK (OpenAI)                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PDF Upload → Docling → Chunks                               │
│              ↓                                                │
│         Graphiti Ingestion                                    │
│              ↓                                                │
│    ┌──────────────────────────────────────┐                  │
│    │ OpenAI GPT-5-nano (2M TPM)         │                  │
│    │ - Entity extraction                  │                  │
│    │ - Relation detection                 │                  │
│    │ - Entity resolution                  │                  │
│    └──────────────────────────────────────┘                  │
│              +                                                │
│    ┌──────────────────────────────────────┐                  │
│    │ OpenAI text-embedding-3-small        │                  │
│    │ - Episode embeddings (1536 dim)     │                  │
│    │ - Entity name embeddings             │                  │
│    │ - Fact embeddings                    │                  │
│    └──────────────────────────────────────┘                  │
│              ↓                                                │
│         Neo4j Storage                                         │
│    (Episodes, Entities, Relations)                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     RAG STACK (Ollama)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  User Question                                                │
│       ↓                                                       │
│  Graphiti Hybrid Search (utilise embeddings OpenAI)          │
│       ↓                                                       │
│  Context Retrieved                                            │
│       ↓                                                       │
│  Build RAG Prompt                                             │
│       ↓                                                       │
│  ┌──────────────────────────────────────┐                    │
│  │ Ollama Mistral 7b                    │                    │
│  │ - Answer generation                  │                    │
│  │ - User conversation                  │                    │
│  └──────────────────────────────────────┘                    │
│       ↓                                                       │
│  Grounded Answer                                              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Pourquoi cette séparation?**
- ✅ **Graphiti = OpenAI GPT-5-nano:** Qualité + Vitesse (2M TPM) + Coût minimal
- ✅ **RAG = Ollama:** Coût 0€ pour queries utilisateur, confidentialité, latence acceptable
- ✅ **Aucun mélange:** Chaque stack utilise son propre LLM, pas de confusion
- ✅ **Scalabilité:** Graphiti ingestion ultra-rapide (2M TPM) vs RAG queries (temps réel) séparés

**Performance:**
- **Graphiti:** 436 chunks ingérés en ~20-30s (vs 5-10 min avec Ollama)
- **Coût:** ~$0.50-1.00 par document 35 pages (GPT-5-nano = le moins cher)

**Coûts Estimés:**
- **Graphiti (OpenAI GPT-5-nano):** ~$0.50-1.00 par document 35 pages
- **RAG (Ollama Mistral):** 0€ (local)

### Schéma Neo4j (Géré par Graphiti)

```
Nodes:
  Episode {
    uuid: string (PK)
    name: string                        # "Niveau 4 GP.pdf - Chunk 12"
    content: string (indexed fulltext)  # Texte du chunk
    source: string                      # "text", "json", "message"
    source_description: string          # "Document: Niveau 4 GP.pdf, Chunk 12/436"
    created_at: datetime                # Système
    valid_at: datetime                  # Référence temporelle
    group_id: string (nullable)         # "user_123" pour isolation
  }

  Entity {
    uuid: string (PK)
    name: string (indexed)              # "Niveau 4", "Prérequis", "FFESSM"
    summary: string                     # Description générée par LLM
    entity_type: string                 # Type détecté par LLM
    name_embedding: vector              # Pour recherche sémantique
    group_id: string (nullable)
  }

  Community {
    uuid: string (PK)
    name: string
    summary: string                     # Résumé de la communauté
  }

Relationships:
  (Episode)-[:HAS_ENTITY]->(Entity)
    Lien bidirectionnel: Episode → Entities extraites

  (Entity)-[:RELATES_TO {fact: string, valid_at: datetime, invalid_at: datetime}]->(Entity)
    Relations sémantiques avec temporal awareness

  (Entity)-[:MEMBER_OF]->(Community)
    Groupement d'entités similaires
```

### Flux de Données Complet

```
1. UPLOAD PDF
   ↓
2. DOCLING CONVERSION (280s pour 35 pages)
   DoclingDocument {pages, tables, pictures}
   ↓
3. HIERARCHICAL CHUNKING (5s)
   436 chunks sémantiques (avg 127 tokens)
   ↓
4. GRAPHITI INGESTION (30-60s pour 436 chunks)
   Pour chaque chunk:
   ├─ Créer Episode node
   ├─ LLM: Extraire entities (ex: "Niveau 4", "Prérequis", "MFT")
   ├─ LLM: Détecter relations (ex: "Niveau 4" -[REQUIRES]-> "Niveau 3")
   ├─ Résolution entities (dédoublonnage)
   └─ Détection contradictions temporelles
   ↓
5. NEO4J STORAGE
   Episodes (436) + Entities (~50-100) + Relations (~100-200)
   ↓
6. COMMUNITY BUILDING (périodique, pas à chaque upload)
   Louvain algorithm → groupes d'entités liées
   ↓
7. RAG QUERY
   User question
   ↓
   Graphiti Hybrid Search (semantic + BM25 + RRF)
   ├─ Search Episodes (chunks texte)
   ├─ Search Entities (concepts extraits)
   └─ Graph traversal (relations)
   ↓
   Top 10 results (EntityEdges avec facts)
   ↓
   Build RAG Prompt (context + question)
   ↓
   Ollama LLM Generation
   ↓
   Grounded Answer avec citations
```

---

## Plan d'Implémentation Détaillé

### Phase A: Préparation Environnement (15 min)

#### A.1 - Vérifier Clé OpenAI ✅ PRÉREQUIS

**Objectif:** S'assurer que la clé OpenAI est configurée pour Graphiti

**Vérification:**
```bash
# Vérifier que OPENAI_API_KEY est dans .env
grep "OPENAI_API_KEY" .env

# Output attendu: OPENAI_API_KEY=sk-proj-SDuU8A9vNJEf2i...
```

**Si absente, ajouter dans `.env`:**
```bash
# OpenAI API (for Graphiti knowledge graph)
OPENAI_API_KEY=sk-proj-SDuU8A9vNJEf2i....
```

**Test API:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-proj-SDuU8A9vNJEf2i...." | jq '.data[] | select(.id | contains("gpt-5-nano"))'

# Output attendu: Modèle gpt-5-nano disponible
```

**Critères de Succès:**
- ✅ `OPENAI_API_KEY` présente dans `.env`
- ✅ API OpenAI répond (200 OK)
- ✅ Modèle `gpt-5-nano` accessible
- ✅ Rate limit: 2M tokens/min confirmé

---

#### A.2 - Mettre à Jour Graphiti Version ⚠️ CRITIQUE

**Fichier:** `backend/requirements.txt`

**Changement:**
```diff
- graphiti-core==0.3.7
+ graphiti-core==0.17.0
```

**Rebuild Docker:**
```bash
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker compose -f docker/docker-compose.dev.yml build backend --no-cache
docker compose -f docker/docker-compose.dev.yml up -d backend
```

**Vérification:**
```bash
docker exec rag-backend python -c "import graphiti_core; print(graphiti_core.__version__)"
# Output attendu: 0.17.0
```

---

#### A.3 - Configurer Variables Environnement

**Fichier:** `backend/app/core/config.py`

**Vérifier que `OPENAI_API_KEY` est chargée:**
```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # OpenAI Configuration (pour Graphiti uniquement)
    OPENAI_API_KEY: Optional[str] = None  # ✅ Déjà présent normalement
    OPENAI_MODEL: str = "gpt-4o"          # ✅ Déjà présent
    
    # Note: Pas besoin de variables spécifiques Graphiti
    # Graphiti utilise automatiquement OPENAI_API_KEY si disponible
```

**Pas de modifications nécessaires dans `.env`** - Clé déjà présente!

---

### Phase B: Configuration Graphiti Client (1h)

#### B.1 - Refactor `graphiti.py` avec Configuration OpenAI

**Fichier:** `backend/app/integrations/graphiti.py`

**Changements Majeurs:**

```python
"""
Graphiti Integration avec OpenAI GPT-4o-mini

Architecture:
- Graphiti: OpenAI GPT-4o-mini (entity extraction) + text-embedding-3-small (embeddings)
- RAG/User: Mistral 7b sur Ollama (séparé, pas de mélange!)
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.search.search_config_recipes import EDGE_HYBRID_SEARCH_RRF
from graphiti_core.search.search_config import SearchConfig

from app.core.config import settings

logger = logging.getLogger('diveteacher.graphiti')


# Global Graphiti client (singleton pattern)
_graphiti_client: Optional[Graphiti] = None
_indices_built: bool = False


async def get_graphiti_client() -> Graphiti:
    """
    Get or create Graphiti client singleton avec OpenAI
    
    Returns:
        Initialized Graphiti client
        
    Note:
        - Build indices only once on first call
        - Reuse same client for all operations
        - Uses OpenAI by default (GPT-4o-mini + text-embedding-3-small)
        - Requires OPENAI_API_KEY in environment
    """
    global _graphiti_client, _indices_built
    
    if _graphiti_client is None:
        if not settings.GRAPHITI_ENABLED:
            raise RuntimeError("Graphiti is disabled in settings")
        
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY required for Graphiti (not found in settings)")
        
        logger.info("🔧 Initializing Graphiti client with OpenAI...")
        
        # Graphiti utilise OpenAI par défaut
        # Pas besoin de llm_client custom!
        _graphiti_client = Graphiti(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
            # ✅ Graphiti charge automatiquement:
            #    - LLM: gpt-4o-mini (ou OPENAI_MODEL si défini)
            #    - Embedder: text-embedding-3-small
            #    - Via OPENAI_API_KEY dans environment
        )
        
        logger.info("✅ Graphiti client initialized: OpenAI GPT-5-nano (2M TPM) + text-embedding-3-small")
    
    # Build indices and constraints (only once)
    if not _indices_built:
        logger.info("🔨 Building Neo4j indices and constraints (Graphiti)...")
        await _graphiti_client.build_indices_and_constraints()
        _indices_built = True
        logger.info("✅ Graphiti indices and constraints built")
    
    return _graphiti_client


async def close_graphiti_client():
    """Close Graphiti client connection"""
    global _graphiti_client, _indices_built
    
    if _graphiti_client is not None:
        logger.info("🔌 Closing Graphiti connection...")
        await _graphiti_client.close()
        _graphiti_client = None
        _indices_built = False
        logger.info("✅ Graphiti connection closed")


async def ingest_chunks_to_graph(
    chunks: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> None:
    """
    Ingest semantic chunks to Graphiti knowledge graph
    
    Args:
        chunks: List of chunks from HierarchicalChunker
        metadata: Document-level metadata
        
    Raises:
        RuntimeError: If Graphiti is disabled
        
    Note:
        - Each chunk is ingested as an "episode" in Graphiti
        - Graphiti automatically extracts entities and relationships
        - Failed chunks are logged but don't block the pipeline
        - Community building is NOT called here (too expensive, call periodically)
    """
    if not settings.GRAPHITI_ENABLED:
        logger.warning("⚠️  Graphiti disabled - skipping ingestion")
        return
    
    logger.info(f"📥 Ingesting {len(chunks)} chunks to Graphiti/Neo4j")
    
    client = await get_graphiti_client()
    
    successful = 0
    failed = 0
    
    # Determine group_id for multi-tenant isolation
    group_id = metadata.get("user_id", "default")  # ✅ Phase 1+: real user IDs
    
    # Pour chaque chunk, appeler Graphiti
    for chunk in chunks:
        chunk_text = chunk["text"]
        chunk_index = chunk["index"]
        
        try:
            # IMPORTANT: Utiliser datetime avec timezone UTC
            reference_time = datetime.now(timezone.utc)
            
            # Ingest chunk comme "episode" dans Graphiti
            await client.add_episode(
                name=f"{metadata['filename']} - Chunk {chunk_index}",
                episode_body=chunk_text,
                source=EpisodeType.text,
                source_description=f"Document: {metadata['filename']}, "
                                 f"Chunk {chunk_index}/{chunk['metadata']['total_chunks']}",
                reference_time=reference_time,
                group_id=group_id,  # ✅ Multi-tenant isolation
                # TODO Phase 1+: Ajouter entity_types et edge_types custom
            )
            successful += 1
            
            if (chunk_index + 1) % 10 == 0:
                logger.info(f"   Processed {chunk_index + 1}/{len(chunks)} chunks...")
            
        except Exception as e:
            logger.error(f"Failed to ingest chunk {chunk_index}: {e}", exc_info=True)
            failed += 1
            # Continue avec chunks suivants (ne pas fail tout le pipeline)
    
    # Log résultats
    if failed > 0:
        logger.warning(f"⚠️  Ingestion partial: {successful} OK, {failed} failed")
    else:
        logger.info(f"✅ Successfully ingested {successful} chunks")
    
    # ❌ NE PAS appeler build_communities() ici (trop coûteux)
    # À appeler manuellement via endpoint dédié ou cron job


async def search_knowledge_graph(
    query: str,
    num_results: int = 10,
    group_ids: Optional[List[str]] = None,
    search_config: Optional[SearchConfig] = None
) -> List[Dict[str, Any]]:
    """
    Search knowledge graph using Graphiti's native hybrid search
    
    Args:
        query: User's search query
        num_results: Number of results to return
        group_ids: Filter by group_ids (multi-tenant)
        search_config: Custom search configuration (default: EDGE_HYBRID_SEARCH_RRF)
        
    Returns:
        List of dicts with fact, source_entity, target_entity, score, etc.
        
    Note:
        - Uses Graphiti's hybrid search (semantic + BM25 + RRF)
        - Returns EntityEdges (facts/relations) not just Episodes
        - Much more powerful than manual Neo4j queries
    """
    if not settings.GRAPHITI_ENABLED:
        logger.warning("⚠️  Graphiti disabled - returning empty results")
        return []
    
    logger.info(f"🔍 Graphiti search: '{query}' (num_results={num_results})")
    
    client = await get_graphiti_client()
    
    try:
        # Use Graphiti's native search (hybrid: semantic + BM25 + RRF)
        edge_results = await client.search(
            query=query,
            num_results=num_results,
            group_ids=group_ids,
            search_config=search_config or EDGE_HYBRID_SEARCH_RRF
        )
        
        # Format results pour RAG pipeline
        formatted_results = []
        for edge in edge_results:
            formatted_results.append({
                "fact": edge.fact,
                "source_entity": edge.source_node_uuid,
                "target_entity": edge.target_node_uuid,
                "relation_type": edge.name,
                "valid_at": edge.valid_at.isoformat() if edge.valid_at else None,
                "invalid_at": edge.invalid_at.isoformat() if edge.invalid_at else None,
                "episodes": edge.episodes,  # Source episodes UUIDs
                # Note: Pour récupérer noms entities, faire requête Neo4j séparée
            })
        
        logger.info(f"✅ Graphiti search returned {len(formatted_results)} results")
        return formatted_results
        
    except Exception as e:
        logger.error(f"❌ Graphiti search failed: {e}", exc_info=True)
        return []


async def build_communities() -> bool:
    """
    Build communities in knowledge graph
    
    Returns:
        True if successful, False otherwise
        
    Note:
        - Expensive operation (Louvain algorithm)
        - Call periodically (not after every upload):
          * Dev: Every 5-10 documents
          * Prod: Daily cron job
    """
    if not settings.GRAPHITI_ENABLED:
        logger.warning("⚠️  Graphiti disabled - skipping community building")
        return False
    
    logger.info("🏘️  Building communities (this may take a while)...")
    
    client = await get_graphiti_client()
    
    try:
        await client.build_communities()
        logger.info("✅ Communities built successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Community building failed: {e}", exc_info=True)
        return False
```

**Changements Clés:**
1. ✅ Configuration OpenAI simple (utilise defaults Graphiti, pas de custom client)
2. ✅ Vérification `OPENAI_API_KEY` présente
3. ✅ Ajout `group_id` pour multi-tenant
4. ✅ Nouvelle fonction `search_knowledge_graph()` utilisant Graphiti nativement
5. ✅ `build_communities()` séparée (pas dans ingestion)
6. ✅ **Séparation claire:** Graphiti = OpenAI, RAG/User = Ollama Mistral

---

#### B.2 - Ajouter Endpoint Community Building

**Fichier:** `backend/app/api/graph.py`

**Ajout:**
```python
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.integrations.neo4j import neo4j_client
from app.integrations.graphiti import build_communities as graphiti_build_communities

router = APIRouter()

# ... existing endpoints ...

@router.post("/graph/build-communities")
async def build_communities_endpoint(background_tasks: BackgroundTasks):
    """
    Build communities in knowledge graph
    
    Note:
        - Runs in background task (async)
        - Expensive operation (minutes for large graphs)
        - Recommended frequency:
          * Dev: After every 5-10 documents
          * Prod: Daily cron job
    """
    
    async def run_community_building():
        success = await graphiti_build_communities()
        if success:
            logger.info("✅ Background community building completed")
        else:
            logger.error("❌ Background community building failed")
    
    background_tasks.add_task(run_community_building)
    
    return JSONResponse(content={
        "status": "started",
        "message": "Community building started in background"
    })


@router.get("/graph/stats")
async def get_graph_stats():
    """
    Get knowledge graph statistics
    
    Returns:
        Graph statistics (node count, relationship count, etc.)
    """
    
    neo4j_client.connect()
    
    # Query pour stats complètes
    query = """
    MATCH (e:Episode)
    WITH count(e) AS episode_count
    MATCH (n:Entity)
    WITH episode_count, count(n) AS entity_count
    MATCH ()-[r:RELATES_TO]->()
    RETURN 
        episode_count,
        entity_count,
        count(r) AS relationship_count
    """
    
    try:
        records, summary, keys = neo4j_client.driver.execute_query(
            query,
            database_=neo4j_client.database
        )
        
        if records:
            data = dict(records[0])
            return JSONResponse(content={
                "episodes": data.get("episode_count", 0),
                "entities": data.get("entity_count", 0),
                "relationships": data.get("relationship_count", 0)
            })
        else:
            return JSONResponse(content={
                "episodes": 0,
                "entities": 0,
                "relationships": 0
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Phase C: Intégration RAG avec Graphiti Search (1h)

#### C.1 - Refactor `rag.py` pour Utiliser Graphiti Search

**Fichier:** `backend/app/core/rag.py`

**Changements:**

```python
"""
RAG (Retrieval-Augmented Generation) Chain avec Graphiti
"""

from typing import AsyncGenerator, List, Dict, Any
from app.core.llm import get_llm
from app.integrations.graphiti import search_knowledge_graph
from app.core.config import settings


async def retrieve_context(
    question: str, 
    top_k: int = None,
    group_ids: List[str] = None
) -> Dict[str, Any]:
    """
    Retrieve relevant context using Graphiti's hybrid search
    
    Args:
        question: User's question
        top_k: Number of results (default: from settings)
        group_ids: Filter by group_ids (multi-tenant)
        
    Returns:
        Dictionary with facts (EntityEdges) from Graphiti
        {
            "facts": List[Dict],  # Relations extraites
            "total": int
        }
        
    Note:
        - Uses Graphiti native search (semantic + BM25 + RRF)
        - Returns EntityEdges (relations) not just text chunks
        - More semantic than pure full-text search
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K
    
    # Graphiti hybrid search
    facts = await search_knowledge_graph(
        query=question,
        num_results=top_k,
        group_ids=group_ids
    )
    
    return {
        "facts": facts,
        "total": len(facts)
    }


def build_rag_prompt(question: str, context: Dict[str, Any]) -> tuple[str, str]:
    """
    Build RAG prompt from question and Graphiti facts
    
    Args:
        question: User's question
        context: Dictionary with "facts" key (from Graphiti search)
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    
    facts = context.get("facts", [])
    
    # Build context string from facts
    context_parts = []
    
    if facts:
        context_parts.append("=== KNOWLEDGE FROM DIVING MANUALS ===\n")
        for idx, fact_data in enumerate(facts, 1):
            fact = fact_data.get("fact", "")
            relation_type = fact_data.get("relation_type", "")
            valid_at = fact_data.get("valid_at", "")
            
            context_parts.append(
                f"[Fact {idx} - {relation_type}]\n"
                f"{fact}\n"
                f"Valid: {valid_at if valid_at else 'Current'}"
            )
    
    context_str = "\n\n".join(context_parts)
    
    # System prompt (DiveTeacher-specific)
    system_prompt = """You are DiveTeacher, an AI assistant specialized in scuba diving education.

CRITICAL RULES:
1. Answer ONLY using information from the provided knowledge facts
2. If context is insufficient, say "I don't have enough information in the diving manuals to answer that question accurately"
3. NEVER make up or infer information not present in the context
4. Cite facts: [Fact 1], [Fact 2] when answering
5. Be concise but thorough
6. Use technical diving terms accurately
7. For FFESSM/SSI procedures, cite exact source material

Your goal: Provide accurate, grounded answers that diving students and instructors can trust for their training and safety."""
    
    # User prompt
    if context_parts:
        user_prompt = f"""Knowledge from diving manuals:

{context_str}

---

Question: {question}

Answer based ONLY on the knowledge above. Cite your facts:"""
    else:
        user_prompt = f"""No relevant knowledge found in diving manuals.

Question: {question}

Please explain you don't have enough information to answer this accurately."""
    
    return system_prompt, user_prompt


async def rag_stream_response(
    question: str, 
    temperature: float = 0.7,
    max_tokens: int = 2000,
    group_ids: List[str] = None
) -> AsyncGenerator[str, None]:
    """
    RAG chain: Retrieve (Graphiti) → Build prompt → Stream LLM response
    
    Args:
        question: User's question
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens to generate
        group_ids: Filter by group_ids (multi-tenant)
        
    Yields:
        Response tokens as they are generated
    """
    
    # Step 1: Retrieve context via Graphiti
    context = await retrieve_context(question, group_ids=group_ids)
    
    # Step 2: Build prompt
    system_prompt, user_prompt = build_rag_prompt(question, context)
    
    # Step 3: Stream LLM response
    llm = get_llm()
    async for token in llm.stream_completion(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    ):
        yield token


async def rag_query(
    question: str, 
    temperature: float = 0.7,
    max_tokens: int = 2000,
    group_ids: List[str] = None
) -> Dict[str, Any]:
    """
    RAG query with full response (non-streaming)
    
    Args:
        question: User's question
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens to generate
        group_ids: Filter by group_ids (multi-tenant)
        
    Returns:
        Dictionary with answer, context, and metadata
    """
    
    # Retrieve context
    context = await retrieve_context(question, group_ids=group_ids)
    
    # Build prompt
    system_prompt, user_prompt = build_rag_prompt(question, context)
    
    # Get LLM response
    llm = get_llm()
    full_response = ""
    async for token in llm.stream_completion(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    ):
        full_response += token
    
    return {
        "question": question,
        "answer": full_response,
        "context": context,
        "num_sources": len(context.get("facts", []))
    }
```

**Changements Clés:**
1. ✅ Utilise `search_knowledge_graph()` au lieu de Neo4j direct
2. ✅ Contexte basé sur "facts" (EntityEdges) pas juste chunks
3. ✅ Support `group_ids` pour multi-tenant
4. ✅ Prompt adapté aux facts Graphiti

---

#### C.2 - Déprécier (mais garder) Anciennes Queries Neo4j

**Fichier:** `backend/app/integrations/neo4j.py`

**Ajout en haut du fichier:**
```python
"""
Neo4j Database Client

⚠️  DEPRECATED: Direct Neo4j queries for RAG
    → Use Graphiti search instead (backend/app/integrations/graphiti.py)
    
This client is kept for:
- Graph stats endpoints
- Direct Cypher queries (debugging)
- Fallback if Graphiti unavailable

For RAG queries, use: graphiti.search_knowledge_graph()
"""
```

---

### Phase D: Tests de Validation (1.5h)

#### D.1 - Test Unitaire: Graphiti Client Initialization

**Fichier:** `backend/tests/test_graphiti_init.py` (NOUVEAU)

```python
"""
Test Graphiti Client Initialization avec Ollama
"""
import pytest
import asyncio
from app.integrations.graphiti import get_graphiti_client, close_graphiti_client
from app.core.config import settings


@pytest.mark.asyncio
async def test_graphiti_client_singleton():
    """Test singleton pattern"""
    client1 = await get_graphiti_client()
    client2 = await get_graphiti_client()
    
    assert client1 is client2, "Should return same instance"
    
    await close_graphiti_client()


@pytest.mark.asyncio
async def test_graphiti_ollama_config():
    """Test Ollama LLM configuration"""
    client = await get_graphiti_client()
    
    # Vérifier que le client est bien configuré
    assert client.llm_client is not None, "LLM client should be configured"
    assert client.embedder is not None, "Embedder should be configured"
    
    await close_graphiti_client()


@pytest.mark.asyncio
async def test_graphiti_indices_built():
    """Test that indices are built only once"""
    from app.integrations.graphiti import _indices_built
    
    # Reset
    global _indices_built
    _indices_built = False
    
    # First call should build indices
    await get_graphiti_client()
    assert _indices_built == True
    
    await close_graphiti_client()
```

---

#### D.2 - Test End-to-End: PDF → Graphiti → RAG Query

**Fichier:** `backend/tests/test_e2e_graphiti_rag.py` (NOUVEAU)

```python
"""
Test End-to-End: PDF Upload → Graphiti Ingestion → RAG Query
"""
import pytest
import asyncio
from pathlib import Path
from app.integrations.dockling import convert_document_to_docling, extract_document_metadata
from app.services.document_chunker import get_chunker
from app.integrations.graphiti import ingest_chunks_to_graph, search_knowledge_graph
from app.core.rag import retrieve_context, build_rag_prompt


@pytest.mark.asyncio
async def test_e2e_pdf_to_rag():
    """
    Test complet: PDF → Docling → Chunking → Graphiti → RAG Query
    
    Note: Utilise un petit PDF de test (pas Niveau 4 GP 35 pages)
    """
    
    # 1. Conversion Docling
    test_pdf = "TestPDF/small_test.pdf"  # À créer: 2-3 pages seulement
    doc = await convert_document_to_docling(test_pdf, timeout=60)
    metadata = extract_document_metadata(doc)
    
    assert doc.num_pages > 0, "Should have pages"
    
    # 2. Chunking
    chunker = get_chunker()
    chunks = chunker.chunk_document(doc, "small_test.pdf", "test-e2e-001")
    
    assert len(chunks) > 0, "Should have chunks"
    print(f"✅ Created {len(chunks)} chunks")
    
    # 3. Graphiti Ingestion
    enriched_metadata = {
        "filename": "small_test.pdf",
        "upload_id": "test-e2e-001",
        "user_id": "test_user",
        **metadata
    }
    
    await ingest_chunks_to_graph(chunks=chunks, metadata=enriched_metadata)
    print(f"✅ Ingested {len(chunks)} chunks to Graphiti")
    
    # Wait for Neo4j to index
    await asyncio.sleep(5)
    
    # 4. RAG Query via Graphiti
    question = "What is this document about?"  # Adapté au test PDF
    context = await retrieve_context(question, top_k=5, group_ids=["test_user"])
    
    assert context["total"] > 0, "Should find relevant facts"
    print(f"✅ Found {context['total']} relevant facts")
    
    # 5. Build Prompt
    system_prompt, user_prompt = build_rag_prompt(question, context)
    
    assert "DiveTeacher" in system_prompt, "Should have custom system prompt"
    assert question in user_prompt, "Should include question"
    print(f"✅ Built RAG prompt ({len(user_prompt)} chars)")
    
    print("\n🎉 E2E Test PASSED!")
```

**Commande:**
```bash
docker exec rag-backend pytest tests/test_e2e_graphiti_rag.py -v -s
```

---

#### D.3 - Test Manuel: Upload PDF Réel via Curl

**Commande:**
```bash
# 1. Upload PDF (petit de préférence pour test rapide)
curl -X POST http://localhost:8000/api/upload \
  -F "file=@TestPDF/Nitrox.pdf" \
  -F "metadata={\"user_id\":\"manual_test\"}"

# Output: {"upload_id": "abc-123", "status": "processing"}

# 2. Attendre fin processing (2-5 min pour Nitrox 42 pages)
sleep 300

# 3. Vérifier stats graphe
curl http://localhost:8000/api/graph/stats

# Output attendu:
# {
#   "episodes": 500+,
#   "entities": 50-100,
#   "relationships": 100-200
# }

# 4. Query RAG
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quels sont les risques du Nitrox?",
    "group_ids": ["manual_test"]
  }'

# Output: {"answer": "...", "context": {...}, "num_sources": 5}
```

---

#### D.4 - Inspection Neo4j Browser

**URL:** http://localhost:7475 (Browser Neo4j)

**Queries de Vérification:**

```cypher
// 1. Compter Episodes
MATCH (e:Episode)
RETURN count(e) AS episode_count

// Attendu: 436+ pour Niveau 4 GP, 500+ pour Nitrox

// 2. Compter Entities
MATCH (n:Entity)
RETURN count(n) AS entity_count

// Attendu: 50-100

// 3. Voir sample Entities
MATCH (n:Entity)
RETURN n.name, n.summary, n.entity_type
LIMIT 10

// Attendu: "Niveau 4", "Prérequis", "FFESSM", "MFT", etc.

// 4. Voir Relations
MATCH (source:Entity)-[r:RELATES_TO]->(target:Entity)
RETURN 
  source.name AS from,
  r.fact AS relationship,
  target.name AS to,
  r.valid_at AS valid_at
LIMIT 20

// Attendu: Relations sémantiques extraites par LLM

// 5. Vérifier group_ids (multi-tenant)
MATCH (e:Episode)
WHERE e.group_id IS NOT NULL
RETURN DISTINCT e.group_id AS group_id, count(e) AS count

// Attendu: "default", "manual_test", etc.
```

---

### Phase E: Documentation et Cleanup (30 min)

#### E.1 - Mettre à Jour Documentation

**Fichiers à Updater:**

1. **`docs/NEO4J.md`** (À créer si pas fait en Phase 0.8)
   - Section Graphiti configuration
   - Schéma Neo4j (Episodes, Entities, Relations)
   - SearchConfig examples

2. **`docs/TROUBLESHOOTING.md`** (À créer)
   - Section "Graphiti Errors"
   - Ollama embeddings issues
   - Community building timeouts

3. **`CURRENT-CONTEXT.md`**
   - Update "Phase 0.9 Complete" status
   - Add Graphiti metrics (entities, relations)

4. **`Devplan/PHASE-0.9-GRAPHITI-IMPLEMENTATION.md`** (ce fichier)
   - Section "RÉSULTATS D'IMPLÉMENTATION"
   - Tests validés
   - Metrics observées

---

#### E.2 - Cleanup Code

**Actions:**

1. **Supprimer code mort:**
   - Anciennes queries Neo4j RAG si entièrement remplacées par Graphiti
   - Fichiers de test obsolètes

2. **Ajouter Type Hints:**
   - Vérifier toutes fonctions Graphiti ont annotations complètes

3. **Logging Consistency:**
   - Uniformiser emojis/format logs Graphiti

4. **Docstrings:**
   - S'assurer toutes fonctions publiques ont docstrings Google-style

---

## Tests de Validation

### Checklist Tests Manuels

- [ ] **A.1** - Modèles Ollama installés (`mistral`, `nomic-embed-text`)
- [ ] **A.2** - Graphiti 0.17.0 installé (vérifier version)
- [ ] **A.3** - Variables env Ollama configurées
- [ ] **B.1** - Graphiti client initialize sans erreur
- [ ] **B.1** - Logs montrent "✅ Graphiti client initialized: LLM=mistral..."
- [ ] **B.2** - Endpoint `/graph/build-communities` existe
- [ ] **B.2** - Endpoint `/graph/stats` retourne data valide
- [ ] **C.1** - `rag.py` utilise `search_knowledge_graph()`
- [ ] **C.1** - Queries RAG retournent facts Graphiti (pas juste chunks)
- [ ] **D.2** - E2E test passe (PDF → Graphiti → RAG)
- [ ] **D.3** - Upload manuel Nitrox réussit
- [ ] **D.3** - `/graph/stats` montre entities + relations
- [ ] **D.3** - Query RAG retourne answer with facts
- [ ] **D.4** - Neo4j Browser montre Episodes + Entities + RELATES_TO
- [ ] **D.4** - group_ids présents dans Episodes

### Checklist Tests Automatisés

- [ ] **D.1** - `test_graphiti_client_singleton()` ✅
- [ ] **D.1** - `test_graphiti_ollama_config()` ✅
- [ ] **D.1** - `test_graphiti_indices_built()` ✅
- [ ] **D.2** - `test_e2e_pdf_to_rag()` ✅

**Commande:**
```bash
docker exec rag-backend pytest tests/ -v --cov=app/integrations/graphiti
```

---

## Métriques de Succès

### Métriques Techniques

| Métrique | Cible | Mesure |
|----------|-------|--------|
| **Graphiti Version** | 0.17.0 | `import graphiti_core; print(graphiti_core.__version__)` |
| **OpenAI LLM Config** | GPT-5-nano (2M TPM) | Logs startup backend: "✅ Graphiti client initialized: OpenAI GPT-5-nano" |
| **Embeddings Config** | text-embedding-3-small (1536 dim) | Logs startup backend |
| **Entities Extracted** | 50-100 pour 35 pages PDF | Query Neo4j: `MATCH (n:Entity) RETURN count(n)` |
| **Relations Extracted** | 100-200 | Query Neo4j: `MATCH ()-[r:RELATES_TO]->() RETURN count(r)` |
| **Ingestion Time** | 20-30s pour 436 chunks (2M TPM!) | Logs processor: "✅ Ingestion: Xs" |
| **RAG Query Time** | <2s (sans LLM generation) | Logs rag.py: "✅ Graphiti search returned X results" |
| **Community Building** | <5 min pour 500 episodes | Logs endpoint `/graph/build-communities` |

### Métriques Qualité

| Métrique | Cible | Validation |
|----------|-------|------------|
| **Entity Quality** | Concepts pertinents extraits | Inspect Neo4j: names comme "Niveau 4", "Prérequis", "FFESSM" |
| **Relation Quality** | Relations sémantiques correctes | Inspect Neo4j: facts comme "Niveau 4 requires Niveau 3" |
| **RAG Answer Quality** | Réponses grounded avec citations | Test manuel: question → answer doit citer [Fact 1], [Fact 2] |
| **Multi-tenant Isolation** | group_ids distinct par user | Query Neo4j: `MATCH (e:Episode) RETURN DISTINCT e.group_id` |

### Métriques Observabilité

| Métrique | Outil | Action |
|----------|-------|--------|
| **Logs Structured** | Docker logs backend | `docker logs rag-backend | grep "🔧 Initializing Graphiti"` |
| **Neo4j Health** | Neo4j Browser | http://localhost:7475 → MATCH (n) RETURN count(n) |
| **Sentry Errors** | Sentry dashboard | Vérifier pas d'erreurs Graphiti |
| **API Response Times** | `/api/rag/query` | curl + `time` command |

---

## Problèmes Potentiels et Solutions

### Problème: OpenAI API Rate Limiting

**Symptôme:**
```
ERROR: Graphiti ingestion failed: Rate limit exceeded (429)
```

**Causes:**
- Tier OpenAI pas configuré avec 2M TPM
- (Très peu probable avec GPT-5-nano qui a rate limit maximal)

**Solutions:**
1. **Vérifier tier OpenAI:**
   ```bash
   # Checker limits via API
   curl https://api.openai.com/v1/usage \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   
   # GPT-5-nano devrait avoir 2M TPM par défaut
   ```

2. **Si vraiment rate limited (rare), batch processing:**
   ```python
   # Ingest par batches de 50 chunks avec pause
   for i in range(0, len(chunks), 50):
       batch = chunks[i:i+50]
       await ingest_chunks_to_graph(batch, metadata)
       await asyncio.sleep(1)  # Pause 1s entre batches
   ```

3. **Augmenter SEMAPHORE_LIMIT dans Graphiti (optionnel):**
   ```bash
   # .env
   SEMAPHORE_LIMIT=20  # Default: 10, augmenter avec 2M TPM!
   ```

---

### Problème: Entities Extraction Rate Faible

**Symptôme:**
```
Neo4j shows:
- 436 Episodes ✅
- 5 Entities ❌ (attendu: 50-100)
- 2 Relations ❌ (attendu: 100-200)
```

**Causes:**
- Prompts Graphiti pas optimisés pour domaine plongée
- Chunks trop longs/courts
- (Très peu probable avec GPT-5-nano, qualité excellente)

**Solutions:**
1. **Vérifier qualité extraction:**
   ```bash
   # Check logs ingestion
   docker logs rag-backend | grep "Graphiti"
   
   # Vérifier entities dans Neo4j
   # http://localhost:7475
   MATCH (n:Entity) RETURN n.name, n.summary LIMIT 20
   ```

2. **Custom Entity Types (Phase 1+):**
   ```python
   # Dans graphiti.py
   from pydantic import BaseModel, Field
   
   class DivingCertification(BaseModel):
       """Certification de plongée"""
       name: str = Field(description="Nom certification (ex: Niveau 4)")
       level: int = Field(description="Niveau (1-4)")
       organization: str = Field(description="FFESSM, SSI, PADI, etc.")
   
   class DivingProcedure(BaseModel):
       """Procédure de plongée"""
       name: str = Field(description="Nom procédure")
       description: str = Field(description="Description")
   
   # Utiliser dans add_episode
   await client.add_episode(
       ...,
       entity_types=[DivingCertification, DivingProcedure]
   )
   ```

---

### Problème: Community Building Très Lent

**Symptôme:**
```
🏘️  Building communities...
[5 minutes later...]
Still running...
```

**Causes:**
- Graphe trop grand (1000+ episodes, 500+ entities)
- Algorithme Louvain computationnellement cher

**Solutions:**
1. **Skip community building en dev:**
   ```python
   # Phase 0: Skip, focus sur ingestion + search
   # Phase 1: Activer pour prod seulement
   ```

2. **Background task avec timeout:**
   ```python
   async def run_community_building():
       try:
           await asyncio.wait_for(
               graphiti_build_communities(),
               timeout=300  # 5 min max
           )
       except asyncio.TimeoutError:
           logger.warning("⚠️  Community building timeout (5 min)")
   ```

3. **Cron job nocturne:**
   ```bash
   # Production: cron daily 3am
   0 3 * * * curl -X POST http://backend:8000/api/graph/build-communities
   ```

---

## Notes Finales

### Décisions Architecturales

1. **Graphiti Native Search > Neo4j Manual Queries**
   - Graphiti search() utilise hybrid (semantic + BM25 + RRF) optimisé
   - Nos queries manuelles Neo4j sont sous-optimales
   - Migration vers Graphiti = meilleure qualité RAG

2. **Community Building Périodique**
   - Trop coûteux pour appeler après chaque upload
   - Bénéfice marginal (communautés évoluent lentement)
   - Stratégie: Cron daily en prod, manuel en dev

3. **Multi-tenant via group_ids**
   - Prêt pour Phase 1 (Supabase Auth)
   - Isolation data par user dès maintenant
   - Pas de refactor nécessaire plus tard

4. **OpenAI GPT-5-nano (Graphiti) + Ollama (RAG) = Hybrid Optimal**
   - Coût OpenAI ~$0.50-1.00/document (extraction one-time, le moins cher!)
   - Coût Ollama 0€ (queries utilisateur ongoing)
   - Performance maximale: 2M tokens/min (ingestion ultra-rapide)
   - Meilleure qualité extraction (GPT-5-nano > Mistral 7b)
   - Trade-off optimal: Qualité + Vitesse + Coût minimal

### Roadmap Post-Phase 0.9

**Phase 1 - Multi-user:**
- ✅ group_ids déjà implémenté
- TODO: Lier user_id Supabase → group_id Graphiti

**Phase 2 - Custom Entities:**
- TODO: Définir types `DivingCertification`, `DivingProcedure`, `SafetyRule`, etc.
- TODO: Edges custom: `REQUIRES`, `RECOMMENDS`, `CONTRADICTS`, `PART_OF`

**Phase 3 - Advanced RAG:**
- TODO: Temporal queries (point-in-time: "What was valid in 2020?")
- TODO: MMR reranking (diversity)
- TODO: Cross-encoder reranking (meilleure qualité, plus lent)

---

## 🎉 Résultats d'Implémentation

> **Section à compléter après exécution du plan**

### Status par Phase

| Phase | Status | Durée | Notes |
|-------|--------|-------|-------|
| **A - Préparation** | ⏳ | - | - |
| **B - Config Graphiti** | ⏳ | - | - |
| **C - RAG Integration** | ⏳ | - | - |
| **D - Tests** | ⏳ | - | - |
| **E - Documentation** | ⏳ | - | - |

### Problèmes Rencontrés

> À remplir au fur et à mesure

### Solutions Appliquées

> À remplir au fur et à mesure

### Métriques Finales

> À remplir après tests E2E

---

**🚀 Prêt pour Phase 0.9!**

**Prochaine Étape:** Exécuter le plan step-by-step avec validation à chaque phase.

