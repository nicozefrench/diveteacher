/**
 * DiveTeacher Brand Configuration
 * Application constants and configuration
 */

export const APP_NAME = 'DiveTeacher';
export const TAGLINE = 'AI-Powered RAG Knowledge System';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Upload configuration
export const UPLOAD_MAX_FILE_SIZE_MB = 50;
export const SUPPORTED_FILE_TYPES = ['PDF', 'PPT', 'PPTX'];

// Processing stages
export const STAGES = {
  validation: {
    key: 'validation',
    label: 'Validation',
    description: 'File format and integrity check',
  },
  conversion: {
    key: 'conversion',
    label: 'Conversion',
    description: 'Document parsing with Docling',
  },
  chunking: {
    key: 'chunking',
    label: 'Chunking',
    description: 'Text segmentation for RAG',
  },
  ingestion: {
    key: 'ingestion',
    label: 'Ingestion',
    description: 'Knowledge graph integration with Graphiti',
  },
};

// Health check interval
export const HEALTH_CHECK_INTERVAL_MS = 30000;
