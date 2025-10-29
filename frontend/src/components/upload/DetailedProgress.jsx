import { memo } from 'react';
import { Clock, Zap, Database, FileText } from 'lucide-react';
import { formatSubStageLabel, getSubStageConfig } from '../../config/brand';
import { cn } from '../../lib/utils';

/**
 * DetailedProgress Component
 * Displays real-time progress with sub-stages, metrics, and durations
 * 
 * Optimized with React.memo to prevent unnecessary re-renders
 * 
 * @param {Object} status - Enhanced status object from backend
 * @param {string} status.stage - Current main stage
 * @param {string} status.sub_stage - Current sub-stage
 * @param {number} status.progress - Overall progress (0-100)
 * @param {Object} status.progress_detail - Granular progress {current, total, unit}
 * @param {Object} status.metrics - Real-time metrics
 * @param {Object} status.durations - Stage durations
 */
const DetailedProgress = memo(({ status }) => {
  if (!status) return null;

  const {
    stage,
    sub_stage,
    progress,
    progress_detail,
    metrics,
    durations,
  } = status;

  // Get sub-stage configuration
  const subStageConfig = getSubStageConfig(stage, sub_stage);
  const formattedLabel = formatSubStageLabel(stage, sub_stage, progress_detail);

  return (
    <div className="space-y-4">
      {/* Current Sub-Stage (Prominent Display) */}
      <CurrentSubStage
        stage={stage}
        subStage={sub_stage}
        formattedLabel={formattedLabel}
        subStageConfig={subStageConfig}
        progressDetail={progress_detail}
      />

      {/* Progress Bar with Granular Info */}
      <ProgressBar
        progress={progress}
        progressDetail={progress_detail}
      />

      {/* Live Metrics Grid */}
      {metrics && (
        <MetricsGrid metrics={metrics} stage={stage} />
      )}

      {/* Duration Display */}
      {durations && (
        <DurationDisplay durations={durations} />
      )}
    </div>
  );
});

// Display name for debugging
DetailedProgress.displayName = 'DetailedProgress';

/**
 * CurrentSubStage - Large display of current processing activity
 */
const CurrentSubStage = ({ stage, subStage, formattedLabel, subStageConfig, progressDetail }) => {
  return (
    <div className="rounded-lg bg-primary-50 border border-primary-200 p-4">
      <div className="flex items-center gap-3">
        {/* Icon */}
        <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-primary-100">
          <span className="text-2xl" role="img" aria-label="stage-icon">
            {subStageConfig?.icon || '⏳'}
          </span>
        </div>

        {/* Label and Description */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="text-sm font-semibold text-primary-900">
              {formattedLabel}
            </p>
            {progressDetail?.unit && (
              <span className="text-xs text-primary-600 font-medium">
                ({progressDetail.current}/{progressDetail.total} {progressDetail.unit})
              </span>
            )}
          </div>
          {subStageConfig?.description && (
            <p className="mt-1 text-xs text-primary-700">
              {subStageConfig.description}
            </p>
          )}
        </div>

        {/* Animated Pulse Indicator */}
        <div className="flex-shrink-0">
          <div className="h-3 w-3 rounded-full bg-primary-500 animate-pulse" />
        </div>
      </div>
    </div>
  );
};

/**
 * ProgressBar - Granular progress visualization
 */
const ProgressBar = ({ progress, progressDetail }) => {
  const progressPercentage = Math.min(Math.max(progress || 0, 0), 100);
  
  let label = `${progressPercentage}%`;
  if (progressDetail?.current !== undefined && progressDetail?.total !== undefined) {
    label = `${progressDetail.current}/${progressDetail.total} ${progressDetail.unit || 'items'} (${progressPercentage}%)`;
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-gray-600">
        <span className="font-medium">Progress</span>
        <span className="font-semibold">{label}</span>
      </div>
      
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className={cn(
            "h-full transition-all duration-300 ease-out",
            "bg-gradient-to-r from-primary-500 to-primary-600"
          )}
          style={{ width: `${progressPercentage}%` }}
          role="progressbar"
          aria-valuenow={progressPercentage}
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>
    </div>
  );
};

/**
 * MetricsGrid - Display live processing metrics
 */
const MetricsGrid = ({ metrics, stage }) => {
  const metricItems = [];

  // Document metrics
  if (metrics.file_size_mb !== undefined) {
    metricItems.push({
      icon: FileText,
      label: 'File Size',
      value: `${metrics.file_size_mb.toFixed(2)} MB`,
      color: 'text-blue-600',
    });
  }

  if (metrics.pages !== undefined) {
    metricItems.push({
      icon: FileText,
      label: 'Pages',
      value: metrics.pages,
      color: 'text-blue-600',
    });
  }

  // Processing metrics
  if (metrics.chunks !== undefined) {
    metricItems.push({
      icon: Zap,
      label: 'Chunks',
      value: metrics.chunks,
      color: 'text-amber-600',
    });
  }

  // Knowledge graph metrics
  if (metrics.entities !== undefined) {
    metricItems.push({
      icon: Database,
      label: 'Entities',
      value: metrics.entities,
      color: 'text-green-600',
    });
  }

  if (metrics.relations !== undefined) {
    metricItems.push({
      icon: Database,
      label: 'Relations',
      value: metrics.relations,
      color: 'text-green-600',
    });
  }

  // Stage durations (show for completed stages)
  if (metrics.conversion_duration !== undefined && stage !== 'conversion') {
    metricItems.push({
      icon: Clock,
      label: 'Conversion',
      value: `${metrics.conversion_duration.toFixed(1)}s`,
      color: 'text-purple-600',
    });
  }

  if (metrics.chunking_duration !== undefined && stage !== 'chunking') {
    metricItems.push({
      icon: Clock,
      label: 'Chunking',
      value: `${metrics.chunking_duration.toFixed(1)}s`,
      color: 'text-purple-600',
    });
  }

  if (metricItems.length === 0) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {metricItems.map((item, index) => (
        <MetricCard key={index} {...item} />
      ))}
    </div>
  );
};

/**
 * MetricCard - Individual metric display
 */
const MetricCard = ({ icon: Icon, label, value, color }) => {
  return (
    <div className="rounded-lg bg-gray-50 border border-gray-200 p-3">
      <div className="flex items-center gap-2">
        <Icon className={cn("h-4 w-4 flex-shrink-0", color)} />
        <div className="flex-1 min-w-0">
          <p className="text-xs text-gray-600 truncate">{label}</p>
          <p className="text-sm font-semibold text-gray-900 truncate">{value}</p>
        </div>
      </div>
    </div>
  );
};

/**
 * DurationDisplay - Show stage durations breakdown
 */
const DurationDisplay = ({ durations }) => {
  const stages = [
    { key: 'conversion', label: 'Conversion', color: 'bg-blue-500' },
    { key: 'chunking', label: 'Chunking', color: 'bg-amber-500' },
    { key: 'ingestion', label: 'Ingestion', color: 'bg-green-500' },
  ];

  const total = durations.total || 0;
  const hasDurations = stages.some(s => durations[s.key] !== undefined);

  if (!hasDurations) return null;

  return (
    <div className="rounded-lg bg-gray-50 border border-gray-200 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Clock className="h-4 w-4 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">Processing Time</span>
      </div>
      
      <div className="space-y-2">
        {stages.map(({ key, label, color }) => {
          const duration = durations[key];
          if (duration === undefined) return null;
          
          const percentage = total > 0 ? (duration / total) * 100 : 0;
          
          return (
            <div key={key} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-600">{label}</span>
                <span className="font-semibold text-gray-900">{duration.toFixed(1)}s</span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
                <div
                  className={cn("h-full transition-all duration-300", color)}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
        
        {total > 0 && (
          <div className="pt-2 mt-2 border-t border-gray-300">
            <div className="flex items-center justify-between text-xs">
              <span className="font-medium text-gray-700">Total Time</span>
              <span className="font-bold text-gray-900">{total.toFixed(1)}s</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DetailedProgress;

