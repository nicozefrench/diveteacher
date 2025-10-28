/**
 * DocumentItem Component
 * Single document card with status and stage progress
 */

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { StageProgress } from './StageProgress';
import { FileText, RefreshCw, Trash2 } from 'lucide-react';
import { formatFileSize, formatRelativeTime } from '@/lib/utils';

export function DocumentItem({ document, onRetry, onRemove }) {
  const { 
    upload_id, 
    filename, 
    file_size,
    status, 
    stage, 
    progress, 
    error,
    started_at,
    completed_at,
    metadata 
  } = document;
  
  const isProcessing = status === 'processing';
  const isCompleted = status === 'completed';
  const isFailed = status === 'failed';
  
  return (
    <Card className="mb-4">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3 flex-1">
            <FileText className="text-dive-primary flex-shrink-0" size={24} />
            <div className="flex-1 min-w-0">
              <CardTitle className="truncate">{filename}</CardTitle>
              <p className="text-sm text-gray-500 mt-1">
                {formatFileSize(file_size)}
                {started_at && ` · ${formatRelativeTime(new Date(started_at).getTime())}`}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2 ml-4">
            <Badge status={status}>
              {status === 'processing' ? 'Processing' :
               status === 'completed' ? 'Completed' :
               status === 'failed' ? 'Failed' : 'Pending'}
            </Badge>
            
            {isFailed && onRetry && (
              <Button 
                size="sm" 
                variant="secondary"
                onClick={() => onRetry(upload_id)}
              >
                <RefreshCw size={16} />
                Retry
              </Button>
            )}
            
            {onRemove && !isProcessing && (
              <Button 
                size="sm" 
                variant="secondary"
                onClick={() => onRemove(upload_id)}
              >
                <Trash2 size={16} />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {(isProcessing || isCompleted) && (
          <StageProgress 
            currentStage={stage}
            progress={progress}
            status={status}
          />
        )}
        
        {isFailed && error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
            <strong>Error:</strong> {error}
          </div>
        )}
        
        {isCompleted && metadata && (
          <div className="mt-3 flex gap-4 text-sm text-gray-600">
            {metadata.chunks && (
              <span>📄 {metadata.chunks} chunks</span>
            )}
            {metadata.entities && (
              <span>🏷️ {metadata.entities} entities</span>
            )}
            {metadata.relations && (
              <span>🔗 {metadata.relations} relations</span>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

