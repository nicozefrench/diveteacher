import React from 'react';
import DocumentCard from './DocumentCard';

const DocumentList = ({ documents, onRetry }) => {
  if (documents.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>No documents uploaded yet.</p>
        <p className="text-sm mt-2">Upload a PDF or PPT file to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Uploaded Documents
        </h3>
        <span className="text-sm text-gray-500">
          {documents.length} document{documents.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-2">
        {documents.map((doc) => (
          <DocumentCard key={doc.id} document={doc} onRetry={onRetry} />
        ))}
      </div>
    </div>
  );
};

export default DocumentList;
