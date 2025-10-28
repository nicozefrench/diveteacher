# 🔧 PLAN DE REFACTORING: Warm-up Docling

**Date:** 28 Octobre 2025, 21:45  
**Approche:** Solution C - Refactoring propre et solide  
**Durée estimée:** 20 minutes  
**Objectif:** Warm-up fonctionnel, maintenable, et testable

---

## 📋 PROBLÈME ACTUEL

### Le warm-up échoue avec `ModuleNotFoundError`

**Pourquoi ?**
- `warmup_docling.py` est un **script standalone** exécuté depuis `/app/` (racine du container)
- Il tente d'importer `from app.integrations.dockling import DoclingSingleton`
- Python ne trouve pas le module `app` car le script n'est pas dans le package

**Architecturalement:**
```
/app/
├── warmup_docling.py          ← Script standalone (pas dans le package)
├── app/
│   ├── __init__.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── dockling.py        ← DoclingSingleton ici
│   └── ...
```

Quand Python exécute `python3 /app/warmup_docling.py`, le PYTHONPATH ne contient pas `/app/`, donc `import app.*` échoue.

---

## ✅ SOLUTION: Refactoring Propre

### Architecture cible

```
/app/
├── docker-entrypoint.sh       ← Entrypoint Docker (inchangé)
├── app/
│   ├── __init__.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── dockling.py        ← DoclingSingleton + méthode warmup()
│   └── warmup.py              ← Nouveau: script warmup DANS le package
└── (warmup_docling.py supprimé)
```

### Principe

1. **Déplacer la logique de warm-up DANS le package `app/`**
   - Créer `app/warmup.py` (dans le package, pas à la racine)
   - Ce script peut importer `app.integrations.dockling` correctement

2. **Ajouter une méthode `warmup()` au singleton `DoclingSingleton`**
   - Centraliser la logique d'initialisation
   - Réutilisable depuis n'importe où dans le code

3. **Simplifier l'entrypoint Docker**
   - Appeler `python3 -m app.warmup` (run as module)
   - Le `-m` flag ajoute automatiquement le répertoire courant au PYTHONPATH

---

## 🔧 IMPLÉMENTATION EN 3 ÉTAPES

### Étape 1: Ajouter méthode `warmup()` à `DoclingSingleton`

**Fichier:** `backend/app/integrations/dockling.py`

```python
class DoclingSingleton:
    """Singleton for DocumentConverter to ensure single instance."""
    
    _instance: Optional[DocumentConverter] = None
    _lock = Lock()
    
    @classmethod
    def warmup(cls) -> bool:
        """
        Warm-up: Initialize singleton and download models if needed.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("=" * 60)
            logger.info("🔥 WARMING UP DOCLING MODELS")
            logger.info("=" * 60)
            
            logger.info("📦 Initializing DoclingSingleton...")
            converter = cls.get_converter()
            
            logger.info("✅ DoclingSingleton initialized successfully!")
            logger.info("=" * 60)
            logger.info("🎉 DOCLING WARM-UP COMPLETE!")
            logger.info("=" * 60)
            logger.info("")
            logger.info("ℹ️  Models cached with ACCURATE + OCR + Tables config")
            logger.info("ℹ️  Subsequent processing will be FAST")
            logger.info("")
            
            # Validation: Check singleton is not None
            if cls._instance is None:
                logger.error("❌ Warm-up validation FAILED: _instance is None")
                return False
            
            logger.info("✅ VALIDATION: Singleton instance confirmed")
            logger.info(f"✅ VALIDATION: Instance type = {type(cls._instance)}")
            
            return True
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ WARM-UP FAILED: {e}")
            logger.error("=" * 60)
            logger.error("")
            logger.error("⚠️  Models will be downloaded on first document upload")
            logger.error("")
            return False
    
    @classmethod
    def get_converter(cls) -> DocumentConverter:
        # ... (existing code unchanged)
```

### Étape 2: Créer `app/warmup.py` (dans le package)

**Fichier:** `backend/app/warmup.py`

```python
#!/usr/bin/env python3
"""
Warm-up script for Docling models
Executed at container startup to pre-download models
"""

import sys
import logging
from app.integrations.dockling import DoclingSingleton

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main() -> int:
    """
    Main warm-up entry point
    
    Returns:
        0 if successful, 1 if failed
    """
    logger.info("")
    logger.info("🚀 Starting Docling Model Warm-up...")
    logger.info("")
    
    success = DoclingSingleton.warmup()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Étape 3: Modifier `docker-entrypoint.sh`

**Fichier:** `backend/docker-entrypoint.sh`

```bash
#!/bin/bash
# Docker entrypoint script with Docling warm-up

set -e

echo "=================================================="
echo "🚀 DiveTeacher Backend Starting..."
echo "=================================================="
echo ""

# Check if warm-up should be performed
if [ "${SKIP_WARMUP}" != "true" ]; then
    echo "🔥 Step 1: Warming up Docling models..."
    echo "--------------------------------------------------"
    
    # Run warm-up script AS A MODULE (ensures correct PYTHONPATH)
    python3 -m app.warmup || {
        echo "⚠️  Warm-up failed or skipped"
        echo "⚠️  Models will download on first document upload"
    }
    
    echo ""
    echo "✅ Warm-up phase complete"
    echo ""
else
    echo "⏭️  Skipping warm-up (SKIP_WARMUP=true)"
    echo ""
fi

echo "🚀 Step 2: Starting FastAPI application..."
echo "--------------------------------------------------"
echo ""

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Étape 4: Cleanup - Supprimer ancien fichier

**Fichier à supprimer:** `backend/warmup_docling.py`

### Étape 5: Mettre à jour Dockerfile (si nécessaire)

**Fichier:** `backend/Dockerfile`

```dockerfile
# ... (previous layers)

# Copy application code
COPY app/ ./app/

# Copy entrypoint (warmup_docling.py no longer needed)
COPY docker-entrypoint.sh ./

# Make entrypoint executable
RUN chmod +x /app/docker-entrypoint.sh

# Create uploads directory
RUN mkdir -p /uploads

# Expose port
EXPOSE 8000

# Use custom entrypoint with warm-up
ENTRYPOINT ["/app/docker-entrypoint.sh"]
```

---

## 🎯 AVANTAGES DE CETTE SOLUTION

### 1. **Architecture propre**
- Warm-up logic DANS le package `app/`
- Pas de script orphelin à la racine
- Imports cohérents et maintenables

### 2. **Réutilisable**
```python
# Peut être appelé depuis n'importe où dans le code
from app.integrations.dockling import DoclingSingleton

# Warm-up manuel si besoin
DoclingSingleton.warmup()
```

### 3. **Testable**
```python
# Tests unitaires possibles
def test_docling_warmup():
    success = DoclingSingleton.warmup()
    assert success is True
    assert DoclingSingleton._instance is not None
```

### 4. **Logs clairs**
```
🚀 Starting Docling Model Warm-up...
🔥 WARMING UP DOCLING MODELS
📦 Initializing DoclingSingleton...
✅ DoclingSingleton initialized successfully!
✅ VALIDATION: Singleton instance confirmed
🎉 DOCLING WARM-UP COMPLETE!
```

### 5. **Robuste**
- Gestion d'erreurs propre
- Validation du singleton après warm-up
- Non-bloquant (continue si échec)

---

## 📊 PLAN D'EXÉCUTION

### Phase 1: Refactoring (10 min)
1. ✅ Ajouter `DoclingSingleton.warmup()` dans `dockling.py`
2. ✅ Créer `app/warmup.py` (dans le package)
3. ✅ Modifier `docker-entrypoint.sh` (utiliser `python3 -m app.warmup`)
4. ✅ Supprimer `warmup_docling.py` (ancien fichier)

### Phase 2: Build & Test (10 min)
5. ✅ Rebuild backend avec `--no-cache`
6. ✅ Restart backend
7. ✅ Vérifier logs warm-up
8. ✅ Test ingestion avec `test.pdf`

---

## ✅ CRITÈRES DE SUCCÈS

### Logs attendus au startup:
```
🚀 DiveTeacher Backend Starting...
🔥 Step 1: Warming up Docling models...
🚀 Starting Docling Model Warm-up...
🔥 WARMING UP DOCLING MODELS
📦 Initializing DoclingSingleton...
[Docling model download logs if first time]
✅ DoclingSingleton initialized successfully!
✅ VALIDATION: Singleton instance confirmed
✅ VALIDATION: Instance type = <class 'docling.document_converter.DocumentConverter'>
🎉 DOCLING WARM-UP COMPLETE!
✅ Warm-up phase complete

🚀 Step 2: Starting FastAPI application...
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Test ingestion:
```bash
# Upload test.pdf
curl -X POST http://localhost:8000/api/upload -F "file=@TestPDF/test.pdf"

# Logs backend doivent montrer:
# - ✅ Status dict initialized
# - ✅ [_convert_sync] START conversion
# - ✅ [_convert_sync] Converter obtained (INSTANTANÉ)
# - ✅ [_convert_sync] Conversion complete
# - PAS de re-download de modèles
```

---

## 🔍 DEBUGGING SI ÉCHEC

### Si warm-up échoue encore:
```bash
# Test manual du module
docker exec rag-backend python3 -m app.warmup

# Si erreur d'import, vérifier:
docker exec rag-backend ls -la /app/app/warmup.py
docker exec rag-backend python3 -c "import sys; print(sys.path)"
```

### Si conversion lente:
```bash
# Vérifier singleton après warm-up
docker exec rag-backend python3 -c "
from app.integrations.dockling import DoclingSingleton
print('Singleton instance:', DoclingSingleton._instance)
"
```

---

## 📝 DOCUMENTATION À CRÉER

Après succès, documenter dans `docs/DOCLING-WARMUP.md`:
- Architecture du warm-up
- Comment tester manuellement
- Comment désactiver (`SKIP_WARMUP=true`)
- Troubleshooting

---

**STATUS:** PLAN PRÊT - EN ATTENTE D'EXÉCUTION

