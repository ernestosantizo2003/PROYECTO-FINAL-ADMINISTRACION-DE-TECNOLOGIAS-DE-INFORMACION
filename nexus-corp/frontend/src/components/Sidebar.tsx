import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Shield,
  BookOpen,
  GitBranch,
  FileText,
  MessageSquare,
  BarChart3,
  ClipboardList,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Cpu,
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  roles?: string[];
}

const navItems: NavItem[] = [
  {
    path: '/dashboard',
    label: 'Dashboard',
    icon: <LayoutDashboard className="w-5 h-5" />,
  },
  {
    path: '/decisions',
    label: 'Decisiones',
    icon: <FileText className="w-5 h-5" />,
  },
  {
    path: '/feedback',
    label: 'Retroalimentación',
    icon: <MessageSquare className="w-5 h-5" />,
  },
  {
    path: '/whatif',
    label: 'Análisis What-If',
    icon: <GitBranch className="w-5 h-5" />,
    roles: ['decisor', 'admin_sistema'],
  },
  {
    path: '/knowledge',
    label: 'Reglas de Conocimiento',
    icon: <BookOpen className="w-5 h-5" />,
    roles: ['admin_conocimiento', 'admin_sistema', 'decisor'],
  },
  {
    path: '/kpis',
    label: 'KPIs',
    icon: <BarChart3 className="w-5 h-5" />,
    roles: ['analista', 'admin_sistema', 'decisor'],
  },
  {
    path: '/users',
    label: 'Usuarios',
    icon: <Users className="w-5 h-5" />,
    roles: ['admin_sistema'],
  },
  {
    path: '/roles',
    label: 'Roles',
    icon: <Shield className="w-5 h-5" />,
    roles: ['admin_sistema'],
  },
  {
    path: '/audit',
    label: 'Auditoría',
    icon: <ClipboardList className="w-5 h-5" />,
    roles: ['admin_sistema'],
  },
];

const roleLabels: Record<string, string> = {
  admin_sistema: 'Admin Sistema',
  admin_conocimiento: 'Admin Conocimiento',
  decisor: 'Decisor',
  analista: 'Analista',
};

export const Sidebar: React.FC = () => {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const visibleItems = navItems.filter(
    (item) => !item.roles || hasRole(item.roles)
  );

  const initials = user?.full_name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase();

  return (
    <div
      className={`flex flex-col h-full bg-gray-900 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-5 border-b border-gray-700/50">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Cpu className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-white font-bold text-sm tracking-wide">NEXUS</span>
              <span className="text-indigo-400 font-bold text-sm">CORP</span>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center mx-auto">
            <Cpu className="w-5 h-5 text-white" />
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-gray-400 hover:text-white p-1 rounded transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4" />
          ) : (
            <ChevronLeft className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Nav Items */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {visibleItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              } ${collapsed ? 'justify-center' : ''}`
            }
            title={collapsed ? item.label : undefined}
          >
            <span className="flex-shrink-0">{item.icon}</span>
            {!collapsed && <span className="truncate">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User Section */}
      <div className="border-t border-gray-700/50 p-3">
        {!collapsed ? (
          <div className="flex items-center gap-3 mb-2 px-2 py-2 rounded-lg bg-gray-800/50">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white text-xs font-medium truncate">
                {user?.full_name}
              </p>
              <p className="text-gray-400 text-xs truncate">
                {user?.role ? roleLabels[user.role] ?? user.role : ''}
              </p>
            </div>
          </div>
        ) : (
          <div className="flex justify-center mb-2">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-xs font-bold">
              {initials}
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className={`flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors ${
            collapsed ? 'justify-center' : ''
          }`}
          title={collapsed ? 'Cerrar Sesión' : undefined}
        >
          <LogOut className="w-4 h-4 flex-shrink-0" />
          {!collapsed && <span>Cerrar Sesión</span>}
        </button>
      </div>
    </div>
  );
};
