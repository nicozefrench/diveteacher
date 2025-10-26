"""
Dockling Integration

Handles PDF/PPT → Markdown conversion using Dockling.
"""

import asyncio
from pathlib import Path
from docling.document_converter import DocumentConverter

from app.core.config import settings


async def convert_document_to_markdown(file_path: str) -> str:
    """
    Convert document (PDF, PPT, etc.) to markdown using Dockling
    
    Args:
        file_path: Path to document file
        
    Returns:
        Markdown string
        
    Raises:
        RuntimeError: If conversion fails
    """
    
    try:
        # Run Dockling in thread pool (it's CPU-bound)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            _convert_sync, 
            file_path
        )
        return result
        
    except Exception as e:
        raise RuntimeError(f"Dockling conversion failed: {e}")


def _convert_sync(file_path: str) -> str:
    """
    Synchronous Dockling conversion (runs in thread pool)
    
    Args:
        file_path: Path to document
        
    Returns:
        Markdown string
    """
    
    # Initialize Dockling converter
    converter = DocumentConverter()
    
    # Convert document
    result = converter.convert(file_path)
    
    # Export to markdown
    markdown = result.document.export_to_markdown()
    
    return markdown

