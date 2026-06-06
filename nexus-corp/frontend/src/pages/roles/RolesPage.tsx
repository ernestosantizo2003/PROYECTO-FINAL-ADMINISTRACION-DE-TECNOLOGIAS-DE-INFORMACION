import React, { useEffect, useState } from 'react';
import { Shield } from 'lucide-react';
import { Role } from '../../types';
import { rolesService } from '../../services/roles.service';
import { Badge } from '../../components/ui/Badge';
import { Card } from '../../components/ui/Card';
import { Spinner } from '../../components/ui/Spinner';

const roleLabels: Record<string, string> = {
  admin_sistema: 'Administrador del Sistema',
  admin_conocimiento: 'Administrador de Conocimiento',
  decisor: 'Decisor',
  analista: 'Analista',
};

const roleColors: Record<string, string> = {
  admin_sistema: 'bg-red-50 border-red-200',
  admin_conocimiento: 'bg-purple-50 border-purple-200',
  decisor: 'bg-blue-50 border-blue-200',
  analista: 'bg-green-50 border-green-200',
};

const roleIconColors: Record<string, string> = {
  admin_sistema: 'bg-red-100 text-red-600',
  admin_conocimiento: 'bg-purple-100 text-purple-600',
  decisor: 'bg-blue-100 text-blue-600',
  analista: 'bg-green-100 text-green-600',
};

export const RolesPage: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    rolesService
      .getRoles()
      .then((data) => setRoles(data))
      .catch(() => setError('Error al cargar los roles'))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Roles y Permisos</h2>
        <p className="text-sm text-gray-500 mt-1">
          Los roles del sistema son predefinidos y no se pueden modificar
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {roles.map((role) => (
          <div
            key={role.id}
            className={`rounded-lg border-2 p-6 ${roleColors[role.name] || 'bg-gray-50 border-gray-200'}`}
          >
            <div className="flex items-start gap-4">
              <div
                className={`p-3 rounded-xl ${roleIconColors[role.name] || 'bg-gray-100 text-gray-600'}`}
              >
                <Shield className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 text-base">
                  {roleLabels[role.name] || role.name}
                </h3>
                <p className="text-xs font-mono text-gray-500 mt-0.5">{role.name}</p>
                <p className="text-sm text-gray-600 mt-2">{role.description}</p>
              </div>
            </div>

            {role.permissions && role.permissions.length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                  Permisos ({role.permissions.length})
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {role.permissions.map((perm) => (
                    <Badge key={perm} variant="info" size="sm">
                      {perm}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {roles.length === 0 && (
          <Card className="col-span-2">
            <div className="text-center py-8">
              <Shield className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No se encontraron roles en el sistema</p>
            </div>
          </Card>
        )}
      </div>

      <Card>
        <div className="flex items-start gap-4">
          <div className="p-2 bg-indigo-50 rounded-lg">
            <Shield className="w-5 h-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-medium text-gray-900">Acerca de los Roles</h3>
            <div className="mt-2 text-sm text-gray-600 space-y-1">
              <p>
                <strong>Admin Sistema:</strong> Acceso completo a todas las funcionalidades, gestión de usuarios y auditoría.
              </p>
              <p>
                <strong>Admin Conocimiento:</strong> Gestión de reglas de conocimiento y base de conocimiento.
              </p>
              <p>
                <strong>Decisor:</strong> Acceso al análisis What-If, visualización de reglas y gestión de decisiones.
              </p>
              <p>
                <strong>Analista:</strong> Acceso a KPIs, estadísticas y métricas del sistema.
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
