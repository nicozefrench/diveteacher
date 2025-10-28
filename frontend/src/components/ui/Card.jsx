import { cn } from '../../lib/utils';

export const Card = ({ className, children, ...props }) => {
  return (
    <div
      className={cn(
        "card hover:shadow-card-hover transition-shadow duration-200",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ className, children, ...props }) => {
  return (
    <div className={cn("card-header", className)} {...props}>
      {children}
    </div>
  );
};

export const CardBody = ({ className, children, ...props }) => {
  return (
    <div className={cn("card-body", className)} {...props}>
      {children}
    </div>
  );
};

export const CardFooter = ({ className, children, ...props }) => {
  return (
    <div className={cn("card-footer", className)} {...props}>
      {children}
    </div>
  );
};

export const CardTitle = ({ className, children, ...props }) => {
  return (
    <h3
      className={cn("text-lg font-semibold text-gray-900", className)}
      {...props}
    >
      {children}
    </h3>
  );
};

export const CardDescription = ({ className, children, ...props }) => {
  return (
    <p
      className={cn("mt-1 text-sm text-gray-500", className)}
      {...props}
    >
      {children}
    </p>
  );
};
