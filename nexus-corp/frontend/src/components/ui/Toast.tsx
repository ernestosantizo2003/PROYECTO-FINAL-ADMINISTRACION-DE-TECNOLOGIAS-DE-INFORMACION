import React from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import { Toast as ToastType, ToastType as ToastVariant } from '../../hooks/useToast';

interface ToastItemProps {
  toast: ToastType;
  onRemove: (id: string) => void;
}

const iconMap: Record<ToastVariant, React.ReactNode> = {
  success: <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />,
  error: <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />,
  warning: <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0" />,
  info: <Info className="w-5 h-5 text-blue-500 flex-shrink-0" />,
};

const bgMap: Record<ToastVariant, string> = {
  success: 'border-l-4 border-green-500',
  error: 'border-l-4 border-red-500',
  warning: 'border-l-4 border-yellow-500',
  info: 'border-l-4 border-blue-500',
};

const ToastItem: React.FC<ToastItemProps> = ({ toast, onRemove }) => (
  <div
    className={`flex items-start gap-3 bg-white rounded-lg shadow-lg p-4 min-w-[300px] max-w-[420px] animate-in slide-in-from-right-full ${bgMap[toast.type]}`}
  >
    {iconMap[toast.type]}
    <p className="text-sm text-gray-800 flex-1">{toast.message}</p>
    <button
      onClick={() => onRemove(toast.id)}
      className="text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
    >
      <X className="w-4 h-4" />
    </button>
  </div>
);

interface ToastContainerProps {
  toasts: ToastType[];
  onRemove: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={onRemove} />
      ))}
    </div>
  );
};
