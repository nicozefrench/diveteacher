import React from 'react';

export default function UploadProgressBar({ progress, ingestion_progress, stage, sub_stage }) {
  // Determine progress label based on stage
  const getProgressLabel = () => {
    if (stage === 'validation' || stage === 'queued') {
      return 'Validating file...';
    } else if (stage === 'conversion') {
      return 'Converting document...';
    } else if (stage === 'chunking') {
      return 'Segmenting text...';
    } else if (stage === 'ingestion') {
      if (ingestion_progress) {
        const { chunks_completed, chunks_total, progress_pct } = ingestion_progress;
        return `Ingesting chunks (${chunks_completed}/${chunks_total} - ${progress_pct}%)`;
      }
      return 'Starting ingestion...';
    } else if (stage === 'completed') {
      return 'Complete!';
    }
    return 'Processing...';
  };

  const progressLabel = getProgressLabel();
  const displayProgress = Math.min(100, Math.max(0, progress || 0));

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">{progressLabel}</span>
        <span className="font-medium text-gray-900">{displayProgress}%</span>
      </div>
      
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={`
            h-full rounded-full transition-all duration-500 ease-out
            ${stage === 'completed' ? 'bg-green-500 shadow-sm' : 'bg-blue-500'}
          `}
          style={{ width: `${displayProgress}%` }}
        />
      </div>

      {/* Sub-progress for ingestion (optional) */}
      {ingestion_progress && stage === 'ingestion' && (
        <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
          <div className="flex-1 bg-gray-100 rounded-full h-1">
            <div
              className="h-full bg-blue-400 rounded-full transition-all duration-300"
              style={{ width: `${ingestion_progress.progress_pct}%` }}
            />
          </div>
          <span>
            Chunk {(ingestion_progress.current_chunk_index || 0) + 1}/{ingestion_progress.chunks_total}
          </span>
        </div>
      )}
    </div>
  );
}

