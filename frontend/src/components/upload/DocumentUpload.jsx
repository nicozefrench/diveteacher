/**
 * DocumentUpload Component
 * Drag-and-drop file upload with validation
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { uploadDocument } from '@/lib/api';

const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.ms-powerpoint': ['.ppt'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx']
};

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export function DocumentUpload({ onUploadStart, onUploadComplete, onUploadError }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  
  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors[0]?.code === 'file-too-large') {
        setError('File is too large. Maximum size is 50MB.');
      } else if (rejection.errors[0]?.code === 'file-invalid-type') {
        setError('Invalid file type. Only PDF, PPT, and PPTX are supported.');
      } else {
        setError('File rejected. Please try again.');
      }
      return;
    }
    
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    setError(null);
    setUploading(true);
    
    try {
      // Notify parent that upload is starting
      if (onUploadStart) {
        onUploadStart(file);
      }
      
      // Upload the file
      const result = await uploadDocument(file);
      
      // Notify parent that upload completed
      if (onUploadComplete) {
        onUploadComplete({
          upload_id: result.upload_id,
          filename: result.filename,
          file_size: file.size,
          status: 'processing',
          stage: 'validation',
          progress: 0,
          started_at: new Date().toISOString(),
          completed_at: null,
          error: null,
          metadata: null
        });
      }
      
      setUploading(false);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message || 'Upload failed. Please try again.');
      setUploading(false);
      
      if (onUploadError) {
        onUploadError(err);
      }
    }
  }, [onUploadStart, onUploadComplete, onUploadError]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    disabled: uploading
  });
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Document</CardTitle>
      </CardHeader>
      
      <CardContent>
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors
            ${isDragActive ? 'border-dive-primary bg-blue-50' : 'border-gray-300 hover:border-dive-primary'}
            ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center gap-4">
            {uploading ? (
              <>
                <Upload className="text-dive-primary animate-bounce" size={48} />
                <p className="text-lg font-medium text-gray-700">
                  Uploading...
                </p>
              </>
            ) : isDragActive ? (
              <>
                <FileText className="text-dive-primary" size={48} />
                <p className="text-lg font-medium text-gray-700">
                  Drop the file here
                </p>
              </>
            ) : (
              <>
                <Upload className="text-gray-400" size={48} />
                <div>
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    Drag & drop a file here, or click to select
                  </p>
                  <p className="text-sm text-gray-500">
                    Supported formats: PDF, PPT, PPTX (max 50MB)
                  </p>
                </div>
                <Button variant="primary" disabled={uploading}>
                  <Upload size={20} />
                  Select File
                </Button>
              </>
            )}
          </div>
        </div>
        
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded flex items-start gap-2">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
        
        <div className="mt-4 text-sm text-gray-600 space-y-1">
          <p><strong>Processing stages:</strong></p>
          <ul className="list-disc list-inside space-y-0.5 ml-2">
            <li>Validation: File format and integrity check</li>
            <li>Conversion: Document parsing with Docling</li>
            <li>Chunking: Text segmentation for RAG</li>
            <li>Ingestion: Knowledge graph integration with Graphiti</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

