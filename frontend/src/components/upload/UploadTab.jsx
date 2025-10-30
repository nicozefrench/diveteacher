import { useState, useEffect, useRef } from 'react';
import { AlertCircle } from 'lucide-react';
import DocumentUpload from './DocumentUpload';
import DocumentList from './DocumentList';
import { Card, CardHeader, CardBody, CardTitle, CardDescription } from '../ui/Card';
import { uploadDocument, getUploadStatus } from '../../lib/api';

const UploadTab = () => {
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [retryAttempts, setRetryAttempts] = useState({}); // Track retry attempts per document
  const pollIntervalsRef = useRef({}); // Track polling intervals
  const isVisibleRef = useRef(true); // Track tab visibility

  const handleFileUpload = async (file) => {
    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadDocument(file);
      const newDoc = {
        id: response.upload_id,
        filename: file.name,
        size: file.size,
        status: 'processing',
        current_stage: 'validation',
        metadata: {},
      };

      setDocuments(prev => [newDoc, ...prev]);

      // Start polling for this document
      pollDocumentStatus(response.upload_id);
    } catch (err) {
      setError(err.message || 'Failed to upload document');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const pollDocumentStatus = (uploadId) => {
    // Clear existing interval if any
    if (pollIntervalsRef.current[uploadId]) {
      clearInterval(pollIntervalsRef.current[uploadId]);
    }

    const interval = setInterval(async () => {
      // Skip polling if tab not visible
      if (!isVisibleRef.current) {
        return;
      }

      try {
        const status = await getUploadStatus(uploadId);
        
        setDocuments(prev => 
          prev.map(doc => 
            doc.id === uploadId 
              ? {
                  ...doc,
                  // Map all enhanced status fields
                  status: status.status,
                  stage: status.stage,
                  sub_stage: status.sub_stage,
                  progress: status.progress,
                  progress_detail: status.progress_detail,
                  ingestion_progress: status.ingestion_progress,  // ← Bug #9 Fix: Real-time chunk progress
                  metrics: status.metrics || {},
                  durations: status.durations,
                  metadata: status.metadata || {},
                  error: status.error,
                  started_at: status.started_at,
                  completed_at: status.completed_at,
                  failed_at: status.failed_at,
                  // Preserve original filename and size
                  filename: doc.filename,
                  file_size_mb: doc.file_size_mb,
                  size: doc.size,
                }
              : doc
          )
        );

        // 🔍 DEBUG: Phase 1 Investigation - Track data flow
        console.log(`[UploadTab] Updated document ${uploadId}:`, {
          timestamp: new Date().toISOString(),
          status: status.status,
          metrics_from_api: JSON.parse(JSON.stringify(status.metrics || {})),
          metadata_from_api: JSON.parse(JSON.stringify(status.metadata || {})),
          metrics_entities: status.metrics?.entities,
          metrics_relations: status.metrics?.relations,
          metadata_entities: status.metadata?.entities,
          metadata_relations: status.metadata?.relations
        });

        // Handle timeout errors with auto-retry (max 2 attempts)
        if (status.status === 'failed' && status.error && status.error.includes('timeout')) {
          const attempts = retryAttempts[uploadId] || 0;
          
          if (attempts < 2) {
            console.log(`Timeout detected for ${uploadId}, auto-retry attempt ${attempts + 1}/2`);
            
            // Update retry count
            setRetryAttempts(prev => ({
              ...prev,
              [uploadId]: attempts + 1
            }));
            
            // Wait 5 seconds before retry
            setTimeout(() => {
              setDocuments(prev =>
                prev.map(d =>
                  d.id === uploadId
                    ? { 
                        ...d, 
                        status: 'processing', 
                        stage: 'initialization',
                        sub_stage: 'starting',
                        error: `Retrying (attempt ${attempts + 2}/3)...` 
                      }
                    : d
                )
              );
              
              // Don't clear interval, keep polling
            }, 5000);
            
            return; // Don't clear interval yet
          } else {
            console.log(`Max retry attempts reached for ${uploadId}`);
            // Clear interval after max retries
            clearInterval(interval);
            delete pollIntervalsRef.current[uploadId];
          }
        }

        // FIX #16: Never stop polling for 'completed' status to eliminate race condition
        // Why: React's setDocuments() is async (scheduled), but clearInterval() is sync
        // The "one more poll" approach (Fix #14) failed because polling stopped before
        // React finished updating the UI with final metrics.
        // Solution: Let polling continue indefinitely for completed docs. This:
        //   - Eliminates race condition entirely
        //   - Ensures metrics always display (React has unlimited time to update)
        //   - Has minimal overhead (API is fast ~50ms for completed docs)
        //   - Cleanup happens naturally on component unmount (useEffect below)
        
        // Only stop polling for actual failures (not completion)
        if (status.status === 'failed') {
          console.log(`Document ${uploadId} failed, stopping polling`);
          clearInterval(interval);
          delete pollIntervalsRef.current[uploadId];
        }
        
        // For 'completed' status: Continue polling indefinitely
        // User can navigate away anytime (polling stops via useEffect cleanup)
      } catch (err) {
        console.error('Status poll error:', err);
        // Continue polling even on error (might be temporary network issue)
      }
    }, 1500); // Poll every 1.5 seconds
    
    // Store interval reference
    pollIntervalsRef.current[uploadId] = interval;
  };

  // Detect tab visibility for optimized polling
  useEffect(() => {
    const handleVisibilityChange = () => {
      isVisibleRef.current = !document.hidden;
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  // Cleanup all intervals on unmount
  useEffect(() => {
    return () => {
      Object.values(pollIntervalsRef.current).forEach(interval => clearInterval(interval));
    };
  }, []);

  const handleRetry = async (documentId) => {
    // Find the document
    const doc = documents.find(d => d.id === documentId);
    if (!doc) return;

    // Reset status and retry
    setDocuments(prev =>
      prev.map(d =>
        d.id === documentId
          ? { ...d, status: 'processing', current_stage: 'validation', error: null }
          : d
      )
    );

    // Resume polling
    pollDocumentStatus(documentId);
  };

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {/* Upload Card */}
      <div className="lg:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle>Upload Document</CardTitle>
            <CardDescription>
              Upload PDF or PowerPoint files to add to the knowledge graph
            </CardDescription>
          </CardHeader>
          <CardBody>
            <DocumentUpload 
              onFileSelect={handleFileUpload}
              isUploading={isUploading}
            />
            
            {error && (
              <div className="mt-4 flex items-start gap-3 rounded-md bg-error-50 p-4">
                <AlertCircle className="h-5 w-5 flex-shrink-0 text-error-500" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-error-800">Upload Failed</p>
                  <p className="mt-1 text-sm text-error-700">{error}</p>
                </div>
              </div>
            )}

            {/* Info Box */}
            <div className="mt-6 rounded-md bg-gray-50 p-4">
              <h4 className="text-sm font-medium text-gray-900">Processing Stages</h4>
              <ul className="mt-3 space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="font-medium text-gray-900">1.</span>
                  <span><strong>Validation:</strong> File format and integrity check</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-medium text-gray-900">2.</span>
                  <span><strong>Conversion:</strong> Document parsing with Docling</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-medium text-gray-900">3.</span>
                  <span><strong>Chunking:</strong> Text segmentation for RAG</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="font-medium text-gray-900">4.</span>
                  <span><strong>Ingestion:</strong> Knowledge graph integration</span>
                </li>
              </ul>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Documents List */}
      <div className="lg:col-span-2">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Uploaded Documents</CardTitle>
                <CardDescription>
                  Track the processing status of your documents
                </CardDescription>
              </div>
              {documents.length > 0 && (
                <span className="badge badge-gray">
                  {documents.length} {documents.length === 1 ? 'document' : 'documents'}
                </span>
              )}
            </div>
          </CardHeader>
          <CardBody className="p-0">
            {documents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
                  <svg
                    className="h-6 w-6 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                </div>
                <h3 className="mt-4 text-sm font-semibold text-gray-900">No documents yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Upload a PDF or PowerPoint to get started
                </p>
              </div>
            ) : (
              <DocumentList documents={documents} onRetry={handleRetry} />
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  );
};

export default UploadTab;
