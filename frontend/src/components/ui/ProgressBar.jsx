/**
 * ProgressBar Component
 * Animated progress indicator
 */

import { cn } from '@/lib/utils';

export function ProgressBar({ progress, className, ...props }) {
  const clampedProgress = Math.min(100, Math.max(0, progress));
  
  return (
    <div 
      className={cn('dive-progress-bar', className)}
      {...props}
    >
      <div 
        className="dive-progress-fill"
        style={{ width: `${clampedProgress}%` }}
      />
    </div>
  );
}

