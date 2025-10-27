#!/usr/bin/env python3
"""
Check Neo4j Graphiti Data
Vérifie si les données Graphiti ont été ingérées dans Neo4j
"""
import sys
from neo4j import GraphDatabase

def check_graphiti_data(uri, user, password):
    """Check Graphiti data in Neo4j"""
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session() as session:
            print("🔍 Checking Neo4j Graphiti Data")
            print("=" * 50)
            print()
            
            # Count Episodes
            result = session.run("MATCH (e:Episode) RETURN count(e) as count")
            episodes_count = result.single()["count"]
            
            # Count Entities
            result = session.run("MATCH (e:Entity) RETURN count(e) as count")
            entities_count = result.single()["count"]
            
            # Count Relations
            result = session.run("MATCH ()-[r:RELATION]->() RETURN count(r) as count")
            relations_count = result.single()["count"]
            
            # Count Communities
            result = session.run("MATCH (c:Community) RETURN count(c) as count")
            communities_count = result.single()["count"]
            
            # Display counts
            print(f"📊 Node Counts:")
            print(f"   Episodes:    {episodes_count:>6}")
            print(f"   Entities:    {entities_count:>6}")
            print(f"   Communities: {communities_count:>6}")
            print(f"   Relations:   {relations_count:>6}")
            print()
            
            # Sample Episodes (if any)
            if episodes_count > 0:
                result = session.run("""
                    MATCH (e:Episode) 
                    RETURN e.name as name, e.created_at as created_at 
                    ORDER BY e.created_at DESC 
                    LIMIT 5
                """)
                print("📝 Recent Episodes:")
                for record in result:
                    name = record["name"][:60] + "..." if len(record["name"]) > 60 else record["name"]
                    print(f"   • {name}")
                print()
            
            # Sample Entities (if any)
            if entities_count > 0:
                result = session.run("""
                    MATCH (e:Entity) 
                    RETURN e.name as name, labels(e) as labels
                    LIMIT 10
                """)
                print("🎯 Sample Entities:")
                for record in result:
                    name = record["name"]
                    entity_labels = ", ".join(record["labels"])
                    print(f"   • {name} ({entity_labels})")
                print()
            
            # Status
            if episodes_count > 0:
                print("✅ Graphiti data found in Neo4j!")
                return 0
            else:
                print("⚠️  No Graphiti Episodes found in Neo4j")
                print("   → Ingestion may still be in progress or failed")
                return 1
                
    finally:
        driver.close()

if __name__ == "__main__":
    # DiveTeacher Neo4j config
    NEO4J_URI = "bolt://localhost:7688"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "diveteacher_dev_2025"
    
    try:
        sys.exit(check_graphiti_data(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD))
    except Exception as e:
        print(f"❌ Error connecting to Neo4j: {e}")
        sys.exit(2)

