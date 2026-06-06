import React from 'react';
import { useLocation } from 'react-router-dom';
import { Bell, Search } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const routeTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/users': 'Gestión de Usuarios',
  '/roles': 'Roles y Permisos',
  '/knowledge': 'Base de Conocimiento',
  '/whatif': 'Análisis What-If',
  '/decisions': 'Decisiones',
  '/feedback': 'Retroalimentación',
  '/kpis': 'KPIs y Métricas',
  '/audit': 'Registro de Auditoría',
};

const roleLabels: Record<string, string> = {
  admin_sistema: 'Admin Sistema',
  admin_conocimiento: 'Admin Conocimiento',
  decisor: 'Decisor',
  analista: 'Analista',
};

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { user } = useAuth();

  const title = routeTitles[location.pathname] || 'NexusCorp';

  const initials = user?.full_name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase();

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
      </div>

      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="hidden md:flex items-center gap-2 bg-gray-100 rounded-lg px-3 py-1.5 text-sm text-gray-500">
          <Search className="w-4 h-4" />
          <span>Buscar...</span>
        </div>

        {/* Notification Bell */}
        <button className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-indigo-600 rounded-full" />
        </button>

        {/* User Avatar */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
            {initials}
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium text-gray-900 leading-none">
              {user?.full_name}
            </p>
            <p className="text-xs text-gray-500 mt-0.5">
              {user?.role ? roleLabels[user.role] ?? user.role : ''}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};
