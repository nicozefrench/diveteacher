/**
 * Card Component
 * Reusable card container with DiveTeacher styling
 */

import { cn } from '@/lib/utils';

export function Card({ children, className, active, ...props }) {
  return (
    <div 
      className={cn(
        'dive-card',
        active && 'dive-card-active',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className, ...props }) {
  return (
    <div 
      className={cn('mb-4', className)}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardTitle({ children, className, ...props }) {
  return (
    <h3 
      className={cn('text-lg font-semibold text-gray-900', className)}
      {...props}
    >
      {children}
    </h3>
  );
}

export function CardContent({ children, className, ...props }) {
  return (
    <div 
      className={cn('', className)}
      {...props}
    >
      {children}
    </div>
  );
}

