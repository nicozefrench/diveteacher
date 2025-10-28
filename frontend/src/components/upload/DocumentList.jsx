import DocumentItem from './DocumentItem';

const DocumentList = ({ documents, onRetry }) => {
  return (
    <div className="divide-y divide-gray-200">
      {documents.map((doc) => (
        <DocumentItem key={doc.id} document={doc} onRetry={onRetry} />
      ))}
    </div>
  );
};

export default DocumentList;
