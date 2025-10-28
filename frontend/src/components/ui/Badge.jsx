/**
 * Badge Component
 * Status badges with semantic colors
 */

import { cn } from '@/lib/utils';
import { getStatusBadgeClass } from '@/lib/utils';

export function Badge({ children, className, status, variant, ...props }) {
  const badgeClass = status 
    ? getStatusBadgeClass(status)
    : variant === 'success' ? 'dive-badge-success'
    : variant === 'warning' ? 'dive-badge-warning'
    : variant === 'error' ? 'dive-badge-error'
    : variant === 'info' ? 'dive-badge-info'
    : 'dive-badge-pending';
  
  return (
    <span 
      className={cn(
        'dive-badge',
        badgeClass,
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

