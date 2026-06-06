import React, { useEffect, useState, useCallback } from 'react';
import { ClipboardList, ChevronLeft, ChevronRight } from 'lucide-react';
import { AuditLog } from '../../types';
import api from '../../services/api';
import { Input } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Badge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Spinner';
import { Button } from '../../components/ui/Button';
import { useToast } from '../../hooks/useToast';
import { ToastContainer } from '../../components/ui/Toast';

const ACTION_COLORS: Record<string, 'success' | 'danger' | 'warning' | 'info' | 'indigo'> = {
  CREATE: 'success',
  UPDATE: 'warning',
  DELETE: 'danger',
  LOGIN: 'indigo',
  LOGOUT: 'info',
  READ: 'info',
};

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [filterEntityType, setFilterEntityType] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [searchUser, setSearchUser] = useState('');
  const { toasts, removeToast, error: toastError } = useToast();

  const pageSize = 20;

  const loadLogs = useCallback(async () => {
    setIsLoading(true);
    try {
      const params: Record<string, string | number> = {
        page,
        size: pageSize,
      };
      if (filterEntityType) params.entity_type = filterEntityType;
      if (filterAction) params.action = filterAction;
      if (searchUser) params.user_id = searchUser;

      const response = await api.get('/audit', { params });
      if (Array.isArray(response.data)) {
        setLogs(response.data);
        setTotal(response.data.length);
      } else {
        setLogs(response.data.items || []);
        setTotal(response.data.total || 0);
      }
    } catch {
      toastError('Error al cargar el registro de auditoría');
    } finally {
      setIsLoading(false);
    }
  }, [page, filterEntityType, filterAction, searchUser, toastError]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  const totalPages = Math.ceil(total / pageSize);

  const formatDetails = (details: Record<string, unknown>) => {
    try {
      const str = JSON.stringify(details);
      return str.length > 60 ? str.slice(0, 60) + '...' : str;
    } catch {
      return '—';
    }
  };

  const entityTypeOptions = [
    { value: '', label: 'Todos los tipos' },
    { value: 'user', label: 'Usuario' },
    { value: 'rule', label: 'Regla' },
    { value: 'decision', label: 'Decisión' },
    { value: 'scenario', label: 'Escenario' },
    { value: 'feedback', label: 'Feedback' },
  ];

  const actionOptions = [
    { value: '', label: 'Todas las acciones' },
    { value: 'CREATE', label: 'Crear' },
    { value: 'UPDATE', label: 'Actualizar' },
    { value: 'DELETE', label: 'Eliminar' },
    { value: 'LOGIN', label: 'Login' },
    { value: 'LOGOUT', label: 'Logout' },
    { value: 'READ', label: 'Consultar' },
  ];

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Registro de Auditoría</h2>
          <p className="text-sm text-gray-500 mt-1">
            Historial de todas las acciones realizadas en el sistema
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg border border-gray-200 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Select
            label="Tipo de Entidad"
            value={filterEntityType}
            onChange={(e) => { setFilterEntityType(e.target.value); setPage(1); }}
            options={entityTypeOptions}
          />
          <Select
            label="Acción"
            value={filterAction}
            onChange={(e) => { setFilterAction(e.target.value); setPage(1); }}
            options={actionOptions}
          />
          <Input
            label="Buscar por Usuario ID"
            value={searchUser}
            onChange={(e) => { setSearchUser(e.target.value); setPage(1); }}
            placeholder="ID del usuario..."
          />
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="flex justify-center py-16">
              <Spinner size="lg" />
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-16">
              <ClipboardList className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No hay registros de auditoría</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      {['Fecha', 'Usuario', 'Acción', 'Tipo Entidad', 'Entidad ID', 'Detalles', 'IP'].map(
                        (h) => (
                          <th
                            key={h}
                            className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider whitespace-nowrap"
                          >
                            {h}
                          </th>
                        )
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {logs.map((log, idx) => (
                      <tr
                        key={log.id}
                        className={`hover:bg-gray-50 transition-colors ${idx % 2 === 1 ? 'bg-gray-50/50' : ''}`}
                      >
                        <td className="px-4 py-3 text-xs text-gray-600 whitespace-nowrap">
                          {new Date(log.created_at).toLocaleString('es-GT', {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </td>
                        <td className="px-4 py-3 text-xs font-mono text-gray-600 max-w-[100px] truncate">
                          {log.user_id}
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={ACTION_COLORS[log.action] || 'default'} size="sm">
                            {log.action}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600 capitalize">
                          {log.entity_type}
                        </td>
                        <td className="px-4 py-3 text-xs font-mono text-gray-500 max-w-[80px] truncate">
                          {log.entity_id}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-500 max-w-[180px] truncate font-mono">
                          {formatDetails(log.details)}
                        </td>
                        <td className="px-4 py-3 text-xs text-gray-500 whitespace-nowrap">
                          {log.ip_address || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
                  <p className="text-sm text-gray-500">
                    Mostrando {(page - 1) * pageSize + 1} -{' '}
                    {Math.min(page * pageSize, total)} de {total} registros
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      leftIcon={<ChevronLeft className="w-4 h-4" />}
                      disabled={page === 1}
                      onClick={() => setPage((p) => p - 1)}
                    >
                      Anterior
                    </Button>
                    <span className="text-sm text-gray-600">
                      Página {page} de {totalPages}
                    </span>
                    <Button
                      size="sm"
                      variant="secondary"
                      rightIcon={<ChevronRight className="w-4 h-4" />}
                      disabled={page === totalPages}
                      onClick={() => setPage((p) => p + 1)}
                    >
                      Siguiente
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </>
  );
};
