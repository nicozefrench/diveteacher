#!/bin/bash
# Script pour nettoyer complètement Neo4j via le backend Docker

echo "============================================================"
echo "🧹 NETTOYAGE COMPLET NEO4J + GRAPHITI"
echo "============================================================"
echo ""

# Vérifier que Docker est en cours d'exécution
if ! docker ps | grep -q rag-backend; then
    echo "❌ Le conteneur backend n'est pas en cours d'exécution"
    echo "💡 Lancez d'abord: docker compose -f docker/docker-compose.dev.yml up -d backend"
    exit 1
fi

echo "📋 Étape 1: Vérification de l'état actuel..."
echo ""

# Créer un script Python temporaire dans le conteneur
docker exec rag-backend python3 << 'PYTHON_SCRIPT'
from neo4j import GraphDatabase
from app.core.config import settings

print("🔍 Connexion à Neo4j...")
print(f"📍 URI: {settings.NEO4J_URI}")
print(f"👤 User: {settings.NEO4J_USER}")
print("")

driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
)

try:
    with driver.session(database=settings.NEO4J_DATABASE) as session:
        # 1. Compter les nœuds avant
        result = session.run("MATCH (n) RETURN count(n) as count")
        count_before = result.single()["count"]
        print(f"📊 Nœuds avant nettoyage: {count_before}")
        
        if count_before == 0:
            print("")
            print("✅ La base est déjà vide!")
            exit(0)
        
        # 2. Afficher les types de nœuds
        result = session.run("""
            MATCH (n)
            RETURN DISTINCT labels(n) as labels, count(n) as count
            ORDER BY count DESC
        """)
        print("")
        print("📋 Types de nœuds présents:")
        for record in result:
            labels = record["labels"]
            count = record["count"]
            print(f"   - {labels}: {count} nœuds")
        
        # 3. Afficher quelques relations
        result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) as type, count(r) as count
            ORDER BY count DESC
            LIMIT 5
        """)
        relations = list(result)
        if relations:
            print("")
            print("📋 Types de relations présentes:")
            for record in relations:
                rel_type = record["type"]
                count = record["count"]
                print(f"   - {rel_type}: {count} relations")
        
        print("")
        print("=" * 60)
        print("🗑️  DÉBUT DU NETTOYAGE")
        print("=" * 60)
        print("")
        
        # 4. Supprimer tous les nœuds et relations
        print("🗑️  Suppression de tous les nœuds et relations...")
        session.run("MATCH (n) DETACH DELETE n")
        print("   ✅ Tous les nœuds et relations supprimés")
        
        # 5. Supprimer les contraintes
        print("")
        print("🗑️  Suppression des contraintes...")
        result = session.run("SHOW CONSTRAINTS")
        constraints = list(result)
        if constraints:
            for record in constraints:
                constraint_name = record["name"]
                print(f"   - Suppression: {constraint_name}")
                try:
                    session.run(f"DROP CONSTRAINT {constraint_name} IF EXISTS")
                except Exception as e:
                    print(f"     ⚠️  Avertissement: {e}")
        else:
            print("   ✅ Aucune contrainte à supprimer")
        
        # 6. Supprimer les index
        print("")
        print("🗑️  Suppression des index...")
        result = session.run("SHOW INDEXES")
        indexes = list(result)
        constraint_names = [c["name"] for c in constraints]
        if indexes:
            for record in indexes:
                index_name = record["name"]
                # Ne pas supprimer les index liés aux contraintes
                if index_name not in constraint_names:
                    print(f"   - Suppression: {index_name}")
                    try:
                        session.run(f"DROP INDEX {index_name} IF EXISTS")
                    except Exception as e:
                        print(f"     ⚠️  Avertissement: {e}")
        else:
            print("   ✅ Aucun index à supprimer")
        
        # 7. Vérifier que tout est vide
        print("")
        print("=" * 60)
        print("📊 VÉRIFICATION FINALE")
        print("=" * 60)
        print("")
        
        result = session.run("MATCH (n) RETURN count(n) as count")
        count_after = result.single()["count"]
        
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        relations_after = result.single()["count"]
        
        print(f"📊 Nœuds après nettoyage: {count_after}")
        print(f"📊 Relations après nettoyage: {relations_after}")
        print("")
        
        if count_after == 0 and relations_after == 0:
            print("=" * 60)
            print("✅ NEO4J EST MAINTENANT COMPLÈTEMENT VIDE!")
            print("✅ PRÊT POUR DE NOUVEAUX TESTS!")
            print("=" * 60)
        else:
            print("=" * 60)
            print(f"⚠️  Attention: {count_after} nœuds et {relations_after} relations restants")
            print("=" * 60)
            
finally:
    driver.close()

PYTHON_SCRIPT

EXIT_CODE=$?

echo ""
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ NETTOYAGE TERMINÉ AVEC SUCCÈS!"
else
    echo "❌ ERREUR PENDANT LE NETTOYAGE (code: $EXIT_CODE)"
fi
echo "============================================================"

exit $EXIT_CODE

