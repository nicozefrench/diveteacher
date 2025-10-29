import { FileText, RefreshCw } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import DetailedProgress from './DetailedProgress';
import ExpandableDetails from './ExpandableDetails';
import { formatBytes } from '../../lib/utils';

const DocumentItem = ({ document, onRetry }) => {
  const { filename, size, status, metadata, error } = document;

  const getStatusVariant = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'processing': return 'info';
      default: return 'pending';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed': return 'Complete';
      case 'failed': return 'Failed';
      case 'processing': return 'Processing';
      default: return 'Pending';
    }
  };

  return (
    <div className="p-6 hover:bg-gray-50 transition-colors">
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-primary-50">
          <FileText className="h-5 w-5 text-primary-600" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <h4 className="text-sm font-medium text-gray-900 truncate">
                {filename}
              </h4>
              <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                <span>{formatBytes(size)}</span>
                {metadata?.pages && (
                  <span>• {metadata.pages} pages</span>
                )}
              </div>
            </div>
            <Badge variant={getStatusVariant(status)}>
              {getStatusLabel(status)}
            </Badge>
          </div>

          {/* Enhanced Progress for Processing */}
          {status === 'processing' && (
            <div className="mt-4">
              {/* First-time upload warning - show at the top */}
              <div className="mb-4 rounded-md bg-warning-50 border border-warning-200 p-3">
                <p className="text-xs text-warning-700">
                  <strong>⏳ First upload may take 10-15 minutes</strong> while AI models are downloaded. 
                  This is normal! Subsequent uploads will be much faster (1-2 min). ⚡
                </p>
              </div>
              
              {/* NEW: Detailed Progress with sub-stages and metrics */}
              <DetailedProgress status={document} />
            </div>
          )}

          {/* Error Message */}
          {status === 'failed' && error && (
            <div className="mt-3 rounded-md bg-error-50 p-3">
              <p className="text-sm text-error-700">{error}</p>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => onRetry(document.id)}
                className="mt-2"
              >
                <RefreshCw className="h-3 w-3" />
                Retry
              </Button>
            </div>
          )}

          {/* Completion Metadata - Enhanced Display */}
          {status === 'completed' && metadata && (
            <div className="mt-4 space-y-2">
              {/* Summary Stats */}
              <div className="flex flex-wrap gap-4 text-xs text-gray-500">
                {metadata.chunks && (
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium text-gray-700">{metadata.chunks}</span>
                    <span>chunks</span>
                  </div>
                )}
                {metadata.entities && (
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium text-gray-700">{metadata.entities}</span>
                    <span>entities</span>
                  </div>
                )}
                {metadata.relations && (
                  <div className="flex items-center gap-1.5">
                    <span className="font-medium text-gray-700">{metadata.relations}</span>
                    <span>relations</span>
                  </div>
                )}
              </div>

              {/* Processing Time */}
              {metadata.durations?.total && (
                <div className="text-xs text-gray-500">
                  <span className="font-medium">Processing time:</span>{' '}
                  <span className="text-gray-700">{metadata.durations.total.toFixed(1)}s</span>
                </div>
              )}
            </div>
          )}

          {/* Expandable Details Panel (for processing and completed) */}
          {(status === 'processing' || status === 'completed') && (
            <ExpandableDetails
              uploadId={document.id}
              status={document}
              metadata={metadata}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentItem;
