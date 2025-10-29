import React from 'react';
import { CheckCircle, Clock, AlertCircle, Loader } from 'lucide-react';

const statusConfig = {
  processing: {
    label: 'Processing',
    icon: Loader,
    className: 'bg-blue-100 text-blue-800 border-blue-200',
    iconClassName: 'animate-spin',
  },
  completed: {
    label: 'Complete',
    icon: CheckCircle,
    className: 'bg-green-100 text-green-800 border-green-200',
    iconClassName: '',
  },
  failed: {
    label: 'Failed',
    icon: AlertCircle,
    className: 'bg-red-100 text-red-800 border-red-200',
    iconClassName: '',
  },
  error: {
    label: 'Error',
    icon: AlertCircle,
    className: 'bg-red-100 text-red-800 border-red-200',
    iconClassName: '',
  },
  pending: {
    label: 'Pending',
    icon: Clock,
    className: 'bg-gray-100 text-gray-800 border-gray-200',
    iconClassName: '',
  },
};

export default function StatusBadge({ status }) {
  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;

  return (
    <div 
      className={`
        inline-flex items-center gap-1.5 px-3 py-1 rounded-full 
        border text-sm font-medium
        ${config.className}
      `}
    >
      <Icon className={`w-4 h-4 ${config.iconClassName}`} />
      {config.label}
    </div>
  );
}

