import { cn } from '../../lib/utils';
import { CheckCircle2, Clock, AlertCircle, Info } from 'lucide-react';

const statusConfig = {
  success: {
    className: 'badge-success',
    icon: CheckCircle2,
  },
  warning: {
    className: 'badge-warning',
    icon: AlertCircle,
  },
  error: {
    className: 'badge-error',
    icon: AlertCircle,
  },
  info: {
    className: 'badge-info',
    icon: Info,
  },
  pending: {
    className: 'badge-gray',
    icon: Clock,
  },
};

export const Badge = ({ className, variant = 'info', showIcon = true, children, ...props }) => {
  const config = statusConfig[variant] || statusConfig.info;
  const Icon = config.icon;

  return (
    <span
      className={cn("badge", config.className, className)}
      {...props}
    >
      {showIcon && <Icon className="h-3 w-3" />}
      {children}
    </span>
  );
};
