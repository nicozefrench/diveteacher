/**
 * UploadTab Component
 * Main tab for document upload and monitoring
 * Handles real-time status polling
 */

import { useState, useEffect, useCallback } from 'react';
import { DocumentUpload } from './DocumentUpload';
import { DocumentList } from './DocumentList';
import { getUploadStatus } from '@/lib/api';

export function UploadTab() {
  const [documents, setDocuments] = useState([]);
  const [pollingIds, setPollingIds] = useState(new Set());
  
  // Add document to list when upload completes
  const handleUploadComplete = useCallback((newDocument) => {
    setDocuments(prev => [newDocument, ...prev]);
    setPollingIds(prev => new Set([...prev, newDocument.upload_id]));
  }, []);
  
  // Polling logic for documents in processing state
  useEffect(() => {
    if (pollingIds.size === 0) return;
    
    const pollStatus = async (uploadId) => {
      try {
        const status = await getUploadStatus(uploadId);
        
        setDocuments(prev => prev.map(doc => 
          doc.upload_id === uploadId 
            ? { ...doc, ...status }
            : doc
        ));
        
        // Stop polling if completed or failed
        if (status.status === 'completed' || status.status === 'failed') {
          setPollingIds(prev => {
            const next = new Set(prev);
            next.delete(uploadId);
            return next;
          });
        }
      } catch (error) {
        console.error(`Failed to fetch status for ${uploadId}:`, error);
      }
    };
    
    // Poll every 1 second
    const interval = setInterval(() => {
      pollingIds.forEach(uploadId => pollStatus(uploadId));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [pollingIds]);
  
  // Retry failed upload
  const handleRetry = useCallback((uploadId) => {
    // For now, just remove it (user needs to re-upload)
    setDocuments(prev => prev.filter(doc => doc.upload_id !== uploadId));
  }, []);
  
  // Remove document
  const handleRemove = useCallback((uploadId) => {
    setDocuments(prev => prev.filter(doc => doc.upload_id !== uploadId));
    setPollingIds(prev => {
      const next = new Set(prev);
      next.delete(uploadId);
      return next;
    });
  }, []);
  
  return (
    <div className="dive-container py-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Upload */}
        <div>
          <DocumentUpload 
            onUploadComplete={handleUploadComplete}
          />
        </div>
        
        {/* Right: Document List */}
        <div>
          <DocumentList 
            documents={documents}
            onRetry={handleRetry}
            onRemove={handleRemove}
          />
        </div>
      </div>
    </div>
  );
}

