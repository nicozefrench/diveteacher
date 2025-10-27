# Neo4j Comprehensive Guide for AI Agent Development

**Version:** 2025-10 | **Target:** Claude Sonnet 4.5 AI Agent  
**Purpose:** Implementation, debugging, and usage of Neo4j in development projects

---

## Table of Contents

1. [Introduction to Neo4j](#introduction-to-neo4j)
2. [Installation & Setup](#installation--setup)
3. [Core Concepts](#core-concepts)
4. [Python Driver Integration](#python-driver-integration)
5. [Cypher Query Language](#cypher-query-language)
6. [Common Patterns & Best Practices](#common-patterns--best-practices)
7. [Debugging & Troubleshooting](#debugging--troubleshooting)
8. [Performance Optimization](#performance-optimization)
9. [Security Considerations](#security-considerations)
10. [Resource Links](#resource-links)

---

## Introduction to Neo4j

### What is Neo4j?

Neo4j is a native graph database management system (DBMS) that uses nodes, relationships, and properties to represent and store data. Unlike traditional relational databases that use tables, Neo4j's property graph model is optimized for connected data and relationship queries.

### Key Characteristics

- **ACID Compliant:** Full transactional support
- **Native Graph Storage:** Data stored as nodes and relationships, not mapped from tables
- **Cypher Query Language:** Declarative, SQL-like language optimized for graphs
- **High Performance:** O(1) relationship traversal regardless of graph size
- **Schema-Flexible:** No rigid schema requirements, but supports optional constraints

### When to Use Neo4j

**Ideal for:**
- Social networks and recommendation engines
- Knowledge graphs and semantic web applications
- Fraud detection and pattern recognition
- Network and IT infrastructure management
- Identity and access management
- Real-time recommendations

**Not ideal for:**
- Simple tabular data without relationships
- Large-scale analytics on non-connected data
- Document storage without relationships

---

## Installation & Setup

### Python Environment Setup

```bash
# Install the official Neo4j Python driver (current package name)
pip install neo4j

# For better performance, optionally install Rust extensions
pip install neo4j[rust]
```

**Important:** The old package name `neo4j-driver` is deprecated and will receive no further updates starting with version 6.0.0. Always use `neo4j`.

### Supported Python Versions (as of 2025)
- Python 3.13 ✓
- Python 3.12 ✓
- Python 3.11 ✓
- Python 3.10 ✓

### Neo4j Server Setup Options

#### Option 1: Neo4j Desktop (Development)
Download from: https://neo4j.com/download/

#### Option 2: Docker (Recommended for Development)
```bash
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -e NEO4J_AUTH=neo4j/your_password \
    neo4j:latest
```

#### Option 3: Neo4j Aura (Cloud - Production Ready)
- Managed cloud service
- Free tier available
- Visit: https://neo4j.com/cloud/aura/

#### Option 4: Neo4j Sandbox (Quick Testing)
- Free temporary instances
- Pre-loaded datasets available
- Visit: https://sandbox.neo4j.com

### Connection Configuration

**Default Connection Details:**
- **Bolt Protocol URI:** `neo4j://localhost:7687` (or `bolt://localhost:7687`)
- **HTTP URI:** `http://localhost:7474` (Browser interface)
- **Default Username:** `neo4j`
- **Default Password:** Must be changed on first login

---

## Core Concepts

### 1. Graph Model Components

#### Nodes
Nodes represent entities in your graph. They are the "nouns" of your data model.

**Characteristics:**
- Can have zero or more labels (e.g., `:Person`, `:Movie`)
- Can have zero or more properties (key-value pairs)
- Unique identifier automatically assigned

**Example:**
```cypher
(:Person {name: "Alice", age: 30, email: "alice@example.com"})
```

#### Relationships
Relationships connect nodes and represent the associations between them. They are the "verbs" of your data model.

**Characteristics:**
- Must have exactly one type (e.g., `:KNOWS`, `:ACTED_IN`)
- Always have a direction (though queries can ignore it)
- Can have zero or more properties
- Must have a start node and an end node

**Best Practice:** Use UPPERCASE_WITH_UNDERSCORES for relationship types, typically verbs.

**Example:**
```cypher
(:Person {name: "Alice"})-[:KNOWS {since: 2020}]->(:Person {name: "Bob"})
```

#### Properties
Properties are key-value pairs that can be attached to both nodes and relationships.

**Supported Data Types:**
- **Numeric:** Integer, Float
- **String:** Text
- **Boolean:** true/false
- **Spatial:** Point
- **Temporal:** Date, Time, DateTime, Duration
- **Collections:** Lists of any single type

**Example:**
```cypher
{
  name: "Alice",
  age: 30,
  hobbies: ["reading", "hiking"],
  created: datetime(),
  location: point({latitude: 48.8566, longitude: 2.3522})
}
```

#### Paths
A path is a sequence of nodes connected by relationships. Paths are fundamental to graph queries.

**Example:**
```cypher
(:Person)-[:KNOWS]->(:Person)-[:WORKS_FOR]->(:Company)
```

### 2. Labels

Labels are used to group nodes into categories. A node can have multiple labels.

**Purpose:**
- Organize nodes by type
- Enable efficient queries (labels are indexed)
- Apply constraints and indexes to specific node types

**Syntax:**
```cypher
(:Person)          // Single label
(:Person:Employee) // Multiple labels
```

### 3. Property Graph Model

The property graph model consists of:
1. **Nodes** with labels and properties
2. **Relationships** with types and properties
3. Both can store arbitrary property data

This model combines:
- The structure of a graph (nodes and edges)
- The flexibility of key-value stores (properties)

---

## Python Driver Integration

### Basic Connection Pattern

```python
from neo4j import GraphDatabase, RoutingControl

# Connection configuration
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "your_password")

# Create driver instance (use as context manager for automatic cleanup)
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    # Verify connectivity
    driver.verify_connectivity()
    print("Connected to Neo4j!")
    
    # Execute queries here
```

### Driver Configuration Options

```python
from neo4j import GraphDatabase
import neo4j

driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "password"),
    
    # Connection pool settings
    max_connection_lifetime=3600,  # seconds
    max_connection_pool_size=50,
    connection_acquisition_timeout=60,  # seconds
    
    # Encryption settings (for production)
    encrypted=True,
    trust=neo4j.TRUST_ALL_CERTIFICATES,  # Or TRUST_SYSTEM_CA_SIGNED_CERTIFICATES
    
    # Other settings
    user_agent="MyApp/1.0",
    resolver=None  # Custom address resolver
)
```

### Query Execution Methods

#### 1. execute_query() - Recommended for Most Cases

This is the **simplest and recommended** method for executing queries. It handles session management automatically.

```python
from neo4j import GraphDatabase, RoutingControl

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    # Basic query execution
    records, summary, keys = driver.execute_query(
        "MATCH (p:Person) RETURN p.name AS name LIMIT 10",
        database_="neo4j",  # Specify database (default: neo4j)
    )
    
    # Process records
    for record in records:
        print(record["name"])
    
    # Access query metadata
    print(f"Query executed in {summary.result_available_after} ms")
    print(f"Consumed {summary.result_consumed_after} ms")
```

#### 2. execute_query() with Parameters

**ALWAYS use parameterized queries** to prevent injection attacks and improve performance.

```python
# Write query (default routing)
records, summary, keys = driver.execute_query(
    """
    MERGE (p:Person {name: $name})
    SET p.age = $age, p.email = $email
    RETURN p
    """,
    name="Alice",
    age=30,
    email="alice@example.com",
    database_="neo4j"
)

# Read query with explicit routing
records, summary, keys = driver.execute_query(
    """
    MATCH (p:Person {name: $name})-[:KNOWS]->(friend)
    RETURN friend.name AS friend_name
    ORDER BY friend_name
    """,
    name="Alice",
    database_="neo4j",
    routing_=RoutingControl.READ  # Route to read replica if available
)
```

#### 3. Sessions for Complex Transactions

Use sessions when you need explicit transaction control or multiple queries in a single transaction.

```python
def create_person_with_friends(driver, person_name, friend_names):
    """Example of a transaction function"""
    def _create_friendship(tx, person_name, friend_names):
        # Create person
        tx.run(
            "MERGE (p:Person {name: $name})",
            name=person_name
        )
        
        # Create friends and relationships
        for friend_name in friend_names:
            tx.run(
                """
                MATCH (p:Person {name: $person_name})
                MERGE (f:Person {name: $friend_name})
                MERGE (p)-[:KNOWS]->(f)
                """,
                person_name=person_name,
                friend_name=friend_name
            )
    
    # Execute in a write transaction
    with driver.session(database="neo4j") as session:
        session.execute_write(_create_friendship, person_name, friend_names)

# Usage
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    create_person_with_friends(driver, "Alice", ["Bob", "Charlie", "Diana"])
```

#### 4. Manual Transaction Control

```python
with driver.session(database="neo4j") as session:
    # Begin transaction
    tx = session.begin_transaction()
    
    try:
        # Execute multiple queries
        tx.run("CREATE (p:Person {name: $name})", name="Alice")
        tx.run("CREATE (p:Person {name: $name})", name="Bob")
        tx.run(
            """
            MATCH (a:Person {name: 'Alice'})
            MATCH (b:Person {name: 'Bob'})
            CREATE (a)-[:KNOWS]->(b)
            """
        )
        
        # Commit if all succeed
        tx.commit()
    except Exception as e:
        # Rollback on error
        tx.rollback()
        raise e
    finally:
        tx.close()
```

### Working with Query Results

```python
# Execute query
records, summary, keys = driver.execute_query(
    """
    MATCH (p:Person)-[r:KNOWS]->(friend:Person)
    WHERE p.age > $min_age
    RETURN p.name AS person, friend.name AS friend, r.since AS since
    ORDER BY person, friend
    """,
    min_age=25,
    database_="neo4j"
)

# Iterate over records
for record in records:
    # Access by key name
    person = record["person"]
    friend = record["friend"]
    since = record["since"]
    
    # Or access by index
    # person = record[0]
    
    # Or convert to dict
    # record_dict = dict(record)
    
    print(f"{person} knows {friend} since {since}")

# Access result metadata
print(f"Returned {len(records)} records")
print(f"Execution time: {summary.result_available_after} ms")
print(f"Query type: {summary.query_type}")
print(f"Counters: {summary.counters}")
```

### Handling Nodes and Relationships in Python

```python
records, summary, keys = driver.execute_query(
    "MATCH (p:Person)-[r:KNOWS]->(f:Person) RETURN p, r, f LIMIT 1",
    database_="neo4j"
)

for record in records:
    # Node object
    person_node = record["p"]
    print(f"Node ID: {person_node.element_id}")
    print(f"Labels: {list(person_node.labels)}")
    print(f"Properties: {dict(person_node)}")
    print(f"Name: {person_node['name']}")  # Access property
    
    # Relationship object
    knows_rel = record["r"]
    print(f"Relationship ID: {knows_rel.element_id}")
    print(f"Type: {knows_rel.type}")
    print(f"Start node: {knows_rel.start_node.element_id}")
    print(f"End node: {knows_rel.end_node.element_id}")
    print(f"Properties: {dict(knows_rel)}")
```

### Error Handling

```python
from neo4j.exceptions import (
    ServiceUnavailable,
    AuthError,
    CypherSyntaxError,
    ConstraintError,
    Neo4jError
)

try:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        records, summary, keys = driver.execute_query(
            "CREATE (p:Person {email: $email})",
            email="duplicate@example.com",
            database_="neo4j"
        )
        
except ServiceUnavailable as e:
    print(f"Could not connect to Neo4j: {e}")
    
except AuthError as e:
    print(f"Authentication failed: {e}")
    
except CypherSyntaxError as e:
    print(f"Cypher syntax error: {e}")
    
except ConstraintError as e:
    print(f"Constraint violation: {e}")
    
except Neo4jError as e:
    print(f"Neo4j error [{e.code}]: {e.message}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Complete Example: CRUD Operations

```python
from neo4j import GraphDatabase, RoutingControl

class Neo4jPersonRepository:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_person(self, name, age, email):
        """Create a new person"""
        records, summary, keys = self.driver.execute_query(
            """
            CREATE (p:Person {name: $name, age: $age, email: $email})
            RETURN p
            """,
            name=name, age=age, email=email,
            database_="neo4j"
        )
        return records[0]["p"] if records else None
    
    def find_person(self, name):
        """Find a person by name"""
        records, summary, keys = self.driver.execute_query(
            "MATCH (p:Person {name: $name}) RETURN p",
            name=name,
            database_="neo4j",
            routing_=RoutingControl.READ
        )
        return records[0]["p"] if records else None
    
    def update_person(self, name, new_age=None, new_email=None):
        """Update person's properties"""
        query = "MATCH (p:Person {name: $name}) SET "
        params = {"name": name}
        updates = []
        
        if new_age is not None:
            updates.append("p.age = $age")
            params["age"] = new_age
        
        if new_email is not None:
            updates.append("p.email = $email")
            params["email"] = new_email
        
        query += ", ".join(updates) + " RETURN p"
        
        records, summary, keys = self.driver.execute_query(
            query, **params, database_="neo4j"
        )
        return records[0]["p"] if records else None
    
    def delete_person(self, name):
        """Delete a person and all their relationships"""
        records, summary, keys = self.driver.execute_query(
            "MATCH (p:Person {name: $name}) DETACH DELETE p",
            name=name,
            database_="neo4j"
        )
        return summary.counters.nodes_deleted
    
    def create_friendship(self, person1, person2, since=None):
        """Create a KNOWS relationship between two people"""
        records, summary, keys = self.driver.execute_query(
            """
            MATCH (p1:Person {name: $person1})
            MATCH (p2:Person {name: $person2})
            MERGE (p1)-[r:KNOWS]->(p2)
            SET r.since = $since
            RETURN r
            """,
            person1=person1, person2=person2, since=since,
            database_="neo4j"
        )
        return records[0]["r"] if records else None
    
    def find_friends(self, name):
        """Find all friends of a person"""
        records, summary, keys = self.driver.execute_query(
            """
            MATCH (p:Person {name: $name})-[:KNOWS]->(friend:Person)
            RETURN friend.name AS name, friend.age AS age
            ORDER BY name
            """,
            name=name,
            database_="neo4j",
            routing_=RoutingControl.READ
        )
        return [dict(record) for record in records]

# Usage
repo = Neo4jPersonRepository("neo4j://localhost:7687", "neo4j", "password")

try:
    # Create
    repo.create_person("Alice", 30, "alice@example.com")
    repo.create_person("Bob", 25, "bob@example.com")
    
    # Read
    person = repo.find_person("Alice")
    print(f"Found: {person['name']}")
    
    # Update
    repo.update_person("Alice", new_age=31)
    
    # Create relationship
    repo.create_friendship("Alice", "Bob", since="2020-01-01")
    
    # Query relationships
    friends = repo.find_friends("Alice")
    print(f"Alice's friends: {friends}")
    
    # Delete
    # repo.delete_person("Bob")
    
finally:
    repo.close()
```

---

## Cypher Query Language

### Cypher Fundamentals

Cypher is Neo4j's declarative query language, similar to SQL but optimized for graphs. It uses ASCII-art syntax to represent patterns visually.

**Key Principles:**
- **Declarative:** Specify WHAT you want, not HOW to get it
- **Pattern-based:** Queries describe graph patterns
- **Visual:** Syntax mirrors how you'd draw a graph
- **Composable:** Build complex queries from simple clauses

### ASCII-Art Syntax

```cypher
()              // Anonymous node
(p)             // Node with variable 'p'
(:Person)       // Node with label 'Person'
(p:Person)      // Node with variable and label
(p:Person {name: 'Alice'})  // Node with label and properties

-[]->           // Directed relationship
-[r]->          // Relationship with variable
-[:KNOWS]->     // Relationship with type
-[r:KNOWS]->    // Relationship with variable and type
-[r:KNOWS {since: 2020}]->  // Relationship with properties

<-[]->          // Bidirectional
-[]-            // Undirected (match both directions)
```

### Essential Cypher Clauses

#### 1. MATCH - Find Patterns

```cypher
// Match all Person nodes
MATCH (p:Person)
RETURN p

// Match with property filter
MATCH (p:Person {name: 'Alice'})
RETURN p

// Match with WHERE clause (more flexible)
MATCH (p:Person)
WHERE p.age > 25 AND p.email CONTAINS '@example.com'
RETURN p

// Match relationships
MATCH (p:Person)-[r:KNOWS]->(friend:Person)
RETURN p.name, friend.name, r.since

// Match undirected relationships
MATCH (p:Person)-[:KNOWS]-(friend:Person)
WHERE p.name = 'Alice'
RETURN friend.name

// Match paths of specific length
MATCH (p:Person {name: 'Alice'})-[:KNOWS*2]-(foaf)
RETURN DISTINCT foaf.name AS friend_of_friend

// Match variable length paths
MATCH (p:Person {name: 'Alice'})-[:KNOWS*1..3]-(connected)
RETURN DISTINCT connected.name

// Match shortest path
MATCH path = shortestPath(
  (p1:Person {name: 'Alice'})-[:KNOWS*]-(p2:Person {name: 'Bob'})
)
RETURN path, length(path) AS hops
```

#### 2. CREATE - Create New Data

```cypher
// Create a single node
CREATE (p:Person {name: 'Alice', age: 30})
RETURN p

// Create multiple nodes
CREATE 
  (p1:Person {name: 'Alice'}),
  (p2:Person {name: 'Bob'}),
  (p1)-[:KNOWS {since: 2020}]->(p2)

// Create from MATCH
MATCH (p:Person {name: 'Alice'})
CREATE (p)-[:LIVES_IN]->(:City {name: 'Paris'})
```

#### 3. MERGE - Create or Match (Upsert)

```cypher
// MERGE ensures node exists (creates if not, matches if exists)
MERGE (p:Person {email: 'alice@example.com'})
ON CREATE SET p.name = 'Alice', p.created = timestamp()
ON MATCH SET p.lastSeen = timestamp()
RETURN p

// MERGE relationship
MATCH (p1:Person {name: 'Alice'})
MATCH (p2:Person {name: 'Bob'})
MERGE (p1)-[r:KNOWS]->(p2)
ON CREATE SET r.since = date()
RETURN r

// MERGE with complex pattern
MERGE (p:Person {email: 'alice@example.com'})-[r:WORKS_FOR]->(c:Company {name: 'Acme Inc'})
ON CREATE SET 
  p.name = 'Alice',
  r.startDate = date(),
  c.founded = 2010
RETURN p, r, c
```

**CRITICAL DIFFERENCE:**
- `CREATE` always creates new nodes/relationships (can create duplicates)
- `MERGE` matches existing or creates new (ensures uniqueness)

#### 4. SET - Update Properties

```cypher
// Update single property
MATCH (p:Person {name: 'Alice'})
SET p.age = 31
RETURN p

// Update multiple properties
MATCH (p:Person {name: 'Alice'})
SET p.age = 31, p.email = 'newalice@example.com', p.updated = timestamp()
RETURN p

// Replace all properties (WARNING: removes non-specified properties)
MATCH (p:Person {name: 'Alice'})
SET p = {name: 'Alice', age: 31, email: 'alice@example.com'}
RETURN p

// Add properties without removing existing ones
MATCH (p:Person {name: 'Alice'})
SET p += {phone: '+33123456789', city: 'Paris'}
RETURN p

// Add labels
MATCH (p:Person {name: 'Alice'})
SET p:Employee:Manager
RETURN p
```

#### 5. REMOVE - Remove Properties and Labels

```cypher
// Remove property
MATCH (p:Person {name: 'Alice'})
REMOVE p.age
RETURN p

// Remove multiple properties
MATCH (p:Person {name: 'Alice'})
REMOVE p.age, p.email
RETURN p

// Remove label
MATCH (p:Person:Employee {name: 'Alice'})
REMOVE p:Employee
RETURN p
```

#### 6. DELETE - Remove Nodes and Relationships

```cypher
// Delete relationship only
MATCH (p:Person {name: 'Alice'})-[r:KNOWS]->()
DELETE r

// Delete node (only if it has no relationships)
MATCH (p:Person {name: 'Alice'})
DELETE p

// DETACH DELETE removes node and all its relationships
MATCH (p:Person {name: 'Alice'})
DETACH DELETE p

// Delete all nodes and relationships (DANGEROUS!)
MATCH (n)
DETACH DELETE n
```

#### 7. WHERE - Filter Results

```cypher
// Comparison operators
MATCH (p:Person)
WHERE p.age >= 25 AND p.age <= 40
RETURN p

// String operations
MATCH (p:Person)
WHERE p.name STARTS WITH 'A' 
  OR p.email ENDS WITH '@example.com'
  OR p.description CONTAINS 'engineer'
RETURN p

// Regular expressions
MATCH (p:Person)
WHERE p.email =~ '.*@example\\.com$'
RETURN p

// IN operator
MATCH (p:Person)
WHERE p.name IN ['Alice', 'Bob', 'Charlie']
RETURN p

// IS NULL / IS NOT NULL
MATCH (p:Person)
WHERE p.age IS NOT NULL
RETURN p

// Relationship filtering
MATCH (p:Person)-[r:KNOWS]->(friend)
WHERE r.since >= date('2020-01-01')
RETURN p.name, friend.name

// Pattern filtering in WHERE
MATCH (p:Person)
WHERE (p)-[:KNOWS]->(:Person {name: 'Alice'})
RETURN p.name

// NOT EXISTS
MATCH (p:Person)
WHERE NOT (p)-[:KNOWS]->()
RETURN p.name AS loners
```

#### 8. RETURN - Specify Results

```cypher
// Return nodes
MATCH (p:Person)
RETURN p

// Return specific properties
MATCH (p:Person)
RETURN p.name, p.age

// Return with aliases
MATCH (p:Person)
RETURN p.name AS name, p.age AS age

// Return expressions
MATCH (p:Person)
RETURN p.name, p.age, p.age + 10 AS ageInTenYears

// Return distinct values
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
RETURN DISTINCT c.name

// Return count
MATCH (p:Person)
RETURN count(p) AS totalPeople

// Return aggregations
MATCH (p:Person)
RETURN 
  count(p) AS total,
  avg(p.age) AS averageAge,
  min(p.age) AS youngest,
  max(p.age) AS oldest,
  collect(p.name) AS allNames
```

#### 9. ORDER BY - Sort Results

```cypher
// Sort ascending (default)
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age

// Sort descending
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC

// Multiple sort criteria
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC, p.name ASC

// Sort by expressions
MATCH (p:Person)-[:KNOWS]->(friend)
RETURN p.name, count(friend) AS friendCount
ORDER BY friendCount DESC
```

#### 10. LIMIT & SKIP - Pagination

```cypher
// Limit results
MATCH (p:Person)
RETURN p.name
ORDER BY p.name
LIMIT 10

// Skip results (for pagination)
MATCH (p:Person)
RETURN p.name
ORDER BY p.name
SKIP 20 LIMIT 10  // Page 3 (items 21-30)

// Top N query
MATCH (p:Person)
RETURN p.name, p.age
ORDER BY p.age DESC
LIMIT 5  // Top 5 oldest people
```

#### 11. WITH - Chain Query Parts

```cypher
// Basic chaining
MATCH (p:Person)
WITH p, p.age * 12 AS ageInMonths
WHERE ageInMonths > 300
RETURN p.name, ageInMonths

// Aggregation in pipeline
MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
WITH c, count(p) AS employeeCount
WHERE employeeCount > 10
RETURN c.name, employeeCount
ORDER BY employeeCount DESC

// Transforming data
MATCH (p:Person)
WITH collect({name: p.name, age: p.age}) AS people
RETURN people, size(people) AS totalPeople

// Multiple WITH clauses
MATCH (p:Person)-[:KNOWS]->(friend)
WITH p, count(friend) AS friendCount
WHERE friendCount > 5
WITH p, friendCount
ORDER BY friendCount DESC
LIMIT 10
RETURN p.name, friendCount
```

#### 12. UNWIND - Transform Lists to Rows

```cypher
// Unwind a list
UNWIND [1, 2, 3, 4, 5] AS number
RETURN number * 2 AS doubled

// Create nodes from list
UNWIND ['Alice', 'Bob', 'Charlie'] AS name
CREATE (p:Person {name: name})

// Process complex structures
WITH [{name: 'Alice', age: 30}, {name: 'Bob', age: 25}] AS people
UNWIND people AS person
CREATE (p:Person)
SET p = person
```

#### 13. CALL - Invoke Procedures

```cypher
// List all labels
CALL db.labels()

// List all relationship types
CALL db.relationshipTypes()

// Show indexes
CALL db.indexes()

// Show constraints
CALL db.constraints()

// APOC procedures (if installed)
CALL apoc.meta.graph()

// Custom procedure with parameters
CALL db.index.fulltext.queryNodes('personNameIndex', 'Alice~') 
YIELD node, score
RETURN node.name, score
```

### Common Cypher Patterns

#### Pattern 1: Friend of Friend (Recommendations)

```cypher
// Find friends of friends who are not already friends
MATCH (person:Person {name: 'Alice'})-[:KNOWS]->()-[:KNOWS]->(foaf)
WHERE NOT (person)-[:KNOWS]->(foaf) 
  AND person <> foaf
RETURN foaf.name, count(*) AS mutualFriends
ORDER BY mutualFriends DESC
LIMIT 10
```

#### Pattern 2: Shortest Path

```cypher
// Find shortest path between two people
MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
MATCH path = shortestPath((p1)-[:KNOWS*]-(p2))
RETURN path, length(path) AS degrees

// All shortest paths
MATCH (p1:Person {name: 'Alice'}), (p2:Person {name: 'Bob'})
MATCH paths = allShortestPaths((p1)-[:KNOWS*]-(p2))
RETURN paths, length(paths) AS degrees
```

#### Pattern 3: Hierarchical Data (Tree Traversal)

```cypher
// All employees reporting to a manager (any depth)
MATCH (manager:Employee {name: 'Alice'})<-[:REPORTS_TO*]-(subordinate)
RETURN subordinate.name, 
       length((manager)<-[:REPORTS_TO*]-(subordinate)) AS levels

// Direct reports only
MATCH (manager:Employee {name: 'Alice'})<-[:REPORTS_TO]-(direct)
RETURN direct.name
```

#### Pattern 4: Aggregation by Relationship

```cypher
// Count relationships per node
MATCH (p:Person)-[r:KNOWS]->()
RETURN p.name, count(r) AS connections
ORDER BY connections DESC

// Group by relationship property
MATCH (p:Person)-[r:KNOWS]->(friend)
RETURN r.since AS year, 
       count(friend) AS newFriends
ORDER BY year
```

#### Pattern 5: Conditional Create

```cypher
// Create relationship only if it doesn't exist
MERGE (p1:Person {name: 'Alice'})
MERGE (p2:Person {name: 'Bob'})
MERGE (p1)-[r:KNOWS]->(p2)
ON CREATE SET r.created = timestamp()
ON MATCH SET r.updated = timestamp()
RETURN p1, r, p2
```

#### Pattern 6: Batch Updates

```cypher
// Update all nodes matching criteria
MATCH (p:Person)
WHERE p.age IS NULL
SET p.age = 0

// Batch delete old data
MATCH (log:LogEntry)
WHERE log.timestamp < timestamp() - (30 * 24 * 60 * 60 * 1000)  // 30 days ago
WITH log LIMIT 10000
DETACH DELETE log
```

### Cypher Functions

#### String Functions

```cypher
RETURN 
  toLower('HELLO') AS lower,                    // 'hello'
  toUpper('hello') AS upper,                    // 'HELLO'
  trim('  hello  ') AS trimmed,                 // 'hello'
  left('hello', 3) AS leftChars,                // 'hel'
  right('hello', 3) AS rightChars,              // 'llo'
  substring('hello', 1, 3) AS substr,           // 'ell'
  replace('hello world', 'world', 'Neo4j') AS replaced,  // 'hello Neo4j'
  split('a,b,c', ',') AS parts,                 // ['a', 'b', 'c']
  reverse('hello') AS reversed,                 // 'olleh'
  toString(123) AS string                       // '123'
```

#### Mathematical Functions

```cypher
RETURN 
  abs(-5) AS absolute,                          // 5
  ceil(1.3) AS ceiling,                         // 2
  floor(1.7) AS floored,                        // 1
  round(1.5) AS rounded,                        // 2
  sqrt(16) AS squareRoot,                       // 4
  rand() AS randomFloat,                        // 0.0 to 1.0
  toInteger(3.7) AS integer,                    // 3
  toFloat('3.14') AS float                      // 3.14
```

#### List Functions

```cypher
RETURN 
  size([1, 2, 3]) AS listSize,                  // 3
  head([1, 2, 3]) AS first,                     // 1
  tail([1, 2, 3]) AS rest,                      // [2, 3]
  last([1, 2, 3]) AS lastItem,                  // 3
  range(1, 10) AS numbers,                      // [1,2,3,4,5,6,7,8,9,10]
  range(0, 20, 5) AS steps,                     // [0, 5, 10, 15, 20]
  [x IN [1,2,3,4,5] WHERE x % 2 = 0] AS evens  // [2, 4]
```

#### Aggregation Functions

```cypher
MATCH (p:Person)
RETURN 
  count(p) AS total,
  count(DISTINCT p.age) AS uniqueAges,
  sum(p.age) AS totalAge,
  avg(p.age) AS averageAge,
  min(p.age) AS youngest,
  max(p.age) AS oldest,
  collect(p.name) AS allNames,
  collect(DISTINCT p.city) AS cities
```

#### Temporal Functions

```cypher
RETURN 
  date() AS currentDate,                        // 2025-10-27
  time() AS currentTime,                        // 14:30:00.000+00:00
  datetime() AS now,                            // 2025-10-27T14:30:00.000Z
  timestamp() AS epochMillis,                   // 1730035800000
  date('2025-01-01') AS specificDate,
  duration.between(date('2020-01-01'), date()) AS age,
  date() + duration('P1M') AS nextMonth         // Add 1 month
```

#### Spatial Functions

```cypher
// Create point
RETURN point({latitude: 48.8566, longitude: 2.3522}) AS parisLocation

// Calculate distance (in meters)
WITH 
  point({latitude: 48.8566, longitude: 2.3522}) AS paris,
  point({latitude: 51.5074, longitude: -0.1278}) AS london
RETURN distance(paris, london) AS distanceInMeters  // ~343,556m
```

---

## Common Patterns & Best Practices

### Schema Design Principles

#### 1. Label Your Nodes

**Good:**
```cypher
(:Person {name: 'Alice'})
(:Company {name: 'Acme'})
(:Product {id: 'P123'})
```

**Bad:**
```cypher
({type: 'person', name: 'Alice'})  // Don't use properties for type info
```

#### 2. Use Descriptive Relationship Types

**Good:**
```cypher
(:Person)-[:WORKS_FOR]->(:Company)
(:Person)-[:KNOWS]->(:Person)
(:Customer)-[:PURCHASED]->(:Product)
```

**Bad:**
```cypher
(:Person)-[:RELATED_TO]->(:Company)  // Too generic
(:Person)-[:HAS]->(:Person)          // Too vague
```

#### 3. Direction Matters for Semantics, Not Performance

```cypher
// Both perform identically
MATCH (a)-[:KNOWS]->(b)  // Directed
MATCH (a)-[:KNOWS]-(b)   // Undirected

// But semantics are different
(:Person)-[:WORKS_FOR]->(:Company)  // Person works for company (not vice versa)
```

#### 4. Keep Relationship Types Specific

**Instead of:**
```cypher
(:Person)-[:RELATED {type: 'friend'}]->(:Person)
(:Person)-[:RELATED {type: 'colleague'}]->(:Person)
```

**Use:**
```cypher
(:Person)-[:FRIEND_OF]->(:Person)
(:Person)-[:COLLEAGUE_OF]->(:Person)
```

### Indexing Strategy

#### Create Indexes for Lookup Properties

```cypher
// Create single-property index
CREATE INDEX person_name_idx FOR (p:Person) ON (p.name)

// Create composite index (multiple properties)
CREATE INDEX person_name_age_idx FOR (p:Person) ON (p.name, p.age)

// Create full-text index
CREATE FULLTEXT INDEX person_fulltext FOR (p:Person) ON EACH [p.name, p.bio]

// List all indexes
CALL db.indexes()

// Drop index
DROP INDEX person_name_idx
```

**When to use indexes:**
- Properties used in `MATCH` with equality (=)
- Properties used in `WHERE` filters
- Properties used in `ORDER BY`
- Unique identifiers

#### Create Constraints

```cypher
// Unique constraint (automatically creates index)
CREATE CONSTRAINT person_email_unique FOR (p:Person) REQUIRE p.email IS UNIQUE

// Node key constraint (composite uniqueness)
CREATE CONSTRAINT person_key FOR (p:Person) REQUIRE (p.firstName, p.lastName) IS NODE KEY

// Property existence constraint
CREATE CONSTRAINT person_email_exists FOR (p:Person) REQUIRE p.email IS NOT NULL

// Relationship existence constraint
CREATE CONSTRAINT knows_since_exists FOR ()-[r:KNOWS]-() REQUIRE r.since IS NOT NULL

// List all constraints
CALL db.constraints()

// Drop constraint
DROP CONSTRAINT person_email_unique
```

### Query Optimization Tips

#### 1. Use Parameters (Always!)

**Good (Parameterized):**
```python
driver.execute_query(
    "MATCH (p:Person {name: $name}) RETURN p",
    name="Alice",
    database_="neo4j"
)
```

**Bad (String Interpolation):**
```python
name = "Alice"
driver.execute_query(
    f"MATCH (p:Person {{name: '{name}'}}) RETURN p",  # DON'T DO THIS!
    database_="neo4j"
)
```

**Why parameters?**
- Prevents Cypher injection attacks
- Enables query plan caching
- Better performance

#### 2. Use MERGE Wisely

```cypher
// SLOW: Merges on entire node
MERGE (p:Person {name: 'Alice', age: 30, email: 'alice@example.com'})

// FAST: Merge on unique property, then SET others
MERGE (p:Person {email: 'alice@example.com'})
ON CREATE SET p.name = 'Alice', p.age = 30, p.created = timestamp()
ON MATCH SET p.lastSeen = timestamp()
```

#### 3. Filter Early

**Good:**
```cypher
MATCH (p:Person)
WHERE p.age > 25
MATCH (p)-[:KNOWS]->(friend)
RETURN friend.name
```

**Better:**
```cypher
MATCH (p:Person)-[:KNOWS]->(friend)
WHERE p.age > 25
RETURN friend.name
```

#### 4. Use LIMIT in Aggregations

```cypher
// Instead of aggregating everything
MATCH (p:Person)
RETURN count(p)

// Use LIMIT when you don't need exact count
MATCH (p:Person)
RETURN count(p) LIMIT 1000  // "at least 1000"
```

#### 5. Profile Your Queries

```cypher
// See execution plan (without executing)
EXPLAIN 
MATCH (p:Person)-[:KNOWS]-(friend)
WHERE p.name = 'Alice'
RETURN friend.name

// Execute and see actual performance
PROFILE 
MATCH (p:Person)-[:KNOWS]-(friend)
WHERE p.name = 'Alice'
RETURN friend.name
```

Look for:
- **DB Hits:** Lower is better
- **Rows:** Fewer intermediate rows = better
- **NodeByLabelScan:** Good if combined with index
- **NodeByIndexSeek:** Best for lookups

### Batch Operations

#### Batch Create with UNWIND

```python
# Instead of many individual creates
people_data = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]

records, summary, keys = driver.execute_query(
    """
    UNWIND $people AS person
    CREATE (p:Person)
    SET p = person
    """,
    people=people_data,
    database_="neo4j"
)
```

#### Batch Update

```cypher
// Update in batches to avoid long locks
CALL {
  MATCH (p:Person)
  WHERE p.age IS NULL
  RETURN p LIMIT 1000
}
SET p.age = 0
```

#### Batch Delete

```cypher
// Delete large datasets in batches
CALL apoc.periodic.iterate(
  "MATCH (n:OldData) RETURN n",
  "DETACH DELETE n",
  {batchSize: 10000}
)
```

### Transaction Management Best Practices

1. **Keep transactions short** - Long-running transactions lock resources
2. **Use auto-commit for reads** - Use `execute_query()` for simple reads
3. **Use explicit transactions for writes** - For multiple related operations
4. **Batch operations** - Group similar operations together
5. **Handle failures** - Always catch and handle exceptions

---

## Debugging & Troubleshooting

### Common Issues and Solutions

#### Issue 1: Slow Queries

**Symptoms:**
- Queries taking seconds or minutes
- High memory usage
- Database becomes unresponsive

**Diagnosis:**
```cypher
// Profile the query
PROFILE 
MATCH (p:Person)-[:KNOWS*3]->(friend)
WHERE p.name = 'Alice'
RETURN friend.name
```

**Solutions:**
- Add indexes on frequently queried properties
- Reduce relationship traversal depth
- Use LIMIT to restrict result size
- Filter early in the query
- Consider using `shortestPath()` instead of variable-length patterns

#### Issue 2: Connection Errors

**Error:** `ServiceUnavailable: Unable to connect to localhost:7687`

**Checks:**
```python
from neo4j import GraphDatabase

try:
    driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))
    driver.verify_connectivity()
    print("Connected!")
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    driver.close()
```

**Solutions:**
- Verify Neo4j is running: `docker ps` or check Neo4j Desktop
- Check the URI (neo4j:// for default, bolt:// for direct)
- Verify port 7687 is accessible
- Check authentication credentials
- Check firewall settings

#### Issue 3: Authentication Failures

**Error:** `AuthError: The client is unauthorized due to authentication failure`

**Solutions:**
- Reset password via Neo4j Browser or CLI
- For Neo4j Desktop: Check database settings
- For Docker: Verify NEO4J_AUTH environment variable
- Check that default credentials haven't been changed

#### Issue 4: Constraint Violations

**Error:** `ConstraintError: Node(123) already exists with label Person and property email = 'alice@example.com'`

**Solutions:**
```python
try:
    driver.execute_query(
        "CREATE (p:Person {email: $email})",
        email="alice@example.com",
        database_="neo4j"
    )
except ConstraintError:
    # Handle duplicate
    print("Person with this email already exists")
    # Maybe use MERGE instead
    driver.execute_query(
        """
        MERGE (p:Person {email: $email})
        ON CREATE SET p.name = $name
        RETURN p
        """,
        email="alice@example.com",
        name="Alice",
        database_="neo4j"
    )
```

#### Issue 5: Memory Issues (OutOfMemory)

**Error:** `OutOfMemoryError`

**Causes:**
- Returning too many nodes/relationships
- Variable-length pattern matching without limits
- Large aggregations

**Solutions:**
```cypher
// Add LIMIT
MATCH (p:Person)-[:KNOWS*1..5]-(connected)
RETURN connected
LIMIT 1000  // Prevent unbounded results

// Use pagination
MATCH (p:Person)
RETURN p
ORDER BY p.name
SKIP $skip
LIMIT $limit

// Process in batches
CALL {
  MATCH (p:Person)
  RETURN p LIMIT 10000
}
WITH collect(p) AS batch
// Process batch
```

#### Issue 6: Cypher Syntax Errors

**Error:** `CypherSyntaxError: Invalid input 'X': expected...`

**Common mistakes:**
```cypher
// Wrong: Missing return
MATCH (p:Person)
// Add: RETURN p

// Wrong: Invalid property syntax
MATCH (p:Person {name: Alice})  // Missing quotes
// Fix:
MATCH (p:Person {name: 'Alice'})

// Wrong: Invalid relationship pattern
MATCH (p:Person)-->(friend)  // Missing relationship brackets
// Fix:
MATCH (p:Person)-[]->(friend)

// Wrong: Using = for pattern matching
MATCH (p:Person = {name: 'Alice'})
// Fix:
MATCH (p:Person {name: 'Alice'})
```

### Debugging Tools

#### 1. EXPLAIN and PROFILE

```cypher
// See query plan without executing
EXPLAIN 
MATCH (p:Person {name: 'Alice'})-[:KNOWS]->(friend)
RETURN friend.name

// Execute and see performance metrics
PROFILE 
MATCH (p:Person {name: 'Alice'})-[:KNOWS]->(friend)
RETURN friend.name
```

#### 2. Query Logging

```python
import logging

# Enable Neo4j driver logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("neo4j").setLevel(logging.DEBUG)

# Now all queries will be logged
driver.execute_query(
    "MATCH (p:Person) RETURN count(p)",
    database_="neo4j"
)
```

#### 3. Result Summary Analysis

```python
records, summary, keys = driver.execute_query(
    "MATCH (p:Person) RETURN p LIMIT 10",
    database_="neo4j"
)

print(f"Query type: {summary.query_type}")
print(f"Database: {summary.database}")
print(f"Result available after: {summary.result_available_after} ms")
print(f"Result consumed after: {summary.result_consumed_after} ms")
print(f"Counters: {summary.counters}")
```

#### 4. Neo4j Browser Tools

Access at http://localhost:7474

```cypher
// Database info
:sysinfo

// Show indexes
:schema

// Show slow queries
CALL dbms.listQueries()
YIELD query, elapsedTimeMillis, queryId
WHERE elapsedTimeMillis > 1000
RETURN query, elapsedTimeMillis, queryId

// Kill slow query
CALL dbms.killQuery('query-id')
```

### Monitoring Queries

```python
def monitored_query(driver, query, params=None):
    """Execute query with timing and error handling"""
    import time
    start_time = time.time()
    
    try:
        records, summary, keys = driver.execute_query(
            query,
            **(params or {}),
            database_="neo4j"
        )
        
        elapsed = (time.time() - start_time) * 1000
        
        print(f"Query executed in {elapsed:.2f}ms")
        print(f"Returned {len(records)} records")
        print(f"DB Hits: {summary.counters}")
        
        return records
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        print(f"Query failed after {elapsed:.2f}ms: {e}")
        raise

# Usage
monitored_query(
    driver,
    "MATCH (p:Person) WHERE p.age > $min_age RETURN p",
    {"min_age": 25}
)
```

---

## Performance Optimization

### Database Configuration

#### Memory Settings (neo4j.conf)

```conf
# Heap memory (for query execution)
server.memory.heap.initial_size=2G
server.memory.heap.max_size=4G

# Page cache (for graph storage)
server.memory.pagecache.size=2G

# Transaction log
dbms.tx_log.rotation.retention_policy=2 days 1G
```

### Query Performance

#### Use Indexes

```cypher
// Before: Full label scan
MATCH (p:Person)
WHERE p.email = 'alice@example.com'
RETURN p

// Create index
CREATE INDEX person_email FOR (p:Person) ON (p.email)

// After: Index seek (much faster)
MATCH (p:Person)
WHERE p.email = 'alice@example.com'
RETURN p
```

#### Avoid Cartesian Products

**Bad (Cartesian product):**
```cypher
MATCH (p:Person), (c:Company)
WHERE p.name = 'Alice' AND c.name = 'Acme'
RETURN p, c
```

**Good (Connected pattern):**
```cypher
MATCH (p:Person {name: 'Alice'})-[:WORKS_FOR]->(c:Company {name: 'Acme'})
RETURN p, c
```

#### Limit Relationship Traversal

```cypher
// Instead of unlimited depth
MATCH (p:Person {name: 'Alice'})-[:KNOWS*]->(friend)
RETURN friend

// Use reasonable limits
MATCH (p:Person {name: 'Alice'})-[:KNOWS*1..3]->(friend)
RETURN DISTINCT friend
LIMIT 100
```

### Connection Pooling

```python
# Configure connection pool
driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "password"),
    max_connection_pool_size=50,
    max_connection_lifetime=3600,
    connection_acquisition_timeout=60
)

# Reuse driver instance across application
# Don't create new driver for each query!
```

### Batch Processing

```python
def batch_create_people(driver, people_list, batch_size=1000):
    """Create people in batches"""
    for i in range(0, len(people_list), batch_size):
        batch = people_list[i:i+batch_size]
        
        driver.execute_query(
            """
            UNWIND $people AS person
            MERGE (p:Person {email: person.email})
            SET p += person
            """,
            people=batch,
            database_="neo4j"
        )
        
        print(f"Processed {min(i+batch_size, len(people_list))}/{len(people_list)}")

# Usage
people = [{"name": f"Person{i}", "email": f"person{i}@example.com"} for i in range(10000)]
batch_create_people(driver, people)
```

---

## Security Considerations

### 1. Always Use Parameterized Queries

**VULNERABLE (Cypher Injection):**
```python
# NEVER DO THIS!
name = request.get_parameter("name")
query = f"MATCH (p:Person {{name: '{name}'}}) RETURN p"
driver.execute_query(query, database_="neo4j")

# Attacker could input: "Alice'}) DETACH DELETE p //"
```

**SAFE:**
```python
name = request.get_parameter("name")
records, summary, keys = driver.execute_query(
    "MATCH (p:Person {name: $name}) RETURN p",
    name=name,  # Parameter binding
    database_="neo4j"
)
```

### 2. Use TLS/SSL in Production

```python
from neo4j import GraphDatabase
import neo4j

# Enable TLS
driver = GraphDatabase.driver(
    "neo4j+s://your-server:7687",  # Note: neo4j+s:// or bolt+s://
    auth=("neo4j", "password"),
    encrypted=True,
    trust=neo4j.TRUST_SYSTEM_CA_SIGNED_CERTIFICATES
)
```

### 3. Principle of Least Privilege

```cypher
// Create read-only user
CREATE USER analyst SET PASSWORD 'secure_password' CHANGE NOT REQUIRED
GRANT ROLE reader TO analyst

// Create limited access user
CREATE USER developer SET PASSWORD 'secure_password' CHANGE NOT REQUIRED
GRANT MATCH {*} ON GRAPH neo4j NODE * TO developer
GRANT TRAVERSE ON GRAPH neo4j RELATIONSHIP * TO developer
```

### 4. Input Validation

```python
def validate_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_user(driver, email, name):
    """Create user with input validation"""
    if not validate_email(email):
        raise ValueError("Invalid email format")
    
    if not name or len(name) > 100:
        raise ValueError("Invalid name")
    
    driver.execute_query(
        """
        MERGE (p:Person {email: $email})
        SET p.name = $name
        """,
        email=email,
        name=name,
        database_="neo4j"
    )
```

### 5. Secure Configuration

```conf
# Disable remote JMX
dbms.jvm.additional=-Dcom.sun.management.jmxremote.authenticate=true

# Restrict IP addresses
dbms.connectors.default_listen_address=127.0.0.1

# Enable auth
dbms.security.auth_enabled=true

# Logging
dbms.logs.query.enabled=true
dbms.logs.query.threshold=1s
```

---

## Resource Links

### Official Documentation

- **Neo4j Operations Manual:** https://neo4j.com/docs/operations-manual/current/
  - Installation, configuration, and management
  
- **Neo4j Python Driver Manual:** https://neo4j.com/docs/python-manual/current/
  - Python driver guide and examples
  
- **Python Driver API Documentation:** https://neo4j.com/docs/api/python-driver/current/
  - Complete API reference
  
- **Cypher Manual:** https://neo4j.com/docs/cypher-manual/current/
  - Complete Cypher language reference
  
- **Cypher Cheat Sheet:** https://neo4j.com/docs/cypher-cheat-sheet/
  - Quick reference for Cypher syntax

### GitHub Repositories

- **Neo4j Python Driver:** https://github.com/neo4j/neo4j-python-driver
  - Source code, issues, and changelog
  
- **Neo4j Database:** https://github.com/neo4j/neo4j
  - Neo4j database source code

- **Python Driver Rust Extensions:** https://github.com/neo4j/neo4j-python-driver-rust-ext
  - Optional performance extensions

- **Driver Wiki:** https://github.com/neo4j/neo4j-python-driver/wiki
  - Additional documentation and change logs

### Learning Resources

- **GraphAcademy (Free Courses):** https://graphacademy.neo4j.com/categories/python/
  - Interactive online training for Neo4j with Python
  
- **Getting Started Guide:** https://neo4j.com/docs/getting-started/cypher/
  - Introduction to Cypher and Neo4j
  
- **Tutorial: Cypher Basics:** https://neo4j.com/docs/getting-started/appendix/tutorials/guide-cypher-basics/
  - Step-by-step Cypher tutorial

- **Example Project (Movies):** https://github.com/neo4j-examples/movies-python-bolt
  - Sample web application using the Python driver

### Version Compatibility

- **Neo4j Supported Versions:** https://neo4j.com/developer/kb/neo4j-supported-versions/
  - Driver and database version compatibility matrix
  
- **Migration Guide:** https://neo4j.com/docs/migration-guide/current/
  - Upgrading between Neo4j versions

### Community & Support

- **Neo4j Community Forum:** https://community.neo4j.com/
  - Ask questions and get help
  
- **Neo4j Discord:** https://discord.gg/neo4j
  - Real-time community chat
  
- **Stack Overflow:** https://stackoverflow.com/questions/tagged/neo4j
  - Tagged Neo4j questions

### Tools & Extensions

- **APOC (Awesome Procedures On Cypher):** https://neo4j.com/labs/apoc/
  - Extended procedures and functions library
  
- **Neo4j Browser:** http://localhost:7474 (when running locally)
  - Web-based query interface
  
- **Neo4j Desktop:** https://neo4j.com/download/
  - Desktop application for development

### Production & Cloud

- **Neo4j Aura (Cloud):** https://neo4j.com/cloud/aura/
  - Managed Neo4j cloud service
  
- **Neo4j Sandbox:** https://sandbox.neo4j.com/
  - Free temporary Neo4j instances

---

## Quick Reference for AI Agents

### Essential Import
```python
from neo4j import GraphDatabase, RoutingControl
from neo4j.exceptions import ServiceUnavailable, AuthError, CypherSyntaxError, ConstraintError
```

### Connection Template
```python
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    # Execute queries here
```

### Basic Query Template
```python
records, summary, keys = driver.execute_query(
    "MATCH (n:Label {property: $value}) RETURN n",
    value="some_value",
    database_="neo4j",
    routing_=RoutingControl.READ  # or WRITE
)
```

### Common Cypher Patterns
```cypher
// Create
CREATE (n:Label {property: $value})

// Match
MATCH (n:Label {property: $value}) RETURN n

// Update
MATCH (n:Label {property: $value})
SET n.property = $new_value

// Delete
MATCH (n:Label {property: $value})
DETACH DELETE n

// Upsert (MERGE)
MERGE (n:Label {uniqueProperty: $value})
ON CREATE SET n.created = timestamp()
ON MATCH SET n.updated = timestamp()

// Relationships
MATCH (a:LabelA {id: $id1}), (b:LabelB {id: $id2})
MERGE (a)-[:REL_TYPE {property: $value}]->(b)
```

### Debugging Checklist
1. ✓ Is Neo4j running?
2. ✓ Can I connect? (`driver.verify_connectivity()`)
3. ✓ Are my credentials correct?
4. ✓ Did I use parameters? (NOT string interpolation)
5. ✓ Did I profile the query? (`PROFILE` or `EXPLAIN`)
6. ✓ Are indexes created for lookup properties?
7. ✓ Did I limit result size?
8. ✓ Are errors caught and logged?

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Target AI Agent:** Claude Sonnet 4.5  
**Maintainer:** AI Development Team

---

*This guide is designed to be comprehensive yet practical for AI agents implementing Neo4j solutions. Always refer to the official documentation for the most up-to-date information.*
