"""
Document validation pour Docling

Ce module valide les fichiers avant traitement pour éviter crashes et erreurs.
"""
from pathlib import Path
from typing import Tuple
import logging

logger = logging.getLogger('diveteacher.validator')


class DocumentValidator:
    """Valide les fichiers avant traitement Docling"""

    SUPPORTED_EXTENSIONS = {
        '.pdf', '.docx', '.pptx', '.doc', '.ppt'
    }

    @staticmethod
    def validate(file_path: str, max_size_mb: int = 50) -> Tuple[bool, str]:
        """
        Valide un fichier document

        Args:
            file_path: Chemin vers le fichier
            max_size_mb: Taille max en MB (défaut: 50MB)

        Returns:
            (is_valid, error_message)
            - is_valid: True si fichier valide
            - error_message: Message d'erreur si invalide, "Valid" sinon
        """
        path = Path(file_path)

        # 1. Vérifier existence
        if not path.exists():
            return False, f"File does not exist: {file_path}"

        if not path.is_file():
            return False, f"Path is not a file: {file_path}"

        # 2. Vérifier extension
        if path.suffix.lower() not in DocumentValidator.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported format: {path.suffix}"

        # 3. Vérifier taille
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            return False, f"File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)"

        # 4. Test lecture basique (détection corruption)
        try:
            with open(file_path, 'rb') as f:
                f.read(1024)  # Lire premier KB
        except Exception as e:
            return False, f"File corrupted or unreadable: {str(e)}"

        logger.info(f"Validation OK: {path.name} ({size_mb:.1f}MB)")
        return True, "Valid"

