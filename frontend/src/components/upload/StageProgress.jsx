/**
 * StageProgress Component
 * Displays 4-stage pipeline progress:
 * 1. Validation (0-25%)
 * 2. Conversion (25-50%)
 * 3. Chunking (50-75%)
 * 4. Ingestion (75-100%)
 */

import { CheckCircle, FileText, Scissors, Database, XCircle } from 'lucide-react';
import { brand } from '@/config/brand';

const STAGE_ICONS = {
  validation: CheckCircle,
  conversion: FileText,
  chunking: Scissors,
  ingestion: Database
};

export function StageProgress({ currentStage, progress, status }) {
  const currentIndex = brand.stages.findIndex(s => s.key === currentStage);
  
  return (
    <div className="dive-stage-progress">
      {brand.stages.map((stage, index) => {
        const Icon = STAGE_ICONS[stage.key];
        const isActive = index === currentIndex;
        const isComplete = index < currentIndex || status === 'completed';
        const isFailed = status === 'failed' && index === currentIndex;
        
        const stageClass = isActive ? 'active' :
                          isComplete ? 'complete' :
                          isFailed ? 'failed' : 'pending';
        
        return (
          <div key={stage.key} className={`stage ${stageClass}`}>
            <div className="stage-icon">
              {isFailed ? <XCircle size={20} /> : <Icon size={20} />}
            </div>
            <div className="stage-label">{stage.label}</div>
            {isActive && status === 'processing' && (
              <div className="stage-progress">
                {Math.round(progress)}%
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

