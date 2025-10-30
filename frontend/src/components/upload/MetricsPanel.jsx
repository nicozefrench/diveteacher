import { useEffect } from 'react';
import { Clock, FileText, Layers, GitFork, Zap, CheckCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * MetricsPanel Component
 * 
 * Displays comprehensive processing metrics including:
 * - File information (size, pages, format)
 * - Processing metrics (chunks, entities, relations)
 * - Performance metrics (durations, tokens/sec)
 * - Success/failure indicators
 * 
 * FIX #19: Removed React.memo() to ensure component always re-renders
 * when parent state updates. This fixes the issue where final metrics
 * (entities, relations) were not displayed after document completion.
 * 
 * Root Cause: React.memo() was using shallow comparison, which didn't
 * detect changes in nested objects (status.metrics.entities/relations).
 * 
 * Solution: Remove memo() to guarantee re-render on every parent update.
 * Performance impact is minimal as this component is only rendered per
 * active document (typically 1-2 at a time).
 * 
 * @param {Object} props
 * @param {string} props.uploadId - Upload identifier
 * @param {Object} props.status - Current upload status
 * @param {Object} props.metadata - Document metadata
 */
const MetricsPanel = ({ uploadId, status, metadata = {} }) => {
  const metrics = status?.metrics || {};
  const durations = status?.durations || {};

  // Calculate derived metrics
  const totalDuration = durations.total || 0;
  const isCompleted = status?.status === 'completed';
  const isFailed = status?.status === 'failed';

  // Format duration helper
  const formatDuration = (seconds) => {
    if (!seconds || seconds === 0) return 'N/A';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(0);
    return `${minutes}m ${secs}s`;
  };

  // Metric card component
  const MetricCard = ({ icon: Icon, label, value, unit, color = 'gray' }) => (
    <div className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className={cn("p-2 rounded-lg", `bg-${color}-100`)}>
        <Icon className={cn("h-5 w-5", `text-${color}-600`)} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-2xl font-semibold text-gray-900 mt-1">
          {value !== undefined && value !== null ? value : '–'}
          {unit && <span className="text-base font-normal text-gray-500 ml-1">{unit}</span>}
        </p>
      </div>
    </div>
  );

  // Performance indicator
  const getPerformanceIndicator = () => {
    if (isFailed) {
      return { color: 'red', text: 'Failed', icon: '❌' };
    }
    if (!isCompleted) {
      return { color: 'blue', text: 'Processing...', icon: '⏳' };
    }
    if (totalDuration < 60) {
      return { color: 'green', text: 'Excellent', icon: '🚀' };
    }
    if (totalDuration < 120) {
      return { color: 'green', text: 'Good', icon: '✅' };
    }
    return { color: 'yellow', text: 'Acceptable', icon: '⚠️' };
  };

  const performance = getPerformanceIndicator();

  return (
    <div className="space-y-6">
      {/* Header with Status */}
      <div className="flex items-center justify-between">
        <h4 className="text-lg font-semibold text-gray-900">Processing Metrics</h4>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Performance:</span>
          <span className={cn(
            "px-3 py-1 rounded-full text-sm font-medium",
            performance.color === 'green' && "bg-green-100 text-green-700",
            performance.color === 'blue' && "bg-blue-100 text-blue-700",
            performance.color === 'yellow' && "bg-yellow-100 text-yellow-700",
            performance.color === 'red' && "bg-red-100 text-red-700"
          )}>
            {performance.icon} {performance.text}
          </span>
        </div>
      </div>

      {/* File Information */}
      <div>
        <h5 className="text-sm font-medium text-gray-700 mb-3">File Information</h5>
        <div className="grid grid-cols-2 gap-3">
          <MetricCard
            icon={FileText}
            label="File Size"
            value={metrics.file_size_mb?.toFixed(2)}
            unit="MB"
            color="blue"
          />
          <MetricCard
            icon={FileText}
            label="Pages"
            value={metrics.pages || metadata.pages}
            unit={metrics.pages === 1 ? 'page' : 'pages'}
            color="blue"
          />
        </div>
      </div>

      {/* Processing Metrics */}
      <div>
        <h5 className="text-sm font-medium text-gray-700 mb-3">Processing Results</h5>
        <div className="grid grid-cols-3 gap-3">
          <MetricCard
            icon={Layers}
            label="Chunks"
            value={metrics.num_chunks || metrics.chunks || metadata.chunks}
            unit="chunks"
            color="purple"
          />
          <MetricCard
            icon={GitFork}
            label="Entities"
            value={metrics.entities !== undefined && metrics.entities !== null ? metrics.entities : (metadata.entities || '—')}
            unit={metrics.entities !== undefined && metrics.entities !== null ? 'found' : ''}
            color="green"
          />
          <MetricCard
            icon={GitFork}
            label="Relations"
            value={metrics.relations !== undefined && metrics.relations !== null ? metrics.relations : (metadata.relations || '—')}
            unit={metrics.relations !== undefined && metrics.relations !== null ? 'found' : ''}
            color="green"
          />
        </div>
      </div>

      {/* Duration Breakdown */}
      {Object.keys(durations).length > 0 && (
        <div>
          <h5 className="text-sm font-medium text-gray-700 mb-3">Duration Breakdown</h5>
          <div className="space-y-3">
            {/* Conversion */}
            {durations.conversion > 0 && (
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700">Conversion</span>
                    <span className="font-medium text-gray-900">
                      {formatDuration(durations.conversion)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                      style={{
                        width: `${totalDuration > 0 ? (durations.conversion / totalDuration) * 100 : 0}%`
                      }}
                    />
                  </div>
                </div>
                <span className="text-xs text-gray-500 w-12 text-right">
                  {totalDuration > 0 ? `${((durations.conversion / totalDuration) * 100).toFixed(0)}%` : '0%'}
                </span>
              </div>
            )}

            {/* Chunking */}
            {durations.chunking > 0 && (
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700">Chunking</span>
                    <span className="font-medium text-gray-900">
                      {formatDuration(durations.chunking)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                      style={{
                        width: `${totalDuration > 0 ? (durations.chunking / totalDuration) * 100 : 0}%`
                      }}
                    />
                  </div>
                </div>
                <span className="text-xs text-gray-500 w-12 text-right">
                  {totalDuration > 0 ? `${((durations.chunking / totalDuration) * 100).toFixed(0)}%` : '0%'}
                </span>
              </div>
            )}

            {/* Ingestion */}
            {durations.ingestion > 0 && (
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700">Ingestion</span>
                    <span className="font-medium text-gray-900">
                      {formatDuration(durations.ingestion)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all duration-500"
                      style={{
                        width: `${totalDuration > 0 ? (durations.ingestion / totalDuration) * 100 : 0}%`
                      }}
                    />
                  </div>
                </div>
                <span className="text-xs text-gray-500 w-12 text-right">
                  {totalDuration > 0 ? `${((durations.ingestion / totalDuration) * 100).toFixed(0)}%` : '0%'}
                </span>
              </div>
            )}

            {/* Total */}
            {totalDuration > 0 && (
              <div className="pt-3 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-gray-600" />
                    <span className="text-sm font-medium text-gray-900">Total Duration</span>
                  </div>
                  <span className="text-lg font-semibold text-gray-900">
                    {formatDuration(totalDuration)}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Success Summary (for completed uploads) */}
      {isCompleted && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h5 className="text-sm font-semibold text-green-900 mb-1">
                Processing Complete
              </h5>
              <p className="text-sm text-green-700">
                Successfully processed{' '}
                {metrics.pages || metadata.pages || 0} pages into{' '}
                {metrics.num_chunks || metrics.chunks || metadata.chunks || 0} chunks in{' '}
                {formatDuration(totalDuration)}.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Summary (for failed uploads) */}
      {isFailed && status?.error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-3">
            <div className="text-red-600 text-2xl flex-shrink-0">❌</div>
            <div className="flex-1">
              <h5 className="text-sm font-semibold text-red-900 mb-1">
                Processing Failed
              </h5>
              <p className="text-sm text-red-700">
                {status.error}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Display name for debugging
MetricsPanel.displayName = 'MetricsPanel';

export default MetricsPanel;

