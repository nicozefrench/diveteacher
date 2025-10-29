import React from 'react';
import StatusBadge from './StatusBadge';
import ProgressBar from './ProgressBar';
import { FileText } from 'lucide-react';

export default function DocumentHeader({ document }) {
  const { 
    filename, 
    file_size_mb, 
    size,
    status, 
    progress, 
    ingestion_progress,
    stage,
    sub_stage
  } = document;

  // Calculate file size (support both size in bytes and file_size_mb)
  const displaySize = file_size_mb 
    ? file_size_mb.toFixed(2) + ' MB'
    : size 
      ? (size / (1024 * 1024)).toFixed(2) + ' MB'
      : '—';

  return (
    <div className="flex-1 min-w-0">
      {/* Document Info - Single Line */}
      <div className="flex items-center gap-3">
        <FileText className="w-5 h-5 text-blue-500 flex-shrink-0" />
        
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <span className="font-medium text-gray-900 truncate">
            {filename}
          </span>
          <span className="text-sm text-gray-500 flex-shrink-0">
            {displaySize}
          </span>
        </div>

        <StatusBadge status={status} />
      </div>

      {/* Progress Bar (only if processing) */}
      {status === 'processing' && (
        <div className="mt-2">
          <ProgressBar 
            progress={progress}
            ingestion_progress={ingestion_progress}
            stage={stage}
            sub_stage={sub_stage}
          />
        </div>
      )}
    </div>
  );
}

