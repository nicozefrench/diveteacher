# Graphiti - Guide Technique Complet pour Agent IA

**Version Document**: 1.0  
**Date**: Octobre 2025  
**Repository**: https://github.com/getzep/graphiti  
**Agent Target**: Claude Sonnet 4.5

---

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture et Concepts Fondamentaux](#architecture-et-concepts-fondamentaux)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [API Core et Patterns d'Utilisation](#api-core-et-patterns-dutilisation)
6. [Types d'Entités et Edges Personnalisés](#types-dentités-et-edges-personnalisés)
7. [Capacités de Recherche](#capacités-de-recherche)
8. [Serveur MCP (Model Context Protocol)](#serveur-mcp-model-context-protocol)
9. [API REST Server](#api-rest-server)
10. [Optimisation des Performances](#optimisation-des-performances)
11. [Développement et Contribution](#développement-et-contribution)
12. [Ressources et Documentation](#ressources-et-documentation)

---

## Vue d'ensemble

### Qu'est-ce que Graphiti ?

Graphiti est un framework Python pour construire et interroger des **graphes de connaissances temporellement conscients** (temporal knowledge graphs), spécifiquement conçu pour les agents IA opérant dans des environnements dynamiques.

**Caractéristiques Principales**:
- 🔄 **Mises à jour incrémentales en temps réel** - Intégration immédiate de nouveaux épisodes sans recomputation batch
- 🕒 **Modèle bi-temporel** - Suivi explicite du temps d'occurrence ET d'ingestion des événements
- 🔍 **Recherche hybride efficace** - Combine embeddings sémantiques, BM25 et traversée de graphe
- 🎯 **Ontologie personnalisable** - Définition d'entités via modèles Pydantic
- 📈 **Scalabilité** - Traitement parallèle optimisé pour grandes volumétries
- 📊 **Latence sub-seconde** - P95 à ~300ms (sans appels LLM pendant la recherche)

### Différences avec GraphRAG

| Aspect | GraphRAG (Microsoft) | Graphiti |
|--------|---------------------|----------|
| **Use Case** | Résumé de documents statiques | Gestion de données dynamiques |
| **Data Handling** | Traitement batch | Mises à jour continues et incrémentales |
| **Structure** | Clusters d'entités + résumés communautaires | Données épisodiques + entités sémantiques + communautés |
| **Retrieval** | Résumés LLM séquentiels | Recherche hybride (sémantique, BM25, graphe) |
| **Latency** | Secondes à dizaines de secondes | Typiquement < 1s |
| **Temporal Handling** | Timestamps basiques | Suivi bi-temporel explicite |
| **Contradiction Handling** | Jugements LLM via résumés | Invalidation temporelle des edges |
| **Custom Entities** | Non | Oui, via Pydantic |

**Paper de Référence**: [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956)

---

## Architecture et Concepts Fondamentaux

### Architecture du Graphe

Graphiti utilise un graphe de connaissances **G = (N, E, φ)** avec trois niveaux hiérarchiques:

```
G (Knowledge Graph)
├── Episode Subgraph (Ee, Ne)
│   └── Episodes → Entity Nodes (bidirectional indices)
├── Semantic Entity Subgraph (Es, Ns)
│   └── Entity Nodes ↔ Fact Edges (relationships)
└── Community Subgraph (Ec, Nc)
    └── Entity Communities (detected via graph algorithms)
```

### 1. Episodes

**Définition**: Unité discrète d'information représentant une interaction ou un événement.

**Types d'Episodes**:
```python
from graphiti_core.nodes import EpisodeType

# 3 types supportés
EpisodeType.text      # Texte brut
EpisodeType.json      # Données structurées JSON
EpisodeType.message   # Format conversationnel
```

**Structure**:
```python
episode = {
    'name': 'episode_identifier',
    'content': 'content_text_or_json',
    'type': EpisodeType.text,
    'description': 'context_description',
    'reference_time': datetime.now(),  # Temps de référence de l'événement
    'group_id': 'user_123'  # Pour isolation multi-tenant
}
```

**Extraction depuis un Episode**:
- **Entités**: Noeuds extraits (personnes, lieux, concepts)
- **Relations**: Edges/Facts entre entités
- **Temporal markers**: Métadonnées temporelles

### 2. Entity Nodes (Entités)

**Propriétés Core**:
```python
class EntityNode:
    uuid: str                    # Identifiant unique
    name: str                    # Nom de l'entité
    summary: str                 # Résumé généré
    created_at: datetime         # Timestamp création système
    group_id: Optional[str]      # Isolation multi-tenant
    labels: List[str]            # Labels Neo4j (ex: ["Entity"])
    attributes: Dict             # Attributs personnalisés
    name_embedding: List[float]  # Embedding du nom
```

**Process de Résolution d'Entités**:
1. Extraction via LLM depuis l'épisode
2. Recherche hybride d'entités similaires existantes
3. Résolution via LLM (détection de doublons)
4. Mise à jour ou création de l'entité

### 3. Entity Edges (Relations/Facts)

**Définition**: Représente une relation/fait entre deux entités.

**Structure Temporelle (Bi-Temporal Model)**:
```python
class EntityEdge:
    uuid: str
    source_node_uuid: str        # Entité source
    target_node_uuid: str        # Entité cible
    name: str                    # Type de relation (ex: "WORKS_AT")
    fact: str                    # Phrase complète du fait
    
    # TEMPORAL MODEL - Transaction Time (T')
    created_at: datetime         # Quand le fait a été créé dans le système
    expired_at: Optional[datetime]  # Quand le fait a été invalidé dans le système
    
    # TEMPORAL MODEL - Valid Time (T)
    valid_at: datetime           # Quand le fait était vrai dans le monde réel
    invalid_at: Optional[datetime]  # Quand le fait a cessé d'être vrai
    
    fact_embedding: List[float]  # Embedding pour recherche sémantique
    episodes: List[str]          # UUIDs des épisodes sources
```

**Invalidation Temporelle**:
Lorsqu'un nouveau fait contredit un fait existant:
- Le système utilise le LLM pour détecter les contradictions
- Le fait existant est **invalidé** (pas supprimé)
- `invalid_at` est défini au `valid_at` du fait invalidant
- Préserve l'historique complet

### 4. Communities

**Définition**: Groupes d'entités détectés via algorithmes de détection de communauté (Louvain, etc.).

**Utilité**:
- Organisation hiérarchique des entités
- Amélioration des recherches contextuelles
- Résumés de haut niveau

---

## Installation

### Prérequis

**Système**:
- Python 3.10+
- Base de données graphe (au choix):
  - Neo4j 5.26+
  - FalkorDB 1.1.2+
  - Kuzu 0.11.2+
  - Amazon Neptune Database/Analytics + OpenSearch Serverless

**APIs**:
- Clé API OpenAI (par défaut) ou autre provider LLM
- Optionnel: Anthropic, Groq, Google Gemini

### Installation Base

```bash
# Via pip
pip install graphiti-core

# Via uv (recommandé)
uv add graphiti-core
```

### Installation avec Database Backend

```bash
# Pour FalkorDB
pip install graphiti-core[falkordb]
# ou
uv add graphiti-core[falkordb]

# Pour Kuzu
pip install graphiti-core[kuzu]

# Pour Amazon Neptune
pip install graphiti-core[neptune]
```

### Installation avec LLM Providers

```bash
# Anthropic
pip install graphiti-core[anthropic]

# Google Gemini
pip install graphiti-core[google-genai]

# Groq
pip install graphiti-core[groq]

# Combinaison multiple
pip install graphiti-core[anthropic,google-genai,falkordb]
```

### Installation Neo4j

**Option 1: Neo4j Desktop** (recommandé pour dev)
- Télécharger: https://neo4j.com/download/
- Interface graphique pour gérer instances et databases

**Option 2: Docker**
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your_password \
    neo4j:latest
```

**Option 3: FalkorDB via Docker**
```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
```

---

## Configuration

### Variables d'Environnement Core

```bash
# LLM Provider (OpenAI par défaut)
export OPENAI_API_KEY=your_openai_api_key

# Neo4j Connection
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password

# FalkorDB Connection
export FALKORDB_URI=falkor://localhost:6379

# Amazon Neptune
export NEPTUNE_HOST=neptune-db://<cluster-endpoint>  # ou neptune-graph://<graph-id>
export NEPTUNE_PORT=8182  # optionnel
export AOSS_HOST=<opensearch-serverless-host>
export AOSS_PORT=443  # optionnel

# Performance Tuning
export SEMAPHORE_LIMIT=10  # Limite de concurrence (défaut: 10)

# Telemetry (opt-out)
export GRAPHITI_TELEMETRY_ENABLED=false
```

### Configuration Database Driver

#### Neo4j

```python
from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver

# Driver avec database custom
driver = Neo4jDriver(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="my_custom_database"  # Défaut: "neo4j"
)

graphiti = Graphiti(graph_driver=driver)
```

#### FalkorDB

```python
from graphiti_core.driver.falkordb_driver import FalkorDriver

driver = FalkorDriver(
    host="localhost",
    port=6379,
    username="falkor_user",  # Optionnel
    password="falkor_password",  # Optionnel
    database="my_custom_graph"  # Défaut: "default_db"
)

graphiti = Graphiti(graph_driver=driver)
```

#### Kuzu

```python
from graphiti_core.driver.kuzu_driver import KuzuDriver

driver = KuzuDriver(db="/tmp/graphiti.kuzu")
graphiti = Graphiti(graph_driver=driver)
```

#### Amazon Neptune

```python
from graphiti_core.driver.neptune_driver import NeptuneDriver

driver = NeptuneDriver(
    host="neptune-db://<cluster-endpoint>",  # ou neptune-graph://
    aoss_host="<opensearch-serverless-host>",
    port=8182,  # Défaut
    aoss_port=443  # Défaut
)

graphiti = Graphiti(graph_driver=driver)
```

### Configuration LLM Provider

#### OpenAI (Défaut)

```python
from graphiti_core import Graphiti

# Configuration simple (utilise OPENAI_API_KEY)
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password"
)
```

#### Azure OpenAI

```python
from openai import AsyncAzureOpenAI
from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMConfig, OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient

# Configuration Azure
api_key = "<your-api-key>"
api_version = "2024-02-01"
llm_endpoint = "https://your-llm-resource.openai.azure.com/"
embedding_endpoint = "https://your-embedding-resource.openai.azure.com/"

# Clients Azure séparés
llm_client_azure = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=llm_endpoint
)

embedding_client_azure = AsyncAzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=embedding_endpoint
)

# Config LLM
azure_llm_config = LLMConfig(
    small_model="gpt-4.1-nano",  # Nom de déploiement Azure
    model="gpt-4.1-mini",        # Nom de déploiement Azure
)

# Init Graphiti
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=OpenAIClient(
        config=azure_llm_config,
        client=llm_client_azure
    ),
    embedder=OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            embedding_model="text-embedding-3-small-deployment"
        ),
        client=embedding_client_azure
    ),
    cross_encoder=OpenAIRerankerClient(
        config=LLMConfig(model=azure_llm_config.small_model),
        client=llm_client_azure
    )
)
```

**⚠️ IMPORTANT Azure**: Nécessite opt-in API v1 pour structured outputs. Voir: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle

#### Google Gemini

```bash
uv add "graphiti-core[google-genai]"
```

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

api_key = "<your-google-api-key>"

graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=GeminiClient(
        config=LLMConfig(
            api_key=api_key,
            model="gemini-2.0-flash"
        )
    ),
    embedder=GeminiEmbedder(
        config=GeminiEmbedderConfig(
            api_key=api_key,
            embedding_model="embedding-001"
        )
    ),
    cross_encoder=GeminiRerankerClient(
        config=LLMConfig(
            api_key=api_key,
            model="gemini-2.5-flash-lite-preview-06-17"
        )
    )
)
```

#### Ollama (Local LLMs)

```bash
# Installer les modèles
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text

# Lancer Ollama
ollama serve
```

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient

llm_config = LLMConfig(
    api_key="ollama",  # Placeholder
    model="deepseek-r1:7b",
    small_model="deepseek-r1:7b",
    base_url="http://localhost:11434/v1"
)

llm_client = OpenAIGenericClient(config=llm_config)

graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=llm_client,
    embedder=OpenAIEmbedder(
        config=OpenAIEmbedderConfig(
            api_key="ollama",
            embedding_model="nomic-embed-text",
            embedding_dim=768,
            base_url="http://localhost:11434/v1"
        )
    ),
    cross_encoder=OpenAIRerankerClient(
        client=llm_client,
        config=llm_config
    )
)
```

---

## API Core et Patterns d'Utilisation

### Pattern Basique d'Utilisation

```python
import asyncio
import logging
from datetime import datetime, timezone
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

logging.basicConfig(level=logging.INFO)

async def main():
    # 1. INITIALIZATION
    graphiti = Graphiti(
        "bolt://localhost:7687",
        "neo4j",
        "password"
    )
    
    # 2. BUILD INDICES (une seule fois)
    await graphiti.build_indices_and_constraints()
    
    # 3. ADD EPISODES
    episodes = [
        {
            'content': 'Kamala Harris was the attorney general of California. '
                      'She was previously the district attorney for San Francisco.',
            'type': EpisodeType.text,
            'description': 'podcast transcript'
        },
        {
            'content': 'As AG, Harris was in office from January 3, 2011 – January 3, 2017',
            'type': EpisodeType.text,
            'description': 'podcast transcript'
        },
        {
            'content': {
                'name': 'Gavin Newsom',
                'position': 'Governor',
                'state': 'California'
            },
            'type': EpisodeType.json,
            'description': 'podcast metadata'
        }
    ]
    
    for i, episode in enumerate(episodes):
        await graphiti.add_episode(
            name=f"episode_{i}",
            episode_body=episode['content'],
            source=episode['type'],
            source_description=episode['description'],
            reference_time=datetime.now(timezone.utc)
        )
    
    # 4. BUILD COMMUNITIES (optionnel, pour meilleure organisation)
    await graphiti.build_communities()
    
    # 5. SEARCH
    results = await graphiti.search('Who was the California Attorney General?')
    
    for edge in results:
        print(f"Fact: {edge.fact}")
        print(f"Relation: {edge.name}")
        print(f"Valid: {edge.valid_at} -> {edge.invalid_at}")
    
    # 6. CLOSE
    await graphiti.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Méthodes Core de l'API Graphiti

#### `build_indices_and_constraints()`

```python
await graphiti.build_indices_and_constraints()
```
- **Usage**: À appeler **une seule fois** lors de la première initialisation
- **Effet**: Crée les indices et contraintes nécessaires dans la database
- **Requis**: Avant toute autre opération

#### `add_episode()`

```python
await graphiti.add_episode(
    name: str,                      # Identifiant de l'épisode
    episode_body: str | dict,       # Contenu (texte ou JSON)
    source: EpisodeType,            # text, json, ou message
    source_description: str,        # Description du contexte
    reference_time: datetime,       # Timestamp de référence de l'événement
    group_id: Optional[str] = None, # Pour isolation multi-tenant
    entity_types: Optional[List[Type[BaseModel]]] = None,  # Types custom
    edge_types: Optional[List[Type[BaseModel]]] = None     # Types custom
)
```

**Processus interne**:
1. Extraction d'entités via LLM
2. Résolution d'entités (dédoublonnage)
3. Extraction de facts/edges
4. Dédoublonnage d'edges
5. Détection de contradictions et invalidation temporelle
6. Insertion dans le graphe

#### `search()`

```python
results = await graphiti.search(
    query: str,                              # Requête de recherche
    num_results: int = 10,                   # Nombre de résultats
    group_ids: Optional[List[str]] = None,   # Filtrer par group_id
    center_node_uuid: Optional[str] = None,  # Pour reranking par distance
    search_config: Optional[SearchConfig] = None  # Config avancée
)
# Returns: List[EntityEdge]
```

**Méthode de recherche**: Hybrid Search (RRF - Reciprocal Rank Fusion)
- Recherche sémantique (embeddings)
- Recherche BM25 (full-text)
- Fusion et reranking

#### `search_nodes()`

```python
nodes = await graphiti.search_nodes(
    query: str,
    num_results: int = 10,
    group_ids: Optional[List[str]] = None,
    search_config: Optional[SearchConfig] = None
)
# Returns: List[EntityNode]
```

Recherche directement les noeuds d'entités (au lieu des edges).

#### `build_communities()`

```python
await graphiti.build_communities()
```
- Détecte et construit les communautés d'entités
- Améliore les recherches contextuelles
- À appeler après ingestion de plusieurs épisodes

#### `close()`

```python
await graphiti.close()
```
Ferme proprement les connexions database.

---

## Types d'Entités et Edges Personnalisés

### Définition via Pydantic

**Exemple - Types d'Entités Custom**:

```python
from pydantic import BaseModel, Field
from typing import Optional

class Person(BaseModel):
    """Represents a person entity"""
    full_name: str = Field(description="Full name of the person")
    age: Optional[int] = Field(None, description="Age in years")
    occupation: Optional[str] = Field(None, description="Current job/role")
    email: Optional[str] = Field(None, description="Email address")

class Organization(BaseModel):
    """Represents an organization or company"""
    name: str = Field(description="Organization name")
    industry: Optional[str] = Field(None, description="Industry sector")
    founded_year: Optional[int] = Field(None, description="Year founded")
    headquarters: Optional[str] = Field(None, description="Location of HQ")

class Project(BaseModel):
    """Represents a project or initiative"""
    title: str = Field(description="Project title")
    status: Optional[str] = Field(None, description="Current status")
    deadline: Optional[str] = Field(None, description="Target deadline")
```

**Exemple - Types d'Edges Custom**:

```python
class WorksAt(BaseModel):
    """Represents employment relationship"""
    role: str = Field(description="Job title/role")
    start_date: Optional[str] = Field(None, description="Start date")
    department: Optional[str] = Field(None, description="Department")

class LeadsProject(BaseModel):
    """Represents project leadership"""
    responsibility: str = Field(description="Leadership responsibility")
    budget: Optional[float] = Field(None, description="Budget in USD")
```

### Utilisation des Types Custom

```python
from graphiti_core.nodes import EpisodeType

# Liste des types d'entités
entity_types = [Person, Organization, Project]

# Liste des types d'edges
edge_types = [WorksAt, LeadsProject]

# Ajout d'épisode avec types custom
await graphiti.add_episode(
    name="company_update",
    episode_body="""
        Alice Johnson works at TechCorp as a Senior Engineer. 
        She leads the AI Platform project with a budget of $2M.
        The project deadline is December 2025.
    """,
    source=EpisodeType.text,
    source_description="company records",
    reference_time=datetime.now(timezone.utc),
    entity_types=entity_types,
    edge_types=edge_types
)
```

### Recherche Filtrée par Types

```python
from graphiti_core.search.search_filters import SearchFilters

# Filtrer uniquement les personnes
filters = SearchFilters(
    entity_labels=["Person"]  # Correspond au nom de la classe
)

results = await graphiti.search(
    query="Who works on AI projects?",
    num_results=10,
    search_config=SearchConfig(filters=filters)
)
```

### ⚠️ Limitations Actuelles (v0.17.x)

**Issue connue**: Les propriétés custom ne sont pas toujours persistées dans Neo4j
- Les labels spécifiques (`:Person`, `:Organization`) peuvent être absents
- Seules les propriétés standard sont sauvegardées
- Référence: https://github.com/getzep/graphiti/issues/567
- **Workaround**: Surveiller les updates futures ou contribuer au fix

---

## Capacités de Recherche

### Types de Recherche

#### 1. Hybrid Search (Par Défaut)

Combine 3 méthodes:
- **Semantic Search**: Embeddings + cosine similarity
- **Full-Text Search**: BM25
- **Fusion**: Reciprocal Rank Fusion (RRF)

```python
results = await graphiti.search(
    query="California officials",
    num_results=10
)
```

#### 2. Search Recipes (Configurations Prédéfinies)

```python
from graphiti_core.search.search_config_recipes import (
    NODE_HYBRID_SEARCH_RRF,  # Recherche de noeuds avec RRF
    EDGE_HYBRID_SEARCH_RRF,  # Recherche d'edges avec RRF
    # ... autres recipes disponibles
)

nodes = await graphiti.search_nodes(
    query="software engineers",
    num_results=10,
    search_config=NODE_HYBRID_SEARCH_RRF
)
```

#### 3. Reranking Strategies

**Node Distance Reranking**: Réordonne par distance graphe depuis un noeud central

```python
# 1. Obtenir un résultat initial
initial_results = await graphiti.search("tech companies", num_results=5)
center_node_uuid = initial_results[0].source_node_uuid

# 2. Reranker par distance depuis ce noeud
reranked_results = await graphiti.search(
    query="tech companies",
    num_results=20,
    center_node_uuid=center_node_uuid
)
```

**Autres stratégies de reranking**:
- **RRF (Reciprocal Rank Fusion)**: Défaut, rapide
- **MMR (Maximal Marginal Relevance)**: Diversité des résultats
- **EpisodeMentions**: Par fréquence de mentions dans épisodes
- **CrossEncoder**: Meilleure qualité mais plus lent (appel LLM)

### SearchConfig Avancé

```python
from graphiti_core.search.search_config import SearchConfig
from graphiti_core.search.search_filters import SearchFilters
from graphiti_core.search.search_methods import SearchMethod
from graphiti_core.search.reranker import RerankMethod

config = SearchConfig(
    # Méthodes de recherche
    search_methods=[
        SearchMethod.cosine_similarity,
        SearchMethod.bm25,
        SearchMethod.bfs  # Breadth-First Search
    ],
    
    # Nombre de résultats par méthode
    num_results=50,
    
    # Reranking
    reranker=RerankMethod.rrf,
    
    # Filtres
    filters=SearchFilters(
        # Filtrer par labels
        entity_labels=["Person", "Organization"],
        
        # Filtrer par plage temporelle (valid_at)
        start_date=datetime(2020, 1, 1),
        end_date=datetime(2024, 12, 31),
        
        # Filtrer par group_id
        group_ids=["tenant_123"]
    )
)

results = await graphiti.search(
    query="project leaders",
    num_results=10,
    search_config=config
)
```

### Recherche Temporelle

**Point-in-Time Query**: Retrouver l'état du graphe à un moment précis

```python
from datetime import datetime

# Rechercher ce qui était vrai au 1er janvier 2023
filters = SearchFilters(
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 1)
)

results = await graphiti.search(
    query="California officials",
    search_config=SearchConfig(filters=filters)
)

# Les résultats ne contiendront que des edges:
# - Avec valid_at <= 2023-01-01
# - Sans invalid_at OU invalid_at > 2023-01-01
```

---

## Serveur MCP (Model Context Protocol)

### Présentation

Le serveur MCP Graphiti expose les capacités du framework via le protocole MCP, permettant aux assistants IA (Claude Desktop, Cursor, etc.) d'interagir avec le graphe de connaissances.

**Documentation**: https://github.com/getzep/graphiti/blob/main/mcp_server/README.md

### Fonctionnalités Exposées

**Tools MCP disponibles**:
1. `add_episode` - Ajouter un épisode au graphe
2. `search_nodes` - Rechercher des noeuds d'entités
3. `search_facts` - Rechercher des facts/edges
4. `delete_entity_edge` - Supprimer un edge
5. `delete_episode` - Supprimer un épisode
6. `retrieve_episodes` - Récupérer des épisodes
7. `get_entity` - Obtenir une entité par UUID
8. Gestion de groupes (group management)
9. Opérations de maintenance

### Installation

```bash
# Installer uv (gestionnaire de packages)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Cloner le repo
git clone https://github.com/getzep/graphiti.git
cd graphiti/mcp_server
```

### Configuration Claude Desktop

**Fichier**: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "graphiti": {
      "command": "uv",
      "args": [
        "run",
        "/ABSOLUTE/PATH/TO/graphiti/mcp_server/graphiti_mcp_server.py",
        "--transport",
        "sse"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_password",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "MODEL_NAME": "gpt-4.1-mini",
        "GRAPHITI_TELEMETRY_ENABLED": "false"
      }
    }
  }
}
```

### Configuration Cursor

**Fichier**: `.cursor/mcp.json` dans votre projet

```json
{
  "mcpServers": {
    "graphiti": {
      "command": "uv",
      "args": [
        "run",
        "/ABSOLUTE/PATH/TO/graphiti/mcp_server/graphiti_mcp_server.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "your_password",
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "MODEL_NAME": "gpt-4.1-mini"
      }
    }
  }
}
```

### Déploiement Docker

**Fichier**: `.env`
```bash
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4.1-mini
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

**Fichier**: `docker-compose.yml`
```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/your_neo4j_password
    volumes:
      - neo4j_data:/data

  graphiti-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      MODEL_NAME: ${MODEL_NAME}
      NEO4J_URI: ${NEO4J_URI}
      NEO4J_USER: ${NEO4J_USER}
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
    depends_on:
      - neo4j

volumes:
  neo4j_data:
```

```bash
docker-compose up -d
```

### Utilisation depuis Claude

Une fois configuré, Claude peut interagir avec Graphiti:

```
User: "Remember that I work at TechCorp as a Senior Engineer on the AI Platform project"

Claude: [Utilise automatiquement l'outil add_episode du MCP server]

User: "What do you know about my work?"

Claude: [Utilise search_facts pour récupérer les informations]
```

---

## API REST Server

### Présentation

Le répertoire `server/` contient une API REST FastAPI pour interagir avec Graphiti via HTTP.

**Documentation**: https://github.com/getzep/graphiti/blob/main/server/README.md

### Installation

```bash
cd graphiti/server
pip install -r requirements.txt
```

### Configuration

**Fichier**: `.env` ou variables d'environnement

```bash
# Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LLM
OPENAI_API_KEY=your_key
MODEL_NAME=gpt-4.1-mini

# Server
HOST=0.0.0.0
PORT=8000
```

### Lancement

```bash
cd server
uvicorn graph_service.main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints Principaux

**Documentation Auto-générée**: http://localhost:8000/docs (Swagger UI)

**Ingestion**:
- `POST /episodes` - Ajouter un épisode
- `DELETE /episodes/{uuid}` - Supprimer un épisode

**Recherche**:
- `GET /search` - Recherche hybride d'edges
- `GET /search/nodes` - Recherche de noeuds

**Entités**:
- `GET /entities/{uuid}` - Obtenir une entité
- `GET /entities` - Lister les entités

**Graphe**:
- `POST /communities` - Construire les communautés
- `GET /health` - Status du service

### Exemple d'Utilisation

```python
import requests

BASE_URL = "http://localhost:8000"

# Ajouter un épisode
response = requests.post(
    f"{BASE_URL}/episodes",
    json={
        "name": "meeting_notes",
        "content": "Alice discussed the Q4 roadmap with Bob",
        "source": "text",
        "source_description": "meeting notes",
        "group_id": "team_alpha"
    }
)

print(response.json())

# Rechercher
response = requests.get(
    f"{BASE_URL}/search",
    params={
        "query": "Q4 roadmap",
        "num_results": 10
    }
)

results = response.json()
for edge in results["edges"]:
    print(edge["fact"])
```

---

## Optimisation des Performances

### 1. Ajuster la Concurrence (SEMAPHORE_LIMIT)

**Problème**: Graphiti utilise des appels LLM concurrents. Par défaut, `SEMAPHORE_LIMIT=10` pour éviter les erreurs 429 (rate limit).

**Solution**:
```bash
# Si vous avez un tier avec plus de throughput
export SEMAPHORE_LIMIT=50

# Si vous rencontrez des 429
export SEMAPHORE_LIMIT=5
```

**Impact**: Directement sur la vitesse d'ingestion d'épisodes.

### 2. Batch Processing d'Episodes

```python
import asyncio

async def ingest_batch(graphiti, episodes_batch):
    tasks = []
    for episode in episodes_batch:
        task = graphiti.add_episode(
            name=episode['name'],
            episode_body=episode['content'],
            source=episode['type'],
            source_description=episode['description'],
            reference_time=episode['timestamp']
        )
        tasks.append(task)
    
    # Exécute en parallèle (limité par SEMAPHORE_LIMIT)
    await asyncio.gather(*tasks)

# Usage
await ingest_batch(graphiti, batch_of_100_episodes)
```

### 3. Optimisation Neo4j

**Indices recommandés** (créés automatiquement par `build_indices_and_constraints()`):
- Index sur `uuid` pour EntityNode et EntityEdge
- Index sur `name_embedding` pour recherche vectorielle
- Index sur `fact_embedding` pour recherche vectorielle
- Contrainte d'unicité sur `uuid`

**Configuration Neo4j** (`neo4j.conf`):
```ini
# Augmenter la mémoire heap
dbms.memory.heap.initial_size=2G
dbms.memory.heap.max_size=4G

# Augmenter le page cache
dbms.memory.pagecache.size=2G

# Pour recherches parallèles (Enterprise Edition uniquement)
# dbms.cypher.parallel_runtime_enabled=true
```

### 4. Stratégies de Recherche

**Trade-offs**:
- **RRF (Reciprocal Rank Fusion)**: ⚡ Rapide, bonne qualité
- **MMR (Maximal Marginal Relevance)**: 🎯 Diversité, moyen
- **NodeDistance**: 🔗 Contexte graphe, moyen
- **CrossEncoder**: 🎖️ Meilleure qualité, ⏱️ plus lent (appel LLM)

**Recommandation**: Utiliser RRF par défaut, CrossEncoder pour queries critiques.

### 5. Caching et Réutilisation

```python
# Réutiliser la connexion Graphiti
class GraphitiManager:
    _instance = None
    
    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = Graphiti(
                "bolt://localhost:7687",
                "neo4j",
                "password"
            )
            await cls._instance.build_indices_and_constraints()
        return cls._instance
    
    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None
```

---

## Développement et Contribution

### Structure du Repository

```
graphiti/
├── graphiti_core/          # Package core
│   ├── llm_client/         # Clients LLM (OpenAI, Gemini, etc.)
│   ├── embedder/           # Embedders (OpenAI, Voyage, etc.)
│   ├── driver/             # Drivers database (Neo4j, FalkorDB, etc.)
│   ├── search/             # Moteur de recherche
│   ├── nodes.py            # Définitions EntityNode, EntityEdge, Episode
│   ├── graphiti.py         # Classe principale Graphiti
│   └── ...
├── examples/               # Exemples d'utilisation
│   └── quickstart/         # Quickstart avec Neo4j, FalkorDB, Neptune
├── mcp_server/             # Serveur MCP
├── server/                 # API REST FastAPI
├── tests/                  # Tests unitaires et d'intégration
├── pyproject.toml          # Configuration du projet
└── README.md
```

### Setup Développement

```bash
# Cloner le repo
git clone https://github.com/getzep/graphiti.git
cd graphiti

# Installer avec dépendances dev
uv pip install -e ".[dev]"

# Ou avec pip
pip install -e ".[dev]"

# Installer pre-commit hooks
pre-commit install
```

### Lancer les Tests

```bash
# Tests unitaires
pytest tests/

# Tests avec coverage
pytest --cov=graphiti_core tests/

# Tests spécifiques
pytest tests/test_graphiti.py::test_add_episode
```

### Contribution Guidelines

**Référence**: https://github.com/getzep/graphiti/blob/main/CONTRIBUTING.md

**Process**:
1. Fork le repository
2. Créer une branche feature: `git checkout -b feature/ma-nouvelle-fonctionnalite`
3. Faire les modifications avec tests
4. Commit: `git commit -m "feat: ajout de X"`
5. Push: `git push origin feature/ma-nouvelle-fonctionnalite`
6. Ouvrir une Pull Request

**Standards**:
- Type hints Python obligatoires
- Docstrings style Google
- Tests pour toute nouvelle fonctionnalité
- Pre-commit hooks doivent passer (black, ruff, mypy)

### Roadmap Actuel

**En développement**:
1. **Custom graph schemas**: Permettre schémas de noeuds/edges entièrement custom
2. **Enhanced retrieval**: Options de recherche plus robustes
3. **Test coverage**: Augmenter la couverture de tests
4. **MCP Server improvements**: Nouvelles fonctionnalités MCP

---

## Ressources et Documentation

### Liens Officiels

**Repository Principal**:
- GitHub: https://github.com/getzep/graphiti
- PyPI: https://pypi.org/project/graphiti-core/

**Documentation**:
- Docs Officielles: https://help.getzep.com/graphiti/
- Quick Start: https://help.getzep.com/graphiti/getting-started/quick-start
- API Reference: https://help.getzep.com/graphiti/api-reference
- Custom Entities: https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types

**Exemples**:
- Quickstart: https://github.com/getzep/graphiti/tree/main/examples/quickstart
- Custom Entities: https://github.com/getzep/graphiti/tree/main/examples/custom_entity_edge_types

**MCP Server**:
- MCP README: https://github.com/getzep/graphiti/blob/main/mcp_server/README.md
- MCP Documentation: https://help.getzep.com/graphiti/getting-started/mcp-server

**API REST**:
- Server README: https://github.com/getzep/graphiti/blob/main/server/README.md

### Papers et Articles

**Research Paper**:
- [Zep: A Temporal Knowledge Graph Architecture for Agent Memory (arXiv)](https://arxiv.org/abs/2501.13956)
- [Zep: A Temporal Knowledge Graph Architecture for Agent Memory (HTML)](https://arxiv.org/html/2501.13956v1)
- Blog Post: https://blog.getzep.com/state-of-the-art-agent-memory/

**Articles Techniques**:
- [Graphiti: Temporal Knowledge Graphs for Agentic Apps](https://blog.getzep.com/graphiti-knowledge-graphs-for-agents/)
- [Graphiti: Knowledge Graph Memory for an Agentic World (Neo4j)](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)

### Communauté

**Discord**:
- Zep Discord: https://discord.com/invite/W8Kw6bsgXQ
- Channel: `#Graphiti`

**GitHub**:
- Issues: https://github.com/getzep/graphiti/issues
- Discussions: https://github.com/getzep/graphiti/discussions
- Contributing: https://github.com/getzep/graphiti/blob/main/CONTRIBUTING.md

### Bases de Données Supportées

**Neo4j**:
- Neo4j Desktop: https://neo4j.com/download/
- Neo4j Documentation: https://neo4j.com/docs/

**FalkorDB**:
- Website: https://falkordb.com/
- Documentation: https://docs.falkordb.com/

**Kuzu**:
- Website: https://kuzudb.com/
- Documentation: https://kuzudb.com/docs/

**Amazon Neptune**:
- Documentation: https://docs.aws.amazon.com/neptune/
- Developer Resources: https://aws.amazon.com/neptune/developer-resources/

### LLM Providers

**OpenAI**:
- API Docs: https://platform.openai.com/docs/
- Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs

**Azure OpenAI**:
- API Lifecycle: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle

**Google Gemini**:
- API Docs: https://ai.google.dev/docs
- Gemini Models: https://ai.google.dev/models/gemini

**Anthropic**:
- API Docs: https://docs.anthropic.com/

**Ollama**:
- Website: https://ollama.ai/
- Models: https://ollama.ai/library

---

## Annexes

### Checklist d'Installation

- [ ] Python 3.10+ installé
- [ ] Database graphe installée et running (Neo4j/FalkorDB/Kuzu/Neptune)
- [ ] Clé API LLM configurée (OPENAI_API_KEY ou autre)
- [ ] `graphiti-core` installé avec extras appropriés
- [ ] Variables d'environnement configurées
- [ ] Test de connexion database réussi
- [ ] `build_indices_and_constraints()` exécuté

### Checklist de Production

- [ ] SEMAPHORE_LIMIT ajusté selon throughput LLM
- [ ] Database backups configurés
- [ ] Monitoring Neo4j configuré (si applicable)
- [ ] Logging configuré (niveau INFO minimum)
- [ ] Group IDs utilisés pour isolation multi-tenant
- [ ] Telemetry désactivée si nécessaire
- [ ] Secrets managés via vault (pas en env vars hardcodées)
- [ ] Rate limits LLM provider vérifiés
- [ ] Stratégie de reranking choisie (RRF vs CrossEncoder)
- [ ] Build communities exécuté régulièrement

### Troubleshooting Commun

**Problème**: `Graph not found: default_db`
```python
# Solution: Spécifier le bon nom de database
driver = Neo4jDriver(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="neo4j"  # Pas "default_db"
)
```

**Problème**: Erreurs 429 (Rate Limit) du LLM
```bash
# Solution: Réduire la concurrence
export SEMAPHORE_LIMIT=5
```

**Problème**: Recherches lentes
```python
# Solution 1: Utiliser RRF au lieu de CrossEncoder
config = SearchConfig(reranker=RerankMethod.rrf)

# Solution 2: Réduire num_results
results = await graphiti.search(query, num_results=5)
```

**Problème**: Types custom non persistés dans Neo4j
```python
# Workaround: Utiliser attributes dict pour stocker données custom
# Surveiller l'issue: https://github.com/getzep/graphiti/issues/567
```

**Problème**: Structured Outputs échouent avec Azure OpenAI
```
# Solution: Vérifier que le déploiement a opt-in pour API v1
# Voir: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle
```

---

## Notes Finales pour l'Agent IA

### Principes de Développement

1. **Toujours utiliser des contexts managers async** pour les connexions
2. **Utiliser des group_ids** pour isolation multi-tenant dès le début
3. **Penser temporellement** - chaque fait a une durée de validité
4. **Privilégier la recherche hybride (RRF)** pour le meilleur rapport qualité/performance
5. **Construire les communities régulièrement** pour améliorer les recherches contextuelles
6. **Documenter les types custom** avec des descriptions Field() claires

### Patterns Anti-patterns

**❌ À Éviter**:
- Appeler `build_indices_and_constraints()` à chaque démarrage
- Ignorer les group_ids dans une application multi-utilisateur
- Utiliser CrossEncoder pour toutes les recherches (lent)
- Stocker des données sensibles directement dans les facts
- Créer de nouveaux drivers Graphiti pour chaque requête

**✅ À Faire**:
- Réutiliser une instance Graphiti globale
- Fermer proprement les connexions avec `await graphiti.close()`
- Utiliser des types custom pour structurer le domaine
- Exploiter la recherche temporelle pour queries historiques
- Monitorer les rate limits LLM et ajuster SEMAPHORE_LIMIT

### Métriques de Performance Cibles

- **Ingestion**: ~1-5 secondes par épisode (dépend de SEMAPHORE_LIMIT et LLM)
- **Recherche**: < 1 seconde (P95 à 300ms)
- **Build Communities**: Variable selon taille du graphe

---

**Dernière Mise à Jour**: Octobre 2025  
**Version Graphiti**: 0.17.x  
**Maintainer**: Zep AI (https://www.getzep.com)  
**License**: Même licence que le projet parent Graphiti

