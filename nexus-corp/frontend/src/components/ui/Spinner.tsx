import React from 'react';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
}

const sizeClasses = {
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-8 h-8',
  xl: 'w-12 h-12',
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  color = 'text-indigo-600',
  className = '',
}) => {
  return (
    <svg
      className={`animate-spin ${sizeClasses[size]} ${color} ${className}`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
};

export const PageLoader: React.FC = () => (
  <div className="fixed inset-0 bg-white flex items-center justify-center z-50">
    <div className="text-center">
      <Spinner size="xl" />
      <p className="mt-4 text-gray-500 text-sm">Cargando...</p>
    </div>
  </div>
);
