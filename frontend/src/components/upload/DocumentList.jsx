/**
 * DocumentList Component
 * Lists all uploaded documents with real-time status
 */

import { DocumentItem } from './DocumentItem';

export function DocumentList({ documents, onRetry, onRemove }) {
  if (documents.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg mb-2">No documents uploaded yet</p>
        <p className="text-sm">Upload a PDF or PowerPoint to get started</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Documents ({documents.length})
      </h2>
      
      {documents.map(doc => (
        <DocumentItem 
          key={doc.upload_id}
          document={doc}
          onRetry={onRetry}
          onRemove={onRemove}
        />
      ))}
    </div>
  );
}

