# PHASE 0.8 - Neo4j Implementation Complète

**Status:** 🔄 EN COURS  
**Date de Création:** 27 Octobre 2025  
**Objectif:** Implémenter correctement Neo4j pour DiveTeacher avec Graphiti et RAG optimisé  
**Référence:** `resources/252027-neo4j-guide-for-ai-agent.md`

---

## 📋 TABLE DES MATIÈRES

1. [Audit de l'Implémentation Actuelle](#1-audit-de-limplémentation-actuelle)
2. [Analyse des Gaps Critiques](#2-analyse-des-gaps-critiques)
3. [Compatibilité avec Graphiti](#3-compatibilité-avec-graphiti)
4. [Plan d'Implémentation Détaillé](#4-plan-dimplémentation-détaillé)
5. [Tests de Validation](#5-tests-de-validation)
6. [Critères de Succès](#6-critères-de-succès)

---

## 1. AUDIT DE L'IMPLÉMENTATION ACTUELLE

### 1.1 État des Lieux

#### ✅ **Ce qui fonctionne:**
1. **Connexion Neo4j** via Graphiti (indirect)
   - Graphiti gère la connexion Neo4j
   - `build_indices_and_constraints()` appelé
   - Singleton pattern implémenté
   - Cleanup au shutdown

2. **Ingestion via Graphiti**
   - Chunks ingérés comme "episodes"
   - Extraction automatique d'entités/relations
   - Community building après ingestion

3. **Configuration**
   - Variables d'environnement correctes
   - Ports mappés (7475:7474, 7688:7687)
   - Authentification configurée

#### ❌ **Ce qui est problématique:**

##### A. **Neo4jClient (`backend/app/integrations/neo4j.py`)**

**Problème #1: AsyncGraphDatabase vs GraphDatabase**
```python
# ❌ ACTUEL: Utilise AsyncGraphDatabase (déprecated pour queries simples)
from neo4j import AsyncGraphDatabase, AsyncDriver
self.driver = AsyncGraphDatabase.driver(...)
```

**Impact:**
- Complexité inutile pour des opérations simples
- Pattern async/await partout (overhead)
- Pas compatible avec `execute_query()` (recommandé par Neo4j)

**Recommandation Guide:**
> "Use `execute_query()` - This is the **simplest and recommended** method. It handles session management automatically."

---

**Problème #2: Query RAG Basique et Inefficace**
```python
# ❌ ACTUEL: Keyword matching naïf
query = """
MATCH (n)
WHERE ANY(keyword IN $keywords WHERE toLower(n.text) CONTAINS keyword)
RETURN n.text AS text, n.source AS source, n.metadata AS metadata
LIMIT $top_k
"""
```

**Problèmes:**
- Assume que nodes ont `.text`, `.source`, `.metadata` (pas le cas avec Graphiti!)
- Pas de vector search (embeddings)
- Pas de graph traversal (relations ignorées)
- Pas d'indexes utilisés
- Pas de ranking/scoring

**Graphiti crée ces nodes:**
- `:Entity` - Entités extraites
- `:Episode` - Chunks ingérés
- `:Community` - Groupes d'entités
- **RELATIONS:** `:RELATES_TO`, `:MENTIONS`, etc.

---

**Problème #3: Méthodes `ingest_nodes()` et `ingest_relationships()` Inutilisées**
```python
async def ingest_nodes(self, nodes: List[Dict[str, Any]]) -> int:
    # ❌ JAMAIS APPELÉ - Graphiti gère l'ingestion
    query = """
    UNWIND $nodes AS node
    CREATE (n:Entity)
    SET n = node
    """
```

**Impact:**
- Code mort qui confond le pipeline
- Conflit potentiel avec schema Graphiti
- Pas de coordination avec indices Graphiti

---

**Problème #4: Pas d'Indexes Optimisés pour RAG**

Graphiti crée ses propres indexes, MAIS pour RAG query efficace on a besoin de:
- Index full-text sur `Episode.content` (text chunks)
- Index sur `Entity.name` (entités extraites)
- Index sur `Episode.uuid` et `Entity.uuid`

---

**Problème #5: Pas de Vector Search**

Le RAG actuel ne fait PAS de similarity search:
- Pas d'embeddings stockés dans Neo4j
- Pas de vector index
- Pas de hybrid search (keyword + vector)

**Pour DiveTeacher, c'est critique** car:
- Questions techniques nécessitent semantic search
- Tableaux MFT FFESSM doivent être retrouvés même avec termes différents
- "Quel est le palier à 30m?" doit matcher "profondeur 30 mètres" + tableaux

---

##### B. **Architecture Dual: Neo4jClient ET Graphiti**

**Confusion Actuelle:**
```python
# 1. Graphiti utilise Neo4j (avec son propre driver)
graphiti_client = Graphiti(uri=..., user=..., password=...)

# 2. Neo4jClient AUSSI se connecte (driver séparé!)
neo4j_client = Neo4jClient()  # Autre driver!
```

**Problème:**
- 2 drivers différents vers même DB
- 2 pools de connexions
- Potentiel conflit de transactions
- Overhead mémoire

**Recommandation:**
- Graphiti pour **WRITE** (ingestion)
- Neo4jClient pour **READ** (RAG query)
- OU: Accéder directement au driver Graphiti pour queries

---

### 1.2 Comparaison avec Best Practices du Guide

| Aspect | Guide Neo4j | Implémentation Actuelle | Gap |
|--------|-------------|-------------------------|-----|
| **Driver API** | `GraphDatabase.driver()` + `execute_query()` | `AsyncGraphDatabase` (async partout) | ❌ Trop complexe |
| **Query Method** | `execute_query()` (simple, recommandé) | `session.run()` (manuel) | ❌ Overhead |
| **Parameters** | ✅ TOUJOURS paramétrer | ✅ Paramétré | ✅ OK |
| **Indexes** | Créer pour lookup properties | Graphiti crée les siens, RAG queries pas optimisées | ⚠️ Partiel |
| **Vector Search** | Recommandé pour semantic search | ❌ Absent | ❌ Critique |
| **Error Handling** | Try/except spécifiques | Generic try/except | ⚠️ Basique |
| **Connection Pool** | Configuré (max_pool_size, etc.) | Défaut | ⚠️ Non optimisé |
| **Transactions** | `execute_write()` pour writes | Graphiti gère | ✅ OK (via Graphiti) |
| **Batch Operations** | UNWIND pour bulk inserts | Graphiti fait du batch | ✅ OK (via Graphiti) |

---

## 2. ANALYSE DES GAPS CRITIQUES

### 2.1 Gap #1: RAG Query Inefficace (PRIORITÉ 1 🔴)

**Problème:**
```python
# ❌ ACTUEL: Query naïve qui ne fonctionne PAS avec Graphiti schema
MATCH (n)
WHERE ANY(keyword IN $keywords WHERE toLower(n.text) CONTAINS keyword)
```

**Pourquoi ça ne marche pas:**
1. Graphiti crée `:Episode` nodes avec `content` (pas `text`)
2. Pas de scoring/ranking
3. Ignore les entités et relations

**Solution:**
```cypher
# ✅ CORRECT: Hybrid search Episodes + Entities
CALL db.index.fulltext.queryNodes('episode_content', $search_text) 
YIELD node AS episode, score AS episode_score
RETURN episode.content AS text, 
       episode.source_description AS source,
       episode_score AS score
ORDER BY episode_score DESC
LIMIT $top_k

UNION

MATCH (e:Entity)-[:RELATES_TO*1..2]-(related:Entity)
WHERE e.name CONTAINS $search_text
RETURN e.summary AS text,
       e.name AS source,
       1.0 AS score
LIMIT $top_k
```

---

### 2.2 Gap #2: Pas de Vector Embeddings (PRIORITÉ 1 🔴)

**Impact:**
- Questions sémantiques échouent
- "Procédure de remontée" ne matche pas "technique d'ascension"
- Tableaux MFT non retrouvés

**Solution:**
1. Générer embeddings pour chaque Episode/Entity
2. Stocker dans Neo4j (`episode.embedding`)
3. Créer vector index
4. Query avec cosine similarity

---

### 2.3 Gap #3: Pas de Graph Traversal (PRIORITÉ 2 🟡)

**Problème:**
Le RAG actuel ignore les **relations** entre entités.

**Exemple Critique pour DiveTeacher:**
```
Question: "Quels sont les prérequis pour le niveau 4?"

Current Query: ❌ Ne trouve que "niveau 4" text chunks

Ideal Query: ✅
MATCH (cert:Entity {name: "Niveau 4"})-[:REQUIRES]->(prereq:Entity)
RETURN cert, prereq
```

**Graphiti crée automatiquement:**
- `:RELATES_TO` entre entités
- `:MENTIONS` (Episode → Entity)
- Mais on doit les **utiliser** dans queries!

---

### 2.4 Gap #4: Indexes Manquants pour RAG (PRIORITÉ 2 🟡)

**Indexes Graphiti (déjà créés via `build_indices_and_constraints()`):**
- Index sur `Entity.uuid`
- Index sur `Episode.uuid`
- Constraints d'unicité

**Indexes MANQUANTS pour RAG:**
```cypher
-- Full-text search sur Episode content
CREATE FULLTEXT INDEX episode_content FOR (e:Episode) ON EACH [e.content]

-- Index sur Entity name (lookup rapide)
CREATE INDEX entity_name FOR (e:Entity) ON (e.name)

-- Vector index (si embeddings ajoutés)
CREATE VECTOR INDEX episode_embeddings FOR (e:Episode) ON (e.embedding)
```

---

### 2.5 Gap #5: Error Handling Non Spécifique (PRIORITÉ 3 🟢)

**Guide recommande:**
```python
from neo4j.exceptions import (
    ServiceUnavailable,
    AuthError,
    CypherSyntaxError,
    ConstraintError
)
```

**Actuel:**
```python
except Exception as e:  # ❌ Trop générique
    sentry_sdk.capture_exception(e)
```

---

### 2.6 Gap #6: Connection Pool Non Optimisé (PRIORITÉ 3 🟢)

**Actuel:**
```python
self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
# Pas de config pool!
```

**Guide recommande:**
```python
driver = GraphDatabase.driver(
    uri,
    auth=(user, password),
    max_connection_pool_size=50,
    max_connection_lifetime=3600,
    connection_acquisition_timeout=60
)
```

---

## 3. COMPATIBILITÉ AVEC GRAPHITI

### 3.1 Schema Graphiti (Confirmé)

D'après le guide Graphiti (`251020-graphiti-technical-guide.md`):

#### **Nodes:**
```cypher
(:Episode {
  uuid: String,
  name: String,
  content: String,              # Le text du chunk
  source: String,                # "text", "json", etc.
  source_description: String,    # Metadata
  created_at: DateTime,
  valid_at: DateTime
})

(:Entity {
  uuid: String,
  name: String,                  # Nom de l'entité
  entity_type: String,           # Type (PERSON, CONCEPT, etc.)
  summary: String,               # Description
  created_at: DateTime
})

(:Community {
  uuid: String,
  name: String,
  summary: String
})
```

#### **Relationships:**
```cypher
(Episode)-[:MENTIONS]->(Entity)
(Entity)-[:RELATES_TO {fact: String}]->(Entity)
(Entity)-[:IN_COMMUNITY]->(Community)
```

---

### 3.2 Accès au Driver Graphiti

**Option 1: Utiliser le driver interne de Graphiti**
```python
# Graphiti expose son driver Neo4j
graphiti_client = await get_graphiti_client()
driver = graphiti_client.driver  # Accès direct au neo4j.GraphDatabase.driver

# Puis utiliser pour RAG queries
records, summary, keys = driver.execute_query(
    "MATCH (e:Episode) WHERE e.content CONTAINS $text RETURN e",
    text=search_text,
    database_="neo4j"
)
```

**Option 2: Garder Neo4jClient séparé (lecture seule)**
```python
# Graphiti: WRITE operations (ingestion)
# Neo4jClient: READ operations (RAG query)
```

**✅ RECOMMANDATION: Option 1**
- Un seul driver
- Pas de conflit de connexion
- Plus simple à maintenir

---

### 3.3 Queries RAG Optimisées pour Schema Graphiti

#### **Query 1: Full-Text Search sur Episodes**
```cypher
CALL db.index.fulltext.queryNodes('episode_content', $search_text) 
YIELD node, score
RETURN 
  node.content AS text,
  node.source_description AS source,
  node.name AS chunk_name,
  score
ORDER BY score DESC
LIMIT $top_k
```

#### **Query 2: Entity + Related Entities**
```cypher
MATCH (e:Entity)
WHERE e.name CONTAINS $entity_name OR e.summary CONTAINS $entity_name
OPTIONAL MATCH (e)-[r:RELATES_TO]-(related:Entity)
RETURN 
  e.name AS entity,
  e.summary AS description,
  collect({
    name: related.name,
    relationship: r.fact
  }) AS related_entities
LIMIT $top_k
```

#### **Query 3: Episode → Entities (Contexte enrichi)**
```cypher
CALL db.index.fulltext.queryNodes('episode_content', $search_text) 
YIELD node AS episode, score
MATCH (episode)-[:MENTIONS]->(entity:Entity)
RETURN 
  episode.content AS text,
  episode.source_description AS source,
  collect(entity.name) AS mentioned_entities,
  score
ORDER BY score DESC
LIMIT $top_k
```

---

## 4. PLAN D'IMPLÉMENTATION DÉTAILLÉ

### Phase A: Refactor Neo4jClient (2-3h)

#### A.1: Simplifier Driver API ✅
**Objectif:** Migrer vers `GraphDatabase.driver()` + `execute_query()`

**Fichier:** `backend/app/integrations/neo4j.py`

**Changements:**
```python
# ❌ AVANT
from neo4j import AsyncGraphDatabase, AsyncDriver

class Neo4jClient:
    async def connect(self):
        self.driver = AsyncGraphDatabase.driver(...)
    
    async def query_context(self, question: str):
        async with self.driver.session(...) as session:
            result = await session.run(query, ...)
```

**✅ APRÈS**
```python
from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import ServiceUnavailable, CypherSyntaxError, Neo4jError

class Neo4jClient:
    def __init__(self):
        self.driver = None
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.database = settings.NEO4J_DATABASE
    
    def connect(self):
        """Synchronous connection (driver handles async internally)"""
        if not self.driver:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_pool_size=50,
                max_connection_lifetime=3600,
                connection_acquisition_timeout=60
            )
            self.driver.verify_connectivity()
    
    def close(self):
        """Close connection"""
        if self.driver:
            self.driver.close()
            self.driver = None
    
    def query_context(
        self, 
        question: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Simple, synchronous query using execute_query()"""
        self.connect()
        
        try:
            records, summary, keys = self.driver.execute_query(
                """
                CALL db.index.fulltext.queryNodes('episode_content', $search_text) 
                YIELD node, score
                RETURN 
                  node.content AS text,
                  node.source_description AS source,
                  score
                ORDER BY score DESC
                LIMIT $top_k
                """,
                search_text=question,
                top_k=top_k,
                database_=self.database,
                routing_=RoutingControl.READ
            )
            
            return [dict(record) for record in records]
            
        except ServiceUnavailable as e:
            logger.error(f"Neo4j unavailable: {e}")
            return []
        except CypherSyntaxError as e:
            logger.error(f"Cypher syntax error: {e}")
            return []
        except Neo4jError as e:
            logger.error(f"Neo4j error [{e.code}]: {e.message}")
            return []
```

**Impact:**
- ✅ Code plus simple (moins de async/await)
- ✅ Suit best practices Neo4j 2025
- ✅ Connection pool optimisé
- ✅ Error handling spécifique

---

#### A.2: Supprimer Méthodes Inutilisées ✅
**Fichier:** `backend/app/integrations/neo4j.py`

**Supprimer:**
- `ingest_nodes()` - Graphiti gère
- `ingest_relationships()` - Graphiti gère

**Raison:** Conflit potentiel avec schema Graphiti, code mort

---

#### A.3: Ajouter Indexes RAG ✅
**Objectif:** Créer indexes optimisés pour RAG queries

**Nouveau module:** `backend/app/integrations/neo4j_indexes.py`

```python
"""Neo4j Indexes Management for RAG Queries"""

from typing import List
from neo4j import GraphDatabase
from app.core.config import settings
import logging

logger = logging.getLogger('diveteacher.neo4j')


def create_rag_indexes(driver: GraphDatabase.driver) -> List[str]:
    """
    Create indexes optimized for RAG queries
    
    Note: Ces indexes s'AJOUTENT aux indexes Graphiti (pas de conflit)
    
    Returns:
        List of index names created
    """
    indexes_created = []
    
    # 1. Full-text index sur Episode content
    try:
        driver.execute_query(
            """
            CREATE FULLTEXT INDEX episode_content IF NOT EXISTS
            FOR (e:Episode) ON EACH [e.content]
            """,
            database_=settings.NEO4J_DATABASE
        )
        indexes_created.append("episode_content")
        logger.info("✅ Full-text index 'episode_content' created")
    except Exception as e:
        logger.warning(f"Index 'episode_content' may already exist: {e}")
    
    # 2. Index sur Entity name (lookup rapide)
    try:
        driver.execute_query(
            """
            CREATE INDEX entity_name_idx IF NOT EXISTS
            FOR (e:Entity) ON (e.name)
            """,
            database_=settings.NEO4J_DATABASE
        )
        indexes_created.append("entity_name_idx")
        logger.info("✅ Index 'entity_name_idx' created")
    except Exception as e:
        logger.warning(f"Index 'entity_name_idx' may already exist: {e}")
    
    # 3. Index sur Episode valid_at (filter par date)
    try:
        driver.execute_query(
            """
            CREATE INDEX episode_date_idx IF NOT EXISTS
            FOR (e:Episode) ON (e.valid_at)
            """,
            database_=settings.NEO4J_DATABASE
        )
        indexes_created.append("episode_date_idx")
        logger.info("✅ Index 'episode_date_idx' created")
    except Exception as e:
        logger.warning(f"Index 'episode_date_idx' may already exist: {e}")
    
    return indexes_created


def verify_indexes(driver: GraphDatabase.driver) -> dict:
    """Verify all indexes are created"""
    records, summary, keys = driver.execute_query(
        "CALL db.indexes()",
        database_=settings.NEO4J_DATABASE
    )
    
    indexes = [dict(record) for record in records]
    
    return {
        "total": len(indexes),
        "indexes": [
            {
                "name": idx["name"],
                "type": idx["type"],
                "state": idx["state"]
            }
            for idx in indexes
        ]
    }
```

**Appeler dans startup:**
```python
# backend/app/main.py
from app.integrations.neo4j_indexes import create_rag_indexes

@app.on_event("startup")
async def startup_event():
    # ... existing code ...
    
    # Create RAG indexes (après Graphiti indices)
    try:
        neo4j_client.connect()
        indexes = create_rag_indexes(neo4j_client.driver)
        print(f"✅ Created {len(indexes)} RAG indexes")
    except Exception as e:
        print(f"⚠️  Index creation failed: {e}")
```

---

### Phase B: Améliorer Queries RAG (2-3h)

#### B.1: Implémenter Full-Text Search ✅
**Fichier:** `backend/app/integrations/neo4j.py`

**Nouvelle méthode:**
```python
def query_context_fulltext(
    self, 
    question: str, 
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Full-text search sur Episodes (chunks)
    
    Args:
        question: User question
        top_k: Number of results
        
    Returns:
        List of context chunks with scores
    """
    self.connect()
    
    try:
        records, summary, keys = self.driver.execute_query(
            """
            CALL db.index.fulltext.queryNodes('episode_content', $search_text) 
            YIELD node, score
            RETURN 
              node.content AS text,
              node.source_description AS source,
              node.name AS chunk_name,
              node.created_at AS created_at,
              score
            ORDER BY score DESC
            LIMIT $top_k
            """,
            search_text=question,
            top_k=top_k,
            database_=self.database,
            routing_=RoutingControl.READ
        )
        
        context = []
        for record in records:
            context.append({
                "text": record["text"],
                "source": record["source"] or "Unknown",
                "chunk_name": record["chunk_name"],
                "score": record["score"],
                "created_at": record["created_at"]
            })
        
        logger.info(f"Full-text search returned {len(context)} results")
        return context
        
    except Neo4jError as e:
        logger.error(f"Full-text search failed: {e}")
        return []
```

---

#### B.2: Implémenter Entity Search ✅
**Fichier:** `backend/app/integrations/neo4j.py`

**Nouvelle méthode:**
```python
def query_entities_related(
    self, 
    entity_name: str, 
    depth: int = 2
) -> List[Dict[str, Any]]:
    """
    Search entities and their related entities
    
    Args:
        entity_name: Entity to search
        depth: Relationship depth (1-3)
        
    Returns:
        List of entities with relationships
    """
    self.connect()
    
    try:
        records, summary, keys = self.driver.execute_query(
            f"""
            MATCH (e:Entity)
            WHERE toLower(e.name) CONTAINS toLower($entity_name)
               OR toLower(e.summary) CONTAINS toLower($entity_name)
            OPTIONAL MATCH (e)-[r:RELATES_TO*1..{depth}]-(related:Entity)
            RETURN 
              e.name AS entity,
              e.summary AS description,
              e.entity_type AS type,
              collect(DISTINCT {{
                name: related.name,
                type: related.entity_type,
                relationship: [rel IN r | rel.fact][0]
              }}) AS related_entities
            LIMIT 10
            """,
            entity_name=entity_name,
            database_=self.database,
            routing_=RoutingControl.READ
        )
        
        entities = []
        for record in records:
            entities.append({
                "entity": record["entity"],
                "description": record["description"],
                "type": record["type"],
                "related": [r for r in record["related_entities"] if r["name"]]
            })
        
        logger.info(f"Entity search found {len(entities)} entities")
        return entities
        
    except Neo4jError as e:
        logger.error(f"Entity search failed: {e}")
        return []
```

---

#### B.3: Hybrid Search (Episodes + Entities) ✅
**Fichier:** `backend/app/integrations/neo4j.py`

**Méthode principale (remplace `query_context`):**
```python
def query_context_hybrid(
    self, 
    question: str, 
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Hybrid search: Full-text Episodes + Entity search
    
    Returns:
        {
            "episodes": [...],  # Text chunks
            "entities": [...],  # Related entities
            "total": int
        }
    """
    self.connect()
    
    # 1. Full-text search sur chunks
    episodes = self.query_context_fulltext(question, top_k=top_k)
    
    # 2. Extract potential entity names from question
    # Simple keyword extraction (can be improved with NER)
    keywords = [w for w in question.split() if len(w) > 3]
    
    entities = []
    for keyword in keywords[:3]:  # Limit to 3 keywords
        entity_results = self.query_entities_related(keyword, depth=1)
        entities.extend(entity_results)
    
    # Deduplicate entities by name
    unique_entities = {e["entity"]: e for e in entities}.values()
    
    return {
        "episodes": episodes,
        "entities": list(unique_entities)[:top_k],
        "total": len(episodes) + len(unique_entities)
    }
```

---

#### B.4: Mettre à Jour RAG Chain ✅
**Fichier:** `backend/app/core/rag.py`

**Modifications:**
```python
async def retrieve_context(question: str, top_k: int = None) -> Dict[str, Any]:
    """
    Retrieve context using hybrid search
    
    Returns:
        {
            "episodes": List[Dict],
            "entities": List[Dict],
            "total": int
        }
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K
    
    # Hybrid search (Episodes + Entities)
    context = neo4j_client.query_context_hybrid(question, top_k=top_k)
    
    return context


def build_rag_prompt(question: str, context: Dict[str, Any]) -> tuple[str, str]:
    """
    Build prompt from hybrid context
    """
    episodes = context.get("episodes", [])
    entities = context.get("entities", [])
    
    # Build context string
    context_parts = []
    
    # 1. Add episode chunks
    for idx, ep in enumerate(episodes, 1):
        text = ep.get("text", "")
        source = ep.get("source", "Unknown")
        score = ep.get("score", 0)
        context_parts.append(
            f"[Chunk {idx} - Source: {source} - Score: {score:.2f}]\n{text}"
        )
    
    # 2. Add entities (if found)
    if entities:
        entity_parts = []
        for entity in entities:
            name = entity.get("entity", "")
            desc = entity.get("description", "")
            entity_type = entity.get("type", "")
            related = entity.get("related", [])
            
            entity_text = f"**{name}** ({entity_type}): {desc}"
            if related:
                relations = [f"{r['name']} ({r['relationship']})" for r in related[:3]]
                entity_text += f"\nRelated: {', '.join(relations)}"
            
            entity_parts.append(entity_text)
        
        context_parts.append("\n[Related Entities]\n" + "\n".join(entity_parts))
    
    context_str = "\n\n".join(context_parts)
    
    # System prompt (inchangé)
    system_prompt = """You are DiveTeacher, an AI assistant specialized in scuba diving education.

CRITICAL RULES:
1. Answer ONLY using information from the provided context (chunks and entities)
2. If context is insufficient, say "I don't have enough information in the documents"
3. NEVER make up or infer information not present in the context
4. Cite sources (Chunk 1, Chunk 2, Entity name, etc.)
5. Be concise but thorough
6. Use technical diving terms accurately
7. For FFESSM/SSI procedures, cite exact source material

Your goal: Provide accurate, grounded answers that diving students and instructors can trust."""
    
    # User prompt
    if context_parts:
        user_prompt = f"""Context from diving manuals and documents:

{context_str}

---

Question: {question}

Answer based ONLY on the context above:"""
    else:
        user_prompt = f"""No relevant context found in documents.

Question: {question}

Please explain you don't have information to answer this."""
    
    return system_prompt, user_prompt
```

---

### Phase C: Vector Embeddings (FUTUR - Phase 1+) 🔮

**Note:** Vector search nécessite:
1. Modèle d'embeddings (sentence-transformers déjà installé!)
2. Génération d'embeddings pour chaque Episode
3. Stockage dans Neo4j (`episode.embedding`)
4. Vector index Neo4j (Enterprise ou plugin)

**Dépend de:**
- Neo4j 5.11+ avec vector index support
- Ou plugin neo4j-graph-data-science

**Implémentation future:**
```python
# backend/app/integrations/embeddings.py (FUTUR)
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')
    
    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
    
    def store_episode_embedding(self, episode_uuid: str, text: str):
        embedding = self.embed_text(text)
        # Store in Neo4j
        neo4j_client.driver.execute_query(
            """
            MATCH (e:Episode {uuid: $uuid})
            SET e.embedding = $embedding
            """,
            uuid=episode_uuid,
            embedding=embedding,
            database_=settings.NEO4J_DATABASE
        )
```

**Décision:** ⏸️ **Reporter à Phase 1+** (après validation full-text search)

---

### Phase D: Tests et Validation (1-2h)

#### D.1: Tests Unitaires ✅
**Fichier:** `backend/tests/test_neo4j_client.py` (NOUVEAU)

```python
import pytest
from app.integrations.neo4j import Neo4jClient
from neo4j.exceptions import ServiceUnavailable

@pytest.fixture
def neo4j_client():
    client = Neo4jClient()
    client.connect()
    yield client
    client.close()


def test_connection(neo4j_client):
    """Test Neo4j connection"""
    neo4j_client.driver.verify_connectivity()
    assert neo4j_client.driver is not None


def test_query_context_fulltext(neo4j_client):
    """Test full-text search"""
    results = neo4j_client.query_context_fulltext("plongée", top_k=5)
    assert isinstance(results, list)
    # Si docs ingérés, doit retourner des résultats
    if results:
        assert "text" in results[0]
        assert "score" in results[0]


def test_query_entities_related(neo4j_client):
    """Test entity search"""
    results = neo4j_client.query_entities_related("niveau", depth=2)
    assert isinstance(results, list)


def test_query_context_hybrid(neo4j_client):
    """Test hybrid search"""
    results = neo4j_client.query_context_hybrid("niveau 4", top_k=5)
    assert isinstance(results, dict)
    assert "episodes" in results
    assert "entities" in results
    assert "total" in results


def test_error_handling():
    """Test connection error handling"""
    client = Neo4jClient()
    client.uri = "bolt://invalid:7687"
    
    with pytest.raises(ServiceUnavailable):
        client.connect()
```

---

#### D.2: Tests d'Intégration ✅
**Fichier:** `backend/tests/test_rag_integration.py` (NOUVEAU)

```python
import pytest
from app.core.rag import retrieve_context, build_rag_prompt

@pytest.mark.asyncio
async def test_rag_retrieve_context():
    """Test RAG context retrieval"""
    context = await retrieve_context("Qu'est-ce que le niveau 4?", top_k=3)
    
    assert isinstance(context, dict)
    assert "episodes" in context
    assert "entities" in context


@pytest.mark.asyncio
async def test_rag_build_prompt():
    """Test RAG prompt building"""
    context = await retrieve_context("procédure remontée", top_k=3)
    system_prompt, user_prompt = build_rag_prompt("procédure remontée", context)
    
    assert isinstance(system_prompt, str)
    assert isinstance(user_prompt, str)
    assert "DiveTeacher" in system_prompt
    assert "procédure remontée" in user_prompt
```

---

#### D.3: Tests End-to-End ✅

**Script:** `backend/scripts/test_neo4j_rag.py` (NOUVEAU)

```python
"""
Script de test end-to-end pour Neo4j + Graphiti + RAG
"""
import asyncio
from app.integrations.neo4j import neo4j_client
from app.core.rag import retrieve_context, rag_query


async def test_full_pipeline():
    """Test complet du pipeline RAG"""
    
    print("\n🧪 Test 1: Connection Neo4j")
    try:
        neo4j_client.connect()
        neo4j_client.driver.verify_connectivity()
        print("✅ Neo4j connected")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    print("\n🧪 Test 2: Full-Text Search")
    try:
        results = neo4j_client.query_context_fulltext("plongée", top_k=3)
        print(f"✅ Full-text search: {len(results)} results")
        for i, r in enumerate(results[:2], 1):
            print(f"   [{i}] Score: {r['score']:.2f}, Text: {r['text'][:80]}...")
    except Exception as e:
        print(f"❌ Full-text search failed: {e}")
    
    print("\n🧪 Test 3: Entity Search")
    try:
        entities = neo4j_client.query_entities_related("niveau", depth=2)
        print(f"✅ Entity search: {len(entities)} entities")
        for i, e in enumerate(entities[:2], 1):
            print(f"   [{i}] {e['entity']} ({e['type']}): {e['description'][:60]}...")
    except Exception as e:
        print(f"❌ Entity search failed: {e}")
    
    print("\n🧪 Test 4: Hybrid Search")
    try:
        hybrid = neo4j_client.query_context_hybrid("niveau 4 prérequis", top_k=3)
        print(f"✅ Hybrid search: {hybrid['total']} total results")
        print(f"   Episodes: {len(hybrid['episodes'])}")
        print(f"   Entities: {len(hybrid['entities'])}")
    except Exception as e:
        print(f"❌ Hybrid search failed: {e}")
    
    print("\n🧪 Test 5: RAG Query")
    try:
        result = await rag_query("Qu'est-ce que le niveau 4?")
        print(f"✅ RAG query completed")
        print(f"   Sources: {result['num_sources']}")
        print(f"   Answer: {result['answer'][:200]}...")
    except Exception as e:
        print(f"❌ RAG query failed: {e}")
    
    print("\n🧪 Test 6: Indexes Verification")
    try:
        from app.integrations.neo4j_indexes import verify_indexes
        indexes = verify_indexes(neo4j_client.driver)
        print(f"✅ Indexes: {indexes['total']} total")
        for idx in indexes['indexes']:
            if 'episode' in idx['name'] or 'entity' in idx['name']:
                print(f"   - {idx['name']} ({idx['type']}, {idx['state']})")
    except Exception as e:
        print(f"❌ Index verification failed: {e}")
    
    # Cleanup
    neo4j_client.close()
    print("\n✅ All tests completed")


if __name__ == "__main__":
    asyncio.run(test_full_pipeline())
```

**Exécution:**
```bash
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter/backend
python scripts/test_neo4j_rag.py
```

---

### Phase E: Documentation (30min)

#### E.1: Mettre à Jour docs/SETUP.md ✅

**Ajouter section:**
```markdown
## 🔧 Phase 0.8: Neo4j RAG Optimization (IMPLEMENTED)

### Changes in Neo4j Integration

**1. Simplified Driver API**
- Migrated from `AsyncGraphDatabase` to `GraphDatabase.driver()`
- Using `execute_query()` (recommended by Neo4j)
- Connection pool configured (max 50 connections)

**2. RAG Indexes Created**
- Full-text index: `episode_content` (search in chunks)
- Index: `entity_name_idx` (fast entity lookup)
- Index: `episode_date_idx` (filter by date)

**3. Improved RAG Queries**
- **Full-text search:** CALL db.index.fulltext.queryNodes()
- **Entity search:** MATCH entities + relationships
- **Hybrid search:** Episodes + Entities combined

**4. Better Error Handling**
- ServiceUnavailable, CypherSyntaxError, Neo4jError
- Graceful fallbacks (return [] on error)

### Testing Neo4j RAG

```bash
# Run tests
cd backend
python scripts/test_neo4j_rag.py

# Expected output:
✅ Neo4j connected
✅ Full-text search: X results
✅ Entity search: Y entities
✅ Hybrid search: Z total results
✅ RAG query completed
✅ Indexes: N total
```

### Neo4j Browser Verification

1. Open http://localhost:7475
2. Login: neo4j / diveteacher_dev_2025
3. Run queries:

```cypher
// Check indexes
CALL db.indexes()
YIELD name, type, state
WHERE name CONTAINS 'episode' OR name CONTAINS 'entity'
RETURN name, type, state

// Test full-text search
CALL db.index.fulltext.queryNodes('episode_content', 'plongée') 
YIELD node, score
RETURN node.content, score
LIMIT 5

// Check entities
MATCH (e:Entity)
RETURN e.name, e.entity_type, e.summary
LIMIT 10

// Check relationships
MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
RETURN e1.name, type(r), r.fact, e2.name
LIMIT 10
```
```

---

#### E.2: Mettre à Jour CURRENT-CONTEXT.md ✅

**Ajouter dans Session 2:**
```markdown
- ✅ **PHASE 0.8: NEO4J RAG OPTIMIZATION** 🚀
  - Refactored Neo4jClient (AsyncGraph → GraphDatabase)
  - Implemented full-text search on Episodes
  - Implemented entity + relationship queries
  - Implemented hybrid search (Episodes + Entities)
  - Created RAG-specific indexes
  - Updated RAG chain with hybrid context
  - Error handling improved (ServiceUnavailable, etc.)
  - Connection pool optimized
  - Tests end-to-end créés
```

---

## 5. TESTS DE VALIDATION

### 5.1 Checklist Pre-Implementation

- [ ] Lire guide Neo4j complet
- [ ] Analyser code Neo4jClient actuel
- [ ] Analyser code Graphiti integration
- [ ] Vérifier schema Neo4j (Episodes, Entities, Relations)
- [ ] Identifier queries RAG actuelles et problèmes
- [ ] Lire docs Graphiti sur schema

### 5.2 Checklist Implementation

**Phase A: Refactor Neo4jClient**
- [ ] Migrer vers GraphDatabase.driver()
- [ ] Implémenter execute_query() pattern
- [ ] Configurer connection pool
- [ ] Supprimer méthodes inutilisées
- [ ] Créer module neo4j_indexes.py
- [ ] Implémenter create_rag_indexes()
- [ ] Appeler dans startup

**Phase B: Améliorer Queries RAG**
- [ ] Implémenter query_context_fulltext()
- [ ] Implémenter query_entities_related()
- [ ] Implémenter query_context_hybrid()
- [ ] Mettre à jour retrieve_context()
- [ ] Mettre à jour build_rag_prompt()
- [ ] Tester avec questions réelles

**Phase D: Tests**
- [ ] Créer test_neo4j_client.py
- [ ] Créer test_rag_integration.py
- [ ] Créer script test_neo4j_rag.py
- [ ] Exécuter tous les tests
- [ ] Vérifier indexes dans Neo4j Browser

**Phase E: Documentation**
- [ ] Mettre à jour docs/SETUP.md
- [ ] Mettre à jour CURRENT-CONTEXT.md
- [ ] Mettre à jour Devplan/PHASE-0.8-NEO4J-IMPLEMENTATION.md

### 5.3 Tests Fonctionnels

#### Test 1: Connection et Indexes
```bash
# Dans Neo4j Browser (http://localhost:7475)
CALL db.indexes()
YIELD name, type, state
RETURN name, type, state
```

**Résultats Attendus:**
- `episode_content` (FULLTEXT, ONLINE)
- `entity_name_idx` (RANGE, ONLINE)
- `episode_date_idx` (RANGE, ONLINE)
- + Indexes Graphiti (uuid, etc.)

---

#### Test 2: Full-Text Search
```cypher
CALL db.index.fulltext.queryNodes('episode_content', 'plongée niveau 4') 
YIELD node, score
RETURN node.content AS text, node.source_description AS source, score
ORDER BY score DESC
LIMIT 5
```

**Résultats Attendus:**
- 5 chunks pertinents sur "plongée niveau 4"
- Scores décroissants (>0.5 idéalement)
- Text contient "plongée" ou "niveau 4"

---

#### Test 3: Entity Search
```cypher
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS 'niveau'
OPTIONAL MATCH (e)-[r:RELATES_TO]-(related:Entity)
RETURN e.name, e.entity_type, collect(related.name) AS related
LIMIT 5
```

**Résultats Attendus:**
- Entités "Niveau 1", "Niveau 2", "Niveau 4", etc.
- Relationships vers autres entités (prérequis, etc.)

---

#### Test 4: RAG Query via API
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Quels sont les prérequis pour le niveau 4 FFESSM?",
    "stream": false
  }'
```

**Résultats Attendus:**
```json
{
  "question": "Quels sont les prérequis pour le niveau 4 FFESSM?",
  "answer": "Selon les documents FFESSM, les prérequis pour le niveau 4 sont...",
  "context": {
    "episodes": [...],
    "entities": [...]
  },
  "num_sources": 5
}
```

---

### 5.4 Tests de Performance

#### Benchmark Queries
```python
# backend/scripts/benchmark_neo4j.py
import time
from app.integrations.neo4j import neo4j_client

def benchmark_query(name, func, *args):
    start = time.time()
    result = func(*args)
    duration = (time.time() - start) * 1000
    print(f"{name}: {duration:.2f}ms ({len(result)} results)")
    return duration

neo4j_client.connect()

# Benchmark full-text search
benchmark_query(
    "Full-text search",
    neo4j_client.query_context_fulltext,
    "plongée niveau 4",
    5
)

# Benchmark entity search
benchmark_query(
    "Entity search",
    neo4j_client.query_entities_related,
    "niveau",
    2
)

# Benchmark hybrid search
benchmark_query(
    "Hybrid search",
    neo4j_client.query_context_hybrid,
    "niveau 4 prérequis",
    5
)

neo4j_client.close()
```

**Targets de Performance:**
- Full-text search: <100ms
- Entity search: <50ms
- Hybrid search: <150ms
- RAG query complète (avec LLM): <3s

---

## 6. CRITÈRES DE SUCCÈS

### 6.1 Critères Techniques ✅

- [ ] **Connection Neo4j:** Driver connecté, verify_connectivity() réussit
- [ ] **Indexes Créés:** 3 indexes RAG + indexes Graphiti présents
- [ ] **Full-Text Search:** Retourne résultats pertinents (score >0.5)
- [ ] **Entity Search:** Trouve entités + relations (depth=2)
- [ ] **Hybrid Search:** Combine Episodes + Entities correctement
- [ ] **RAG Query:** build_rag_prompt() utilise hybrid context
- [ ] **Error Handling:** Catch ServiceUnavailable, CypherSyntaxError
- [ ] **Performance:** Full-text <100ms, Hybrid <150ms
- [ ] **Tests:** Tous les tests unitaires passent
- [ ] **Documentation:** SETUP.md et CURRENT-CONTEXT.md à jour

### 6.2 Critères Fonctionnels ✅

- [ ] **Query Technique:** "Procédure de remontée d'urgence" retourne chunks pertinents
- [ ] **Query Entité:** "Niveau 4" retourne entité + prérequis
- [ ] **Query Complexe:** "Quels tableaux MFT pour 30m?" retourne chunks + entités tableaux
- [ ] **Citations:** Réponse LLM cite [Chunk 1], [Chunk 2], entités
- [ ] **Pas d'Hallucination:** Si pas de context, LLM dit "pas d'information"
- [ ] **Graphe Visualisé:** API /api/graph/stats retourne nodes + relations count

### 6.3 Critères de Qualité ✅

- [ ] **Code Simplifié:** Moins de async/await inutiles
- [ ] **Best Practices:** Suit guide Neo4j 2025 (execute_query, parameters, etc.)
- [ ] **Logging:** Logs détaillés pour debugging (INFO/ERROR)
- [ ] **Tests Couverts:** Unit tests + integration tests + E2E script
- [ ] **Documentation Claire:** Instructions pour AI agents (SETUP.md)
- [ ] **Pas de Code Mort:** Méthodes inutilisées supprimées

---

## 7. RISQUES ET MITIGATION

### Risque 1: Index Full-Text Pas Créé 🔴
**Symptôme:** `CALL db.index.fulltext.queryNodes()` → "Index not found"

**Cause:** Startup hook échoue, ou index déjà existe avec nom différent

**Mitigation:**
1. Vérifier logs startup: `docker logs backend | grep -i index`
2. Créer index manuellement dans Neo4j Browser
3. Utiliser `IF NOT EXISTS` dans CREATE INDEX

---

### Risque 2: Queries Trop Lentes 🟡
**Symptôme:** Full-text search >1s

**Cause:** Pas d'index, ou trop de résultats

**Mitigation:**
1. PROFILE query dans Neo4j Browser
2. Ajouter LIMIT strict
3. Vérifier index est ONLINE (`CALL db.indexes()`)

---

### Risque 3: Pas de Résultats Retournés 🟡
**Symptôme:** `query_context_hybrid()` → empty []

**Cause:** 
- Pas de documents ingérés
- Full-text search syntax incorrecte
- Schema Graphiti différent

**Mitigation:**
1. Vérifier nodes dans Neo4j: `MATCH (n:Episode) RETURN count(n)`
2. Tester query directement dans Browser
3. Logger query params

---

### Risque 4: Conflit Dual Drivers 🔴
**Symptôme:** Connection timeout, deadlocks

**Cause:** Neo4jClient + Graphiti utilisent 2 drivers différents

**Mitigation:**
1. Option: Utiliser driver interne Graphiti pour queries
2. Option: Garder Neo4jClient READ-ONLY strict
3. Configurer max_connection_pool_size correctement

---

## 8. DÉCISIONS D'ARCHITECTURE

### Décision 1: Neo4jClient Séparé vs Driver Graphiti ✅
**Option A:** Utiliser driver interne Graphiti pour RAG queries
**Option B:** Garder Neo4jClient séparé (READ-ONLY)

**Choix: Option B** ✅
**Raison:**
- Séparation claire: Graphiti = WRITE, Neo4jClient = READ
- Pas de dépendance tight avec Graphiti API
- Plus facile à tester indépendamment
- Connection pool dédié pour queries RAG (performance)

---

### Décision 2: Async vs Sync Driver ✅
**Option A:** Garder AsyncGraphDatabase (tout async)
**Option B:** Migrer vers GraphDatabase (sync avec execute_query)

**Choix: Option B** ✅
**Raison:**
- Guide Neo4j recommande `execute_query()` (simplicity)
- Driver gère async internally (pas besoin async/await partout)
- Code plus simple à lire/maintenir
- Compatible avec sync/async contexts

---

### Décision 3: Vector Search Maintenant vs Plus Tard ✅
**Option A:** Implémenter vector embeddings maintenant
**Option B:** Full-text d'abord, vector en Phase 1+

**Choix: Option B** ✅
**Raison:**
- Full-text search déjà très efficace pour texte
- Embeddings = complexité (model, storage, index)
- Neo4j vector index = Enterprise ou plugin
- Mieux valider full-text d'abord, puis ajouter vector

---

### Décision 4: Indexes à Créer ✅
**Minimum:**
- ✅ Full-text: `episode_content` (CRITICAL pour RAG)
- ✅ Index: `entity_name_idx` (lookup rapide)
- ✅ Index: `episode_date_idx` (filter optionnel)

**Future (Phase 1+):**
- 🔮 Vector: `episode_embeddings` (semantic search)
- 🔮 Composite: `entity_name_type` (multi-property)

---

## 9. TIMELINE ESTIMÉ

| Phase | Durée | Description |
|-------|-------|-------------|
| **A. Refactor Neo4jClient** | 2-3h | Migrer API, créer indexes module |
| **B. Améliorer Queries RAG** | 2-3h | Full-text, entity, hybrid search |
| **C. Vector Embeddings** | ⏸️ SKIP | Reporter à Phase 1+ |
| **D. Tests et Validation** | 1-2h | Unit tests, E2E script, benchmarks |
| **E. Documentation** | 30min | SETUP.md, CURRENT-CONTEXT.md |
| **TOTAL** | **6-9h** | Implémentation complète Phase 0.8 |

---

## 10. RÉFÉRENCES

### Documentation Technique
- ✅ `resources/252027-neo4j-guide-for-ai-agent.md` - Guide complet Neo4j
- ✅ `resources/251020-graphiti-technical-guide.md` - Guide Graphiti
- ✅ `resources/251027-docling-guide-ai-agent.md` - Guide Docling
- ✅ `Devplan/PHASE-0.7-DOCLING-IMPLEMENTATION.md` - Phase précédente

### Code Source Analysé
- ✅ `backend/app/integrations/neo4j.py` - Client Neo4j actuel
- ✅ `backend/app/integrations/graphiti.py` - Intégration Graphiti
- ✅ `backend/app/core/rag.py` - RAG chain
- ✅ `backend/app/api/graph.py` - Graph API endpoints
- ✅ `backend/app/main.py` - Startup/shutdown hooks

### Neo4j Official Docs
- https://neo4j.com/docs/python-manual/current/
- https://neo4j.com/docs/cypher-manual/current/
- https://neo4j.com/docs/operations-manual/current/

---

## 11. NOTES POUR AI AGENT

### Priorités d'Implémentation
1. **PRIORITÉ 1 🔴:** Phase A (Refactor client) + Phase B (Queries RAG)
2. **PRIORITÉ 2 🟡:** Phase D (Tests validation)
3. **PRIORITÉ 3 🟢:** Phase E (Documentation)

### Commandes Clés

```bash
# Rebuild backend après changements
cd /Users/nicozefrench/Dropbox/AI/rag-knowledge-graph-starter
docker compose -f docker/docker-compose.dev.yml build backend
docker compose -f docker/docker-compose.dev.yml up -d backend

# Vérifier logs
docker logs backend -f

# Tester Neo4j
python backend/scripts/test_neo4j_rag.py

# Neo4j Browser
open http://localhost:7475
# Login: neo4j / diveteacher_dev_2025
```

### Validation Finale

```bash
# 1. Vérifier services running
docker ps | grep -E "backend|rag-neo4j"

# 2. Tester connection
curl http://localhost:8000/api/health

# 3. Tester indexes
# Dans Neo4j Browser:
CALL db.indexes()

# 4. Tester RAG query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Niveau 4 FFESSM", "stream": false}'
```

---

**STATUS:** 🔄 EN ATTENTE D'IMPLÉMENTATION  
**NEXT STEP:** Commencer Phase A (Refactor Neo4jClient)

---

*Plan créé le 27 Octobre 2025 par Claude Sonnet 4.5*  
*Basé sur analyse complète de Neo4j guide + code existant*

