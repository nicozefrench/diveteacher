/**
 * Spinner Component
 * Loading spinner
 */

import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Spinner({ className, size = 24, ...props }) {
  return (
    <Loader2 
      className={cn('dive-spinner', className)}
      size={size}
      {...props}
    />
  );
}

