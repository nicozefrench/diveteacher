import { FileText, RefreshCw } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import StageProgress from './StageProgress';
import { formatBytes } from '../../lib/utils';

const DocumentItem = ({ document, onRetry }) => {
  const { filename, size, status, current_stage, metadata, error } = document;

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
              <p className="mt-1 text-xs text-gray-500">
                {formatBytes(size)}
              </p>
            </div>
            <Badge variant={getStatusVariant(status)}>
              {getStatusLabel(status)}
            </Badge>
          </div>

          {/* Stage Progress */}
          {status === 'processing' && (
            <div className="mt-4">
              <StageProgress currentStage={current_stage} />
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

          {/* Metadata */}
          {status === 'completed' && metadata && (
            <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-500">
              {metadata.chunks_created && (
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-gray-700">{metadata.chunks_created}</span>
                  <span>chunks</span>
                </div>
              )}
              {metadata.entities_extracted && (
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-gray-700">{metadata.entities_extracted}</span>
                  <span>entities</span>
                </div>
              )}
              {metadata.relations_created && (
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-gray-700">{metadata.relations_created}</span>
                  <span>relations</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentItem;
