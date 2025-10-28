import { CheckCircle, FileCheck, Scissors, Database, Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { STAGES } from '../../config/brand';

const stageIcons = {
  validation: FileCheck,
  conversion: FileCheck,
  chunking: Scissors,
  ingestion: Database,
};

const StageProgress = ({ currentStage }) => {
  const stageOrder = ['validation', 'conversion', 'chunking', 'ingestion'];
  const currentIndex = stageOrder.indexOf(currentStage);

  return (
    <div className="grid grid-cols-4 gap-2">
      {stageOrder.map((stage, index) => {
        const Icon = stageIcons[stage];
        const stageData = STAGES[stage];
        const isActive = index === currentIndex;
        const isComplete = index < currentIndex;
        const isPending = index > currentIndex;

        return (
          <div key={stage} className="flex flex-col items-center gap-2">
            {/* Icon */}
            <div
              className={cn(
                "relative flex h-10 w-10 items-center justify-center rounded-full transition-all duration-300",
                isComplete && "bg-success-100 text-success-700",
                isActive && "bg-primary-100 text-primary-700 animate-pulse-slow",
                isPending && "bg-gray-100 text-gray-400"
              )}
            >
              {isComplete ? (
                <CheckCircle className="h-5 w-5" />
              ) : isActive ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Icon className="h-5 w-5" />
              )}
            </div>

            {/* Label */}
            <div className="text-center">
              <p
                className={cn(
                  "text-xs font-medium transition-colors",
                  (isComplete || isActive) && "text-gray-900",
                  isPending && "text-gray-500"
                )}
              >
                {stageData.label}
              </p>
              {isActive && (
                <p className="mt-0.5 text-xs text-primary-600">
                  In progress...
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StageProgress;
