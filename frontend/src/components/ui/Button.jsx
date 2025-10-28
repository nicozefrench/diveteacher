/**
 * Button Component
 * Reusable button with variants
 */

import { cn } from '@/lib/utils';

export function Button({ 
  children, 
  className, 
  variant = 'primary', 
  size = 'md',
  disabled,
  ...props 
}) {
  const variantClass = variant === 'primary' 
    ? 'dive-button-primary' 
    : 'dive-button-secondary';
  
  const sizeClass = size === 'sm' 
    ? 'dive-button-sm' 
    : size === 'lg' 
    ? 'dive-button-lg' 
    : '';
  
  return (
    <button 
      className={cn(
        'dive-button',
        variantClass,
        sizeClass,
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}

