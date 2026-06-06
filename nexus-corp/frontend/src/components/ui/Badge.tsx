import React from 'react';

type BadgeVariant =
  | 'default'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'gray'
  | 'indigo';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  danger: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
  gray: 'bg-gray-100 text-gray-600',
  indigo: 'bg-indigo-100 text-indigo-800',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-xs',
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}) => {
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {children}
    </span>
  );
};

export const PriorityBadge: React.FC<{ priority: 1 | 2 | 3 }> = ({ priority }) => {
  const map: Record<number, { label: string; variant: BadgeVariant }> = {
    1: { label: 'Alta', variant: 'danger' },
    2: { label: 'Media', variant: 'warning' },
    3: { label: 'Baja', variant: 'success' },
  };
  const { label, variant } = map[priority] || { label: 'N/A', variant: 'default' };
  return <Badge variant={variant}>{label}</Badge>;
};

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const map: Record<string, { label: string; variant: BadgeVariant }> = {
    pendiente: { label: 'Pendiente', variant: 'warning' },
    aceptada: { label: 'Aceptada', variant: 'success' },
    rechazada: { label: 'Rechazada', variant: 'danger' },
    active: { label: 'Activo', variant: 'success' },
    inactive: { label: 'Inactivo', variant: 'gray' },
  };
  const config = map[status] || { label: status, variant: 'default' as BadgeVariant };
  return <Badge variant={config.variant}>{config.label}</Badge>;
};
