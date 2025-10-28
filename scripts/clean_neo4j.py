#!/usr/bin/env python3
"""
Script pour nettoyer complètement Neo4j et réinitialiser Graphiti
"""

import os
import sys
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from neo4j import GraphDatabase
from app.core.config import settings

def clean_neo4j():
    """Nettoie complètement la base de données Neo4j"""
    
    print("🧹 Nettoyage de Neo4j...")
    print(f"📍 URI: {settings.NEO4J_URI}")
    print(f"👤 User: {settings.NEO4J_USER}")
    
    # Connexion à Neo4j
    driver = GraphDatabase.driver(
        settings.NEO4J_URI.replace("bolt://neo4j:", "bolt://localhost:"),
        auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    
    try:
        with driver.session(database=settings.NEO4J_DATABASE) as session:
            # 1. Compter les nœuds avant nettoyage
            result = session.run("MATCH (n) RETURN count(n) as count")
            count_before = result.single()["count"]
            print(f"\n📊 Nœuds avant nettoyage: {count_before}")
            
            if count_before == 0:
                print("✅ La base est déjà vide!")
                return
            
            # 2. Afficher les types de nœuds
            result = session.run("""
                MATCH (n)
                RETURN DISTINCT labels(n) as labels, count(n) as count
                ORDER BY count DESC
            """)
            print("\n📋 Types de nœuds présents:")
            for record in result:
                labels = record["labels"]
                count = record["count"]
                print(f"   - {labels}: {count} nœuds")
            
            # 3. Supprimer tous les nœuds et relations
            print("\n🗑️  Suppression de tous les nœuds et relations...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # 4. Supprimer tous les index et contraintes
            print("🗑️  Suppression des index et contraintes...")
            
            # Supprimer les contraintes
            result = session.run("SHOW CONSTRAINTS")
            constraints = [record["name"] for record in result]
            for constraint in constraints:
                print(f"   - Suppression contrainte: {constraint}")
                session.run(f"DROP CONSTRAINT {constraint}")
            
            # Supprimer les index
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result if record["name"] not in constraints]
            for index in indexes:
                print(f"   - Suppression index: {index}")
                session.run(f"DROP INDEX {index}")
            
            # 5. Vérifier que tout est vide
            result = session.run("MATCH (n) RETURN count(n) as count")
            count_after = result.single()["count"]
            print(f"\n📊 Nœuds après nettoyage: {count_after}")
            
            if count_after == 0:
                print("\n✅ Neo4j est maintenant complètement vide!")
                print("✅ Prêt pour de nouveaux tests!")
            else:
                print(f"\n⚠️  Attention: {count_after} nœuds restants")
                
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        raise
    finally:
        driver.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🧹 NETTOYAGE COMPLET NEO4J + GRAPHITI")
    print("=" * 60)
    
    try:
        clean_neo4j()
        print("\n" + "=" * 60)
        print("✅ NETTOYAGE TERMINÉ AVEC SUCCÈS!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERREUR: {e}")
        print("=" * 60)
        sys.exit(1)

