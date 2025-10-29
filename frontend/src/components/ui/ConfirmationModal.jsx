import { useState } from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * ConfirmationModal Component
 * 
 * Modal for confirming destructive actions with code verification:
 * - Displays warning message
 * - Requires typing confirmation code
 * - Supports different variants (danger, warning)
 * - Prevents accidental data loss
 * 
 * @param {Object} props
 * @param {string} props.title - Modal title
 * @param {string} props.message - Warning message
 * @param {string} props.confirmationCode - Code user must type (e.g., "DELETE_ALL_DATA")
 * @param {Function} props.onConfirm - Callback with confirmation code
 * @param {Function} props.onCancel - Cancel callback
 * @param {boolean} props.isProcessing - Show processing state
 * @param {'danger'|'warning'} props.variant - Visual variant
 * @returns {JSX.Element} Confirmation modal
 */
const ConfirmationModal = ({
  title,
  message,
  confirmationCode,
  onConfirm,
  onCancel,
  isProcessing = false,
  variant = 'danger'
}) => {
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState('');

  const isValid = inputValue === confirmationCode;

  const handleConfirm = () => {
    if (!isValid) {
      setError(`Please type "${confirmationCode}" to confirm`);
      return;
    }
    onConfirm(confirmationCode);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && isValid) {
      handleConfirm();
    } else if (e.key === 'Escape') {
      onCancel();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={isProcessing ? undefined : onCancel}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6 space-y-4">
        {/* Header */}
        <div className="flex items-start gap-4">
          <div className={cn(
            "p-2 rounded-lg",
            variant === 'danger' && "bg-red-100",
            variant === 'warning' && "bg-yellow-100"
          )}>
            <AlertTriangle className={cn(
              "h-6 w-6",
              variant === 'danger' && "text-red-600",
              variant === 'warning' && "text-yellow-600"
            )} />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <button
              onClick={onCancel}
              disabled={isProcessing}
              className="absolute top-4 right-4 p-1 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Message */}
        <div className={cn(
          "p-4 rounded-lg",
          variant === 'danger' && "bg-red-50 border border-red-200",
          variant === 'warning' && "bg-yellow-50 border border-yellow-200"
        )}>
          <p className={cn(
            "text-sm",
            variant === 'danger' && "text-red-700",
            variant === 'warning' && "text-yellow-700"
          )}>
            {message}
          </p>
        </div>

        {/* Confirmation Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type <code className="px-2 py-0.5 bg-gray-100 rounded text-red-600 font-mono text-xs">{confirmationCode}</code> to confirm:
          </label>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              setError('');
            }}
            onKeyDown={handleKeyDown}
            disabled={isProcessing}
            placeholder={confirmationCode}
            className={cn(
              "w-full px-3 py-2 border rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent",
              error ? "border-red-500" : "border-gray-300",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
            autoFocus
          />
          {error && (
            <p className="mt-1 text-xs text-red-600">{error}</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            onClick={onCancel}
            disabled={isProcessing}
            className="px-4 py-2 rounded-lg text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={!isValid || isProcessing}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              variant === 'danger' && "bg-red-600 hover:bg-red-700",
              variant === 'warning' && "bg-yellow-600 hover:bg-yellow-700"
            )}
          >
            {isProcessing ? 'Processing...' : 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;

