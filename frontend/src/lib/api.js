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
 * Get upload status (for polling)
 * @param {string} uploadId - Upload ID
 * @returns {Promise<Object>} Status object
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

