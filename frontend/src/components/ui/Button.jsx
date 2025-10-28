import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

const Button = forwardRef(({ 
  className, 
  variant = 'primary',
  size = 'default',
  disabled,
  children,
  ...props 
}, ref) => {
  return (
    <button
      ref={ref}
      disabled={disabled}
      className={cn(
        "btn",
        {
          "btn-primary": variant === 'primary',
          "btn-secondary": variant === 'secondary',
          "btn-sm": size === 'sm',
          "btn-lg": size === 'lg',
        },
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export { Button };
