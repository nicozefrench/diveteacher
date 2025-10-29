import { cn } from '../../lib/utils';

/**
 * Card Component
 * 
 * Container component with consistent styling
 */
export const Card = ({ children, className }) => (
  <div className={cn("bg-white rounded-lg border border-gray-200 shadow-sm", className)}>
    {children}
  </div>
);

/**
 * CardHeader Component
 * 
 * Card header section
 */
export const CardHeader = ({ children, className }) => (
  <div className={cn("px-6 py-4 border-b border-gray-200", className)}>
    {children}
  </div>
);

/**
 * CardBody Component
 * 
 * Card body section
 */
export const CardBody = ({ children, className }) => (
  <div className={cn("px-6 py-4", className)}>
    {children}
  </div>
);

/**
 * CardTitle Component
 * 
 * Card title
 */
export const CardTitle = ({ children, className }) => (
  <h3 className={cn("text-lg font-semibold text-gray-900", className)}>
    {children}
  </h3>
);

/**
 * CardDescription Component
 * 
 * Card description/subtitle
 */
export const CardDescription = ({ children, className }) => (
  <p className={cn("text-sm text-gray-600 mt-1", className)}>
    {children}
  </p>
);
