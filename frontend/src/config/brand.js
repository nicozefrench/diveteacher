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

/**
 * Sub-stages for detailed progress tracking
 * Maps backend sub_stage values to user-friendly labels
 */
export const SUB_STAGES = {
  initialization: {
    starting: {
      label: 'Initializing pipeline...',
      icon: '🚀',
      description: 'Setting up processing environment'
    },
  },
  conversion: {
    validating: {
      label: 'Validating document format...',
      icon: '🔍',
      description: 'Checking file format and integrity'
    },
    loading_models: {
      label: 'Loading Docling models...',
      icon: '📦',
      description: 'Preparing AI models for document analysis'
    },
    converting: {
      label: 'Converting to structured format...',
      icon: '⚙️',
      description: 'Parsing document with OCR and TableFormer'
    },
    extracting_metadata: {
      label: 'Extracting metadata...',
      icon: '📋',
      description: 'Analyzing document properties and structure'
    },
    conversion_complete: {
      label: 'Conversion complete ✓',
      icon: '✅',
      description: 'Document successfully parsed'
    },
  },
  chunking: {
    tokenizing: {
      label: 'Tokenizing document...',
      icon: '🔤',
      description: 'Breaking text into semantic units'
    },
    creating_chunks: {
      label: 'Creating semantic chunks...',
      icon: '✂️',
      description: 'Dividing content into optimized chunks'
    },
    chunking_complete: {
      label: 'Chunking complete ✓',
      icon: '✅',
      description: 'Text segmentation finished'
    },
  },
  ingestion: {
    preparing: {
      label: 'Preparing for ingestion...',
      icon: '🔧',
      description: 'Setting up knowledge graph connection'
    },
    processing_chunk: {
      label: 'Processing chunk {current}/{total}...',
      icon: '🔄',
      description: 'Extracting entities and relations from chunk'
    },
    extracting_entities: {
      label: 'Extracting entities and relations...',
      icon: '🕸️',
      description: 'Identifying knowledge graph elements'
    },
    writing_to_neo4j: {
      label: 'Writing to knowledge graph...',
      icon: '💾',
      description: 'Storing data in Neo4j database'
    },
    ingestion_complete: {
      label: 'Ingestion complete ✓',
      icon: '✅',
      description: 'Knowledge graph successfully updated'
    },
  },
  completed: {
    finalized: {
      label: 'Processing complete! 🎉',
      icon: '🎉',
      description: 'Document ready for queries'
    },
  },
  failed: {
    error: {
      label: 'Processing failed',
      icon: '❌',
      description: 'An error occurred during processing'
    },
  },
};

/**
 * Format sub-stage label with dynamic values
 * @param {string} stage - Main stage
 * @param {string} subStage - Sub-stage key
 * @param {Object} progressDetail - Progress detail object {current, total, unit}
 * @returns {string} Formatted label
 */
export function formatSubStageLabel(stage, subStage, progressDetail = {}) {
  const subStageConfig = SUB_STAGES[stage]?.[subStage];
  if (!subStageConfig) return subStage;
  
  let label = subStageConfig.label;
  
  // Replace dynamic placeholders
  if (progressDetail.current !== undefined && progressDetail.total !== undefined) {
    label = label.replace('{current}', progressDetail.current);
    label = label.replace('{total}', progressDetail.total);
  }
  
  return label;
}

/**
 * Get sub-stage configuration
 * @param {string} stage - Main stage
 * @param {string} subStage - Sub-stage key
 * @returns {Object|null} Sub-stage config or null if not found
 */
export function getSubStageConfig(stage, subStage) {
  return SUB_STAGES[stage]?.[subStage] || null;
}

// Health check interval
export const HEALTH_CHECK_INTERVAL_MS = 30000;
