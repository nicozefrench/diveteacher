/**
 * DiveTeacher API Client
 * Handles all communication with FastAPI backend
 */

const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Upload a document
 * @param {File} file - File to upload
 * @returns {Promise<{upload_id: string, filename: string}>}
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Upload failed');
  }
  
  return response.json();
}

/**
 * Get upload status (for polling) - ENHANCED
 * @param {string} uploadId - Upload ID
 * @returns {Promise<UploadStatus>} Enhanced status object with sub_stage, metrics, durations
 * 
 * @typedef {Object} UploadStatus
 * @property {'processing'|'completed'|'failed'} status - Overall status
 * @property {string} stage - Current main stage (initialization, conversion, chunking, ingestion, completed)
 * @property {string} sub_stage - Detailed sub-stage (e.g., "processing_chunk", "validating")
 * @property {number} progress - Overall progress percentage (0-100)
 * @property {Object} progress_detail - Granular progress information
 * @property {number} progress_detail.current - Current item being processed
 * @property {number} progress_detail.total - Total items to process
 * @property {string} progress_detail.unit - Unit of measurement (e.g., "chunks", "stages")
 * @property {Object} metrics - Real-time processing metrics
 * @property {number} metrics.file_size_mb - File size in megabytes
 * @property {number} [metrics.pages] - Number of pages (if available)
 * @property {number} [metrics.chunks] - Number of chunks created
 * @property {number} [metrics.entities] - Number of entities extracted
 * @property {number} [metrics.relations] - Number of relations extracted
 * @property {number} [metrics.conversion_duration] - Conversion stage duration (seconds)
 * @property {number} [metrics.chunking_duration] - Chunking stage duration (seconds)
 * @property {number} [metrics.ingestion_duration] - Ingestion stage duration (seconds)
 * @property {Object} [durations] - Stage durations breakdown
 * @property {number} [durations.conversion] - Conversion duration (seconds)
 * @property {number} [durations.chunking] - Chunking duration (seconds)
 * @property {number} [durations.ingestion] - Ingestion duration (seconds)
 * @property {number} [durations.total] - Total processing duration (seconds)
 * @property {string} started_at - ISO timestamp of processing start
 * @property {string} [completed_at] - ISO timestamp of completion (if completed)
 * @property {string} [failed_at] - ISO timestamp of failure (if failed)
 * @property {string} [error] - Error message (if failed)
 * @property {Object} [metadata] - Additional metadata
 */
export async function getUploadStatus(uploadId) {
  const response = await fetch(`${API_BASE}/api/upload/${uploadId}/status`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch status');
  }
  
  return response.json();
}

/**
 * Stream a RAG query (SSE)
 * Returns an async generator for tokens
 * @param {string} question - User question
 * @param {Object} options - Query options
 * @returns {AsyncGenerator<Object>} SSE events
 */
export async function* streamQuery(question, options = {}) {
  const response = await fetch(`${API_BASE}/api/query/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      temperature: options.temperature || 0.7,
      max_tokens: options.max_tokens || 2000
    })
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Query failed' }));
    throw new Error(error.detail || 'Query failed');
  }
  
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line
      
      for (const line of lines) {
        if (line.trim() === '') continue;
        
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6);
          
          // Check for special [DONE] signal
          if (dataStr === '[DONE]') {
            return;
          }
          
          try {
            const data = JSON.parse(dataStr);
            yield data;
          } catch (e) {
            console.warn('Failed to parse SSE data:', dataStr);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/**
 * Check backend health
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/query/health`);
  
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  
  return response.json();
}

/**
 * Non-streaming query (for testing)
 * @param {string} question - User question
 * @param {Object} options - Query options
 * @returns {Promise<Object>} Response object
 */
export async function query(question, options = {}) {
  const response = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      temperature: options.temperature || 0.7,
      max_tokens: options.max_tokens || 2000
    })
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Query failed' }));
    throw new Error(error.detail || 'Query failed');
  }
  
  return response.json();
}

/**
 * Get upload logs for detailed monitoring
 * @param {string} uploadId - Upload identifier
 * @returns {Promise<{logs: Array}>} Structured logs array
 */
export async function getUploadLogs(uploadId) {
  const response = await fetch(`${API_BASE}/api/upload/${uploadId}/logs`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch logs');
  }
  
  return response.json();
}

/**
 * Get Neo4j statistics
 * @returns {Promise<Object>} Neo4j graph statistics
 * 
 * @typedef {Object} Neo4jStats
 * @property {Object} nodes - Node statistics
 * @property {number} nodes.total - Total number of nodes
 * @property {Object} nodes.by_label - Node counts by label
 * @property {Object} relationships - Relationship statistics
 * @property {number} relationships.total - Total number of relationships
 * @property {Object} relationships.by_type - Relationship counts by type
 * @property {Object} database - Database information
 * @property {string} database.version - Neo4j version
 * @property {string} last_updated - Last update timestamp
 */
export async function getNeo4jStats() {
  const response = await fetch(`${API_BASE}/api/neo4j/stats`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch Neo4j statistics');
  }
  
  return response.json();
}

/**
 * Execute Cypher query against Neo4j
 * @param {string} cypher - Cypher query to execute
 * @returns {Promise<Object>} Query results
 */
export async function executeNeo4jQuery(cypher) {
  const response = await fetch(`${API_BASE}/api/neo4j/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cypher })
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Query execution failed' }));
    throw new Error(error.detail || 'Query execution failed');
  }
  
  return response.json();
}

/**
 * Export Neo4j database data
 * @returns {Promise<Object>} Database export (nodes and relationships)
 */
export async function exportNeo4jData() {
  const response = await fetch(`${API_BASE}/api/neo4j/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!response.ok) {
    throw new Error('Failed to export database');
  }
  
  return response.json();
}

/**
 * Clear Neo4j database (destructive operation)
 * @param {string} confirmationCode - Confirmation code (should be "DELETE_ALL_DATA")
 * @returns {Promise<Object>} Clear operation result
 */
export async function clearNeo4jDatabase(confirmationCode) {
  const response = await fetch(`${API_BASE}/api/neo4j/clear`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      confirm: true,
      confirmation_code: confirmationCode,
      backup_first: false
    })
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to clear database' }));
    throw new Error(error.detail || 'Failed to clear database');
  }
  
  return response.json();
}

