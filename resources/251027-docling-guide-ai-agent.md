# Guide Complet Docling pour Agent IA Claude Sonnet 4.5

> **Document de référence pour l'utilisation de Docling dans un contexte de développement avec agent IA**  
> Version: 1.0 | Date: 27 octobre 2025

---

## Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture et Concepts Clés](#architecture-et-concepts-clés)
3. [Installation et Configuration](#installation-et-configuration)
4. [Utilisation de Base](#utilisation-de-base)
5. [Fonctionnalités Avancées](#fonctionnalités-avancées)
6. [Formats Supportés](#formats-supportés)
7. [Exportation et Transformation](#exportation-et-transformation)
8. [Intégrations avec Frameworks IA](#intégrations-avec-frameworks-ia)
9. [Chunking pour RAG](#chunking-pour-rag)
10. [Gestion des Ressources et Performance](#gestion-des-ressources-et-performance)
11. [Bonnes Pratiques pour Agents IA](#bonnes-pratiques-pour-agents-ia)
12. [Résolution de Problèmes](#résolution-de-problèmes)
13. [Ressources et Références](#ressources-et-références)

---

## Vue d'Ensemble

### Qu'est-ce que Docling?

Docling est une bibliothèque open-source MIT créée par IBM Research Zurich pour simplifier le traitement de documents. Elle permet de parser des documents de formats variés avec une compréhension avancée des PDFs, et fournit des intégrations natives avec l'écosystème Gen AI.

### Caractéristiques Principales

- 🗂️ **Multi-format**: PDF, DOCX, PPTX, XLSX, HTML, WAV, MP3, images (PNG, TIFF, JPEG, etc.)
- 📑 **Compréhension PDF avancée**: mise en page, ordre de lecture, structure de tables, code, formules, classification d'images
- 🧬 **Format unifié**: Représentation `DoclingDocument` expressive et unifiée
- ↪️ **Exports variés**: Markdown, HTML, DocTags, JSON lossless
- 🔒 **Exécution locale**: Pour données sensibles et environnements air-gapped
- 🤖 **Intégrations plug-and-play**: LangChain, LlamaIndex, Crew AI, Haystack
- 🔍 **OCR étendu**: Support complet pour PDFs scannés et images
- 👓 **Visual Language Models**: Support de SmolDocling et autres VLMs
- 🎙️ **Audio**: Automatic Speech Recognition (ASR)
- 💻 **CLI pratique**: Interface en ligne de commande simple

### Modèles IA Utilisés

- **DocLayNet**: Analyse de mise en page (layout analysis)
- **TableFormer**: Reconnaissance de structure de tables
- **SmolDocling**: Visual Language Model léger (256M paramètres)
- **EasyOCR**: Reconnaissance optique de caractères
- Support pour modèles ASR (Automatic Speech Recognition)

---

## Architecture et Concepts Clés

### Pipeline de Conversion

Docling utilise une architecture modulaire basée sur des **backends** spécialisés:

```
Document Source → Backend Converter → DoclingDocument → Export Format
```

#### Backends Disponibles

- **PdfDocumentBackend**: Pour PDFs (backend principal)
- **DocxDocumentBackend**: Pour documents Word
- **PptxDocumentBackend**: Pour présentations PowerPoint
- **XlsxDocumentBackend**: Pour feuilles de calcul Excel
- **HTMLDocumentBackend**: Pour pages HTML
- **ImageDocumentBackend**: Pour images
- **AsciidocDocumentBackend**: Pour documents Asciidoc
- **AudioDocumentBackend**: Pour fichiers audio

### DoclingDocument

`DoclingDocument` est le format de représentation unifié au cœur de Docling. Il capture:

- **Structure**: Hiérarchie des sections, paragraphes, listes, tables
- **Contenu**: Texte, images, formulas, code
- **Métadonnées**: Titre, auteurs, références, langue
- **Provenance**: Bounding boxes, numéros de page
- **Sémantique**: Classification des éléments (titres, texte, légendes, etc.)

### Flux de Travail Typique

```python
from docling.document_converter import DocumentConverter

# 1. Initialiser le convertisseur
converter = DocumentConverter()

# 2. Convertir le document
result = converter.convert(source)

# 3. Accéder au DoclingDocument
doc = result.document

# 4. Exporter dans le format désiré
markdown_text = doc.export_to_markdown()
```

---

## Installation et Configuration

### Installation Standard

```bash
pip install docling
```

**Plateformes supportées**: macOS, Linux, Windows  
**Architectures**: x86_64, arm64

### Installation pour Développement

```bash
git clone https://github.com/docling-project/docling.git
cd docling
pip install -e ".[dev]"
```

### Dépendances Système

Pour OCR complet et fonctionnalités avancées:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### Configuration des Variables d'Environnement

```bash
# Chemin vers les artefacts de modèles (pour usage offline)
export DOCLING_ARTIFACTS_PATH="/path/to/models"

# Limiter les threads CPU utilisés (défaut: 4)
export OMP_NUM_THREADS=4
```

### Téléchargement des Modèles (Usage Offline)

```bash
# Méthode 1: CLI
docling-tools models download

# Méthode 2: Programmatique
from docling.utils.model_downloader import download_models
download_models()
```

Les modèles sont téléchargés dans `$HOME/.cache/docling/models`.

---

## Utilisation de Base

### Conversion Simple

```python
from docling.document_converter import DocumentConverter

# Source peut être: chemin local, URL, ou stream binaire
source = "https://arxiv.org/pdf/2408.09869"
converter = DocumentConverter()
result = converter.convert(source)

# Exporter en Markdown
markdown = result.document.export_to_markdown()
print(markdown)
```

### Conversion depuis Stream Binaire

```python
from io import BytesIO
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

# Créer un stream
buf = BytesIO(binary_pdf_data)
source = DocumentStream(name="document.pdf", stream=buf)

converter = DocumentConverter()
result = converter.convert(source)
```

### Conversion Batch (Multiple Documents)

```python
from pathlib import Path
from docling.document_converter import DocumentConverter

# Liste de documents à convertir
sources = [
    "doc1.pdf",
    "doc2.docx",
    "https://example.com/doc3.pdf"
]

converter = DocumentConverter()

for source in sources:
    result = converter.convert(source)
    output_path = Path(source).stem + ".md"
    Path(output_path).write_text(result.document.export_to_markdown())
```

### Utilisation CLI

```bash
# Conversion simple
docling document.pdf

# Avec spécification du format de sortie
docling --to markdown document.pdf

# Conversion d'un répertoire
docling --output output_dir/ input_dir/

# Utilisation de SmolDocling VLM
docling --pipeline vlm --vlm-model smoldocling document.pdf

# Voir toutes les options
docling --help
```

**Référence CLI**: https://docling-project.github.io/docling/reference/cli/

---

## Fonctionnalités Avancées

### Configuration du Pipeline PDF

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

# Configuration personnalisée
pipeline_options = PdfPipelineOptions(
    do_ocr=True,                    # Activer OCR
    do_table_structure=True,        # Reconnaissance de tables
    artifacts_path="/path/to/models" # Modèles locaux
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

result = converter.convert("document.pdf")
```

### Options de Structure de Tables

#### Mode de Cell Matching

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions(do_table_structure=True)

# Désactiver cell matching pour utiliser les cellules prédites par le modèle
pipeline_options.table_structure_options.do_cell_matching = False

# Créer le convertisseur avec ces options
converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

#### Mode TableFormer (depuis v1.16.0)

```python
from docling.datamodel.pipeline_options import TableFormerMode

pipeline_options = PdfPipelineOptions(do_table_structure=True)

# Mode FAST: Plus rapide mais moins précis
pipeline_options.table_structure_options.mode = TableFormerMode.FAST

# Mode ACCURATE: Plus lent mais meilleure qualité (défaut)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
```

### Limites de Taille et Pages

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

# Limiter à 100 pages et 20MB
result = converter.convert(
    "large_document.pdf",
    max_num_pages=100,
    max_file_size=20971520  # 20MB en octets
)
```

### Services Distants (Opt-in Explicite)

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions

# ATTENTION: Active la communication avec services externes
pipeline_options = PdfPipelineOptions(enable_remote_services=True)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

**Services requérant `enable_remote_services=True`**:
- `PictureDescriptionApiOptions`: Vision models via API

### Utilisation de Backends Spécifiques

```python
import urllib.request
from io import BytesIO
from docling.backend.html_backend import HTMLDocumentBackend
from docling.datamodel.base_models import InputFormat, InputDocument

url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
html_content = urllib.request.urlopen(url).read()

in_doc = InputDocument(
    path_or_stream=BytesIO(html_content),
    format=InputFormat.HTML,
    backend=HTMLDocumentBackend,
    filename="ai_article.html",
)

backend = HTMLDocumentBackend(in_doc=in_doc, path_or_stream=BytesIO(html_content))
docling_doc = backend.convert()

print(docling_doc.export_to_markdown())
```

---

## Formats Supportés

### Formats d'Entrée

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Support complet avec analyse avancée |
| Word | `.docx` | Microsoft Word 2007+ |
| PowerPoint | `.pptx` | Présentations |
| Excel | `.xlsx`, `.xls` | Feuilles de calcul |
| HTML | `.html`, `.htm` | Pages web |
| Images | `.png`, `.jpg`, `.jpeg`, `.tiff`, `.gif`, `.bmp`, `.webp` | Avec OCR |
| Audio | `.wav`, `.mp3`, `.m4a`, `.ogg`, `.flac` | Via ASR |
| Markdown | `.md` | Documents markdown |
| AsciiDoc | `.asciidoc`, `.adoc` | Documentation technique |

### Formats d'Exportation

| Format | Méthode | Description |
|--------|---------|-------------|
| Markdown | `export_to_markdown()` | Format markdown standard |
| HTML | `export_to_html()` | HTML structuré |
| JSON | `export_to_dict()` | Représentation complète |
| DocTags | `export_to_doctags()` | Format DocTags (arXiv:2503.11576) |
| Plain Text | `export_to_text()` | Texte brut |

**Documentation formats**: https://docling-project.github.io/docling/usage/supported_formats/

---

## Exportation et Transformation

### Export Markdown

```python
# Standard
markdown = result.document.export_to_markdown()

# Avec options
markdown = result.document.export_to_markdown(
    include_metadata=True,
    strict_text=False
)
```

### Export HTML

```python
html = result.document.export_to_html()
```

### Export JSON (Lossless)

```python
# Dictionnaire Python
doc_dict = result.document.export_to_dict()

# JSON string
import json
json_str = json.dumps(doc_dict, indent=2)
```

### Export DocTags

```python
doctags = result.document.export_to_doctags()
```

**DocTags Reference**: https://arxiv.org/abs/2503.11576

### Accès Programmatique aux Éléments

```python
doc = result.document

# Itérer sur tous les éléments
for item in doc.iterate_items():
    print(f"Type: {item.label}, Text: {item.text}")

# Accès aux tables
for table in doc.tables:
    print(table.export_to_markdown())

# Accès aux images
for picture in doc.pictures:
    print(f"Image: {picture.prov[0].bbox}")  # Bounding box

# Accès aux métadonnées
metadata = doc.metadata
print(f"Title: {metadata.title}")
print(f"Authors: {metadata.authors}")
```

---

## Intégrations avec Frameworks IA

### LangChain

```python
from langchain_community.document_loaders import DoclingLoader

# Chargement avec DoclingLoader
loader = DoclingLoader(
    file_path="document.pdf",
    export_type="markdown"  # ou "text", "doctags"
)

documents = loader.load()

# Utiliser dans une chaîne RAG
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
splits = text_splitter.split_documents(documents)

vectorstore = FAISS.from_documents(splits, OpenAIEmbeddings())
```

**Documentation**: https://python.langchain.com/docs/integrations/document_loaders/docling

### LlamaIndex

```python
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.docling import DoclingReader

# Option 1: Via SimpleDirectoryReader
reader = SimpleDirectoryReader(
    input_files=["document.pdf"],
    file_extractor={".pdf": DoclingReader()}
)
documents = reader.load_data()

# Option 2: DoclingReader direct
docling_reader = DoclingReader()
documents = docling_reader.load_data(file_path="document.pdf")

# Créer un index
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is this document about?")
```

**Documentation**: https://docs.llamaindex.ai/en/stable/examples/data_connectors/DoclingReaderDemo/

### Haystack

```python
from haystack_integrations.components.converters.docling import DoclingConverter
from haystack import Pipeline

# Créer le convertisseur
converter = DoclingConverter()

# Dans un pipeline
pipeline = Pipeline()
pipeline.add_component("converter", converter)

# Exécuter
result = pipeline.run({
    "converter": {
        "sources": ["document.pdf"]
    }
})

documents = result["converter"]["documents"]
```

### Crew AI

```python
from crewai import Agent, Task, Crew
from docling.document_converter import DocumentConverter

# Convertir le document
converter = DocumentConverter()
result = converter.convert("research_paper.pdf")
markdown = result.document.export_to_markdown()

# Créer un agent avec le contenu
researcher = Agent(
    role="Research Analyst",
    goal="Analyze research papers",
    backstory="Expert in scientific literature",
    verbose=True
)

task = Task(
    description=f"Analyze this research paper:\n\n{markdown}",
    agent=researcher
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
```

**Page intégrations**: https://docling-project.github.io/docling/integrations/

---

## Chunking pour RAG

### HybridChunker

Le `HybridChunker` combine chunking basé sur la structure du document et sur les tokens.

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

# Convertir document
converter = DocumentConverter()
result = converter.convert("document.pdf")
doc = result.document

# Créer le chunker
chunker = HybridChunker(
    tokenizer="BAAI/bge-small-en-v1.5",  # Spécifier le tokenizer
    max_tokens=512,                       # Taille max des chunks
    min_tokens=64,                        # Taille min des chunks
    merge_peers=True                      # Fusionner les éléments pairs
)

# Chunker le document
chunks = list(chunker.chunk(doc))

# Structure d'un chunk
for chunk in chunks[:3]:
    print("=" * 80)
    print(f"Text: {chunk['text'][:100]}...")
    print(f"Meta: {chunk['meta']}")
```

### Structure d'un Chunk

```python
{
    "text": "Full text of the chunk...",
    "meta": {
        "doc_items": [
            {
                "self_ref": "#/texts/28",
                "label": "text",
                "prov": [{
                    "page_no": 2,
                    "bbox": {
                        "l": 53.29, 
                        "t": 287.14, 
                        "r": 295.56, 
                        "b": 212.37
                    }
                }]
            }
        ],
        "headings": ["1 INTRODUCTION"],
        "origin": {
            "mimetype": "application/pdf",
            "filename": "document.pdf"
        }
    }
}
```

### Exemple RAG Complet

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import Anthropic
from langchain.chains import RetrievalQA

# 1. Convertir documents
converter = DocumentConverter()
docs = []
for pdf_path in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    result = converter.convert(pdf_path)
    docs.append(result.document)

# 2. Chunker tous les documents
chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5")
all_chunks = []
for doc in docs:
    chunks = list(chunker.chunk(doc))
    all_chunks.extend(chunks)

# 3. Créer embeddings et vectorstore
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

texts = [chunk['text'] for chunk in all_chunks]
metadatas = [chunk['meta'] for chunk in all_chunks]

vectorstore = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

# 4. Créer chaîne QA
llm = Anthropic(model="claude-sonnet-4-5-20250929")
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
    return_source_documents=True
)

# 5. Requêter
response = qa_chain("What are the main findings of these documents?")
print(response["result"])
```

**Exemple détaillé**: https://docling-project.github.io/docling/examples/hybrid_chunking/

---

## Gestion des Ressources et Performance

### Limitation CPU

```bash
# Limiter à 2 threads CPU
export OMP_NUM_THREADS=2

# Ou dans le code (avant import)
import os
os.environ['OMP_NUM_THREADS'] = '2'

from docling.document_converter import DocumentConverter
```

### Limitation Mémoire

```python
# Traiter par batch avec libération mémoire
import gc
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
batch_size = 10

for i in range(0, len(document_list), batch_size):
    batch = document_list[i:i+batch_size]
    
    for doc_path in batch:
        result = converter.convert(doc_path)
        # Traiter le résultat
        process_result(result)
    
    # Libérer la mémoire
    gc.collect()
```

### Optimisation Pipeline

```python
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

# Pour rapidité maximale
fast_pipeline = PdfPipelineOptions(
    do_ocr=False,  # Désactiver OCR si pas nécessaire
    do_table_structure=True,
)
fast_pipeline.table_structure_options.mode = TableFormerMode.FAST

# Pour qualité maximale
accurate_pipeline = PdfPipelineOptions(
    do_ocr=True,
    do_table_structure=True,
)
accurate_pipeline.table_structure_options.mode = TableFormerMode.ACCURATE
```

### Parallélisation

```python
from concurrent.futures import ThreadPoolExecutor
from docling.document_converter import DocumentConverter

def convert_document(doc_path):
    converter = DocumentConverter()
    return converter.convert(doc_path)

# Traiter en parallèle (attention à la mémoire)
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(convert_document, document_paths))
```

### Monitoring Performance

```python
import time
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

start = time.time()
result = converter.convert("document.pdf")
duration = time.time() - start

print(f"Conversion time: {duration:.2f}s")
print(f"Pages: {len(result.document.pages)}")
print(f"Time per page: {duration/len(result.document.pages):.2f}s")
```

---

## Bonnes Pratiques pour Agents IA

### 1. Gestion d'Erreurs Robuste

```python
from docling.document_converter import DocumentConverter
from docling.exceptions import ConversionError

def safe_convert(doc_path):
    """Conversion sécurisée avec gestion d'erreurs."""
    try:
        converter = DocumentConverter()
        result = converter.convert(
            doc_path,
            max_num_pages=500,      # Limite de sécurité
            max_file_size=50*1024*1024  # 50MB max
        )
        return result.document, None
    except ConversionError as e:
        return None, f"Conversion error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# Utilisation
doc, error = safe_convert("document.pdf")
if error:
    print(f"Failed to convert: {error}")
else:
    markdown = doc.export_to_markdown()
```

### 2. Validation des Entrées

```python
from pathlib import Path
import mimetypes

def validate_document(file_path):
    """Valider que le fichier est supporté."""
    path = Path(file_path)
    
    if not path.exists():
        return False, "File does not exist"
    
    if not path.is_file():
        return False, "Path is not a file"
    
    # Vérifier extension
    supported_extensions = {
        '.pdf', '.docx', '.pptx', '.xlsx', 
        '.html', '.htm', '.md', '.png', 
        '.jpg', '.jpeg', '.tiff', '.wav', '.mp3'
    }
    
    if path.suffix.lower() not in supported_extensions:
        return False, f"Unsupported format: {path.suffix}"
    
    return True, "Valid"

# Utilisation
is_valid, message = validate_document("document.pdf")
if not is_valid:
    print(f"Validation failed: {message}")
```

### 3. Extraction d'Informations Structurées

```python
def extract_structured_data(doc):
    """Extraire données structurées d'un DoclingDocument."""
    data = {
        "metadata": {
            "title": doc.metadata.title,
            "authors": doc.metadata.authors,
            "language": doc.metadata.language,
        },
        "statistics": {
            "num_pages": len(doc.pages),
            "num_tables": len(doc.tables),
            "num_pictures": len(doc.pictures),
        },
        "tables": [],
        "sections": []
    }
    
    # Extraire tables
    for table in doc.tables:
        data["tables"].append({
            "markdown": table.export_to_markdown(),
            "page": table.prov[0].page_no if table.prov else None
        })
    
    # Extraire structure des sections
    current_section = None
    for item in doc.iterate_items():
        if item.label == "section_header":
            current_section = {
                "title": item.text,
                "level": item.level,
                "content": []
            }
            data["sections"].append(current_section)
        elif current_section and item.label == "text":
            current_section["content"].append(item.text)
    
    return data
```

### 4. Cache pour Performance

```python
import hashlib
import pickle
from pathlib import Path

class DocumentCache:
    """Cache simple pour conversions."""
    
    def __init__(self, cache_dir=".docling_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, file_path):
        """Générer clé de cache basée sur hash du fichier."""
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return f"{Path(file_path).stem}_{file_hash}.pkl"
    
    def get(self, file_path):
        """Récupérer du cache."""
        cache_file = self.cache_dir / self._get_cache_key(file_path)
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        return None
    
    def set(self, file_path, doc):
        """Sauvegarder dans cache."""
        cache_file = self.cache_dir / self._get_cache_key(file_path)
        with open(cache_file, 'wb') as f:
            pickle.dump(doc, f)

# Utilisation
cache = DocumentCache()
converter = DocumentConverter()

doc = cache.get("document.pdf")
if doc is None:
    result = converter.convert("document.pdf")
    doc = result.document
    cache.set("document.pdf", doc)

markdown = doc.export_to_markdown()
```

### 5. Logging Détaillé

```python
import logging
from datetime import datetime

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('docling_agent')

def convert_with_logging(doc_path):
    """Conversion avec logging détaillé."""
    logger.info(f"Starting conversion of {doc_path}")
    start_time = datetime.now()
    
    try:
        converter = DocumentConverter()
        result = converter.convert(doc_path)
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Conversion successful in {duration:.2f}s")
        logger.info(f"Pages: {len(result.document.pages)}")
        logger.info(f"Tables: {len(result.document.tables)}")
        
        return result.document
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        raise
```

### 6. Workflow Typique pour Agent IA

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

class DocumentProcessor:
    """Processeur de documents pour agent IA."""
    
    def __init__(self):
        self.converter = DocumentConverter()
        self.chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5")
    
    def process_document(self, doc_path, output_format="markdown"):
        """
        Traiter un document complet.
        
        Args:
            doc_path: Chemin vers le document
            output_format: Format de sortie ('markdown', 'json', 'chunks')
        
        Returns:
            dict avec résultats du traitement
        """
        # 1. Validation
        is_valid, msg = validate_document(doc_path)
        if not is_valid:
            return {"error": msg}
        
        # 2. Conversion
        try:
            result = self.converter.convert(doc_path)
            doc = result.document
        except Exception as e:
            return {"error": f"Conversion failed: {str(e)}"}
        
        # 3. Extraction selon format
        if output_format == "markdown":
            return {
                "content": doc.export_to_markdown(),
                "metadata": self._extract_metadata(doc)
            }
        
        elif output_format == "json":
            return {
                "content": doc.export_to_dict(),
                "metadata": self._extract_metadata(doc)
            }
        
        elif output_format == "chunks":
            chunks = list(self.chunker.chunk(doc))
            return {
                "chunks": chunks,
                "metadata": self._extract_metadata(doc),
                "num_chunks": len(chunks)
            }
    
    def _extract_metadata(self, doc):
        """Extraire métadonnées utiles."""
        return {
            "title": doc.metadata.title,
            "num_pages": len(doc.pages),
            "num_tables": len(doc.tables),
            "num_images": len(doc.pictures),
        }

# Utilisation
processor = DocumentProcessor()
result = processor.process_document("research.pdf", output_format="chunks")

if "error" not in result:
    print(f"Processed {result['num_chunks']} chunks")
    print(f"Title: {result['metadata']['title']}")
```

---

## Résolution de Problèmes

### Problèmes Courants

#### 1. Modèles Non Téléchargés

**Symptôme**: Erreur de modèle manquant lors de la première utilisation

**Solution**:
```bash
docling-tools models download
```

#### 2. Mémoire Insuffisante

**Symptôme**: `MemoryError` ou crash lors du traitement de gros documents

**Solutions**:
```python
# Limiter le nombre de pages
result = converter.convert(doc, max_num_pages=100)

# Limiter la taille du fichier
result = converter.convert(doc, max_file_size=20*1024*1024)  # 20MB

# Réduire les threads
os.environ['OMP_NUM_THREADS'] = '2'
```

#### 3. OCR Lent

**Symptôme**: Conversion de PDFs scannés très lente

**Solutions**:
```python
# Désactiver OCR si pas nécessaire
pipeline_options = PdfPipelineOptions(do_ocr=False)

# Ou réduire la résolution d'OCR
pipeline_options = PdfPipelineOptions(do_ocr=True)
pipeline_options.ocr_options.resolution = 200  # DPI plus bas
```

#### 4. Tables Mal Extraites

**Symptôme**: Structure de tables incorrecte

**Solutions**:
```python
# Essayer sans cell matching
pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False

# Ou utiliser mode ACCURATE
from docling.datamodel.pipeline_options import TableFormerMode
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
```

#### 5. Erreur de Permissions

**Symptôme**: `OperationNotAllowed` lors de l'utilisation de services distants

**Solution**:
```python
# Activer explicitement les services distants
pipeline_options = PdfPipelineOptions(enable_remote_services=True)
```

### Débogage

```python
import logging

# Activer logging détaillé
logging.basicConfig(level=logging.DEBUG)

# Pour Docling spécifiquement
logging.getLogger('docling').setLevel(logging.DEBUG)
```

### Support et Communauté

- **GitHub Issues**: https://github.com/docling-project/docling/issues
- **Discussions**: https://github.com/docling-project/docling/discussions
- **Dosu AI Assistant**: https://app.dosu.dev/097760a8-135e-4789-8234-90c8837d7f1c/ask

---

## Ressources et Références

### Documentation Officielle

- **Site Principal**: https://docling-project.github.io/docling/
- **GitHub Repository**: https://github.com/docling-project/docling
- **Installation Guide**: https://docling-project.github.io/docling/installation/
- **Usage Guide**: https://docling-project.github.io/docling/usage/
- **Examples**: https://docling-project.github.io/docling/examples/
- **API Reference**: https://docling-project.github.io/docling/reference/document_converter/
- **CLI Reference**: https://docling-project.github.io/docling/reference/cli/

### Articles et Papers

- **Docling Technical Report**: https://arxiv.org/abs/2408.09869
  - Citation: Deep Search Team. "Docling Technical Report." arXiv:2408.09869, 2024.
- **DocTags Format**: https://arxiv.org/abs/2503.11576
- **DocLayNet Dataset**: https://arxiv.org/abs/2206.01062
- **TableFormer**: Rechercher sur arXiv pour détails sur le modèle

### Modèles et Datasets

- **SmolDocling on Hugging Face**: https://huggingface.co/ds4sd/SmolDocling-256M-preview
- **DocLayNet**: Layout analysis model
- **TableFormer**: Table structure recognition model

### Intégrations

- **LangChain**: https://python.langchain.com/docs/integrations/document_loaders/docling
- **LlamaIndex**: https://docs.llamaindex.ai/en/stable/examples/data_connectors/DoclingReaderDemo/
- **Haystack**: https://haystack.deepset.ai/integrations/docling
- **Crew AI**: Documentation sur site Crew AI

### Communauté et Support

- **LF AI & Data Foundation**: https://lfaidata.foundation/projects/
- **Contributing Guide**: https://github.com/docling-project/docling/blob/main/CONTRIBUTING.md
- **License**: MIT License

### Exemples de Code

Repository d'exemples: https://docling-project.github.io/docling/examples/

Exemples importants:
- **Basic Conversion**: Conversion simple de documents
- **Custom Convert**: Configuration avancée du pipeline
- **Hybrid Chunking**: Chunking pour RAG
- **Multi-format Conversion**: Traiter plusieurs formats
- **Batch Processing**: Traitement en batch
- **RAG Integration**: Intégration avec systèmes RAG

### Outils Utiles

- **docling-tools**: Utilitaires CLI pour gestion des modèles
  ```bash
  docling-tools models download
  docling-tools models list
  ```

### Changelog et Versions

- **Dernière version stable**: Vérifier sur PyPI ou GitHub releases
- **Changelog**: https://github.com/docling-project/docling/releases
- **Breaking Changes**: Suivre les notes de release pour migrations

---

## Citation

Si vous utilisez Docling dans votre travail, veuillez citer:

```bibtex
@techreport{Docling,
  author = {Deep Search Team},
  month = {8},
  title = {Docling Technical Report},
  url = {https://arxiv.org/abs/2408.09869},
  eprint = {2408.09869},
  doi = {10.48550/arXiv.2408.09869},
  version = {1.0.0},
  year = {2024}
}
```

---

## Notes pour Agent IA Claude Sonnet 4.5

### Points Critiques à Retenir

1. **Toujours valider les entrées** avant conversion
2. **Gérer les erreurs robustement** - la conversion peut échouer
3. **Optimiser pour le cas d'usage** - désactiver fonctionnalités non nécessaires
4. **Utiliser le chunking** pour intégrations RAG
5. **Cache les résultats** pour documents fréquemment accédés
6. **Monitor la mémoire** pour gros documents
7. **Logger les opérations** pour débogage
8. **Tester avec différents formats** - chaque format a ses spécificités

### Workflow Recommandé

```
1. Validation du document
   ↓
2. Conversion avec gestion d'erreurs
   ↓
3. Extraction/transformation selon besoin
   ↓
4. Export dans format approprié
   ↓
5. Post-traitement si nécessaire
```

### Quand Utiliser Docling

✅ **Utiliser pour**:
- Extraction de contenu PDF structuré
- Conversion multi-format vers format unifié
- Préparation de documents pour RAG
- Analyse de structure de documents
- Extraction de tables et métadonnées

❌ **Ne pas utiliser pour**:
- Simple lecture de texte brut
- Édition de documents (pas d'édition, seulement lecture)
- Génération de documents (seulement parsing)
- Traitement en temps réel ultra-rapide (privilégier cache)

---

**Document généré le**: 27 octobre 2025  
**Version Docling couverte**: 1.16.0+  
**Licence**: Ce guide est fourni "as-is" pour usage avec Docling (MIT License)