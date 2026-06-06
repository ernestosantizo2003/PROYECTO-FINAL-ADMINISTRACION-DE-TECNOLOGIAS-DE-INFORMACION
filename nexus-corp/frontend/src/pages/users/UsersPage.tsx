import React, { useEffect, useState, useCallback } from 'react';
import { UserPlus, Edit, UserX, UserCheck, Users } from 'lucide-react';
import { User, Role } from '../../types';
import { usersService, CreateUserDto, UpdateUserDto } from '../../services/users.service';
import { rolesService } from '../../services/roles.service';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Modal } from '../../components/ui/Modal';
import { Badge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Spinner';
import { useToast } from '../../hooks/useToast';
import { ToastContainer } from '../../components/ui/Toast';

interface UserFormData {
  full_name: string;
  username: string;
  email: string;
  password: string;
  role_id: string;
}

const emptyForm: UserFormData = {
  full_name: '',
  username: '',
  email: '',
  password: '',
  role_id: '',
};

const roleLabels: Record<string, string> = {
  admin_sistema: 'Admin Sistema',
  admin_conocimiento: 'Admin Conocimiento',
  decisor: 'Decisor',
  analista: 'Analista',
};

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>(emptyForm);
  const [formErrors, setFormErrors] = useState<Partial<UserFormData>>({});
  const [isSaving, setIsSaving] = useState(false);
  const { toasts, removeToast, success, error: toastError } = useToast();

  const loadData = useCallback(async () => {
    try {
      const [usersRes, rolesRes] = await Promise.all([
        usersService.getUsers(),
        rolesService.getRoles(),
      ]);
      setUsers(usersRes.items);
      setRoles(rolesRes);
    } catch {
      toastError('Error al cargar los datos');
    } finally {
      setIsLoading(false);
    }
  }, [toastError]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const openCreateModal = () => {
    setEditingUser(null);
    setFormData(emptyForm);
    setFormErrors({});
    setShowModal(true);
  };

  const openEditModal = (user: User) => {
    setEditingUser(user);
    setFormData({
      full_name: user.full_name,
      username: user.username,
      email: user.email,
      password: '',
      role_id: user.role_id,
    });
    setFormErrors({});
    setShowModal(true);
  };

  const validateForm = (): boolean => {
    const errors: Partial<UserFormData> = {};
    if (!formData.full_name.trim()) errors.full_name = 'El nombre es requerido';
    if (!formData.username.trim()) errors.username = 'El usuario es requerido';
    if (!formData.email.trim()) errors.email = 'El email es requerido';
    if (!editingUser && !formData.password.trim())
      errors.password = 'La contraseña es requerida';
    if (!formData.role_id) errors.role_id = 'El rol es requerido';
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setIsSaving(true);
    try {
      if (editingUser) {
        const updateData: UpdateUserDto = {
          full_name: formData.full_name,
          email: formData.email,
          role_id: formData.role_id,
        };
        if (formData.password) updateData.password = formData.password;
        await usersService.updateUser(editingUser.id, updateData);
        success('Usuario actualizado correctamente');
      } else {
        const createData: CreateUserDto = {
          full_name: formData.full_name,
          username: formData.username,
          email: formData.email,
          password: formData.password,
          role_id: formData.role_id,
        };
        await usersService.createUser(createData);
        success('Usuario creado correctamente');
      }
      setShowModal(false);
      loadData();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      toastError(axiosErr?.response?.data?.detail || 'Error al guardar el usuario');
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleActive = async (user: User) => {
    try {
      if (user.is_active) {
        await usersService.deactivateUser(user.id);
        success(`Usuario ${user.username} desactivado`);
      } else {
        await usersService.activateUser(user.id);
        success(`Usuario ${user.username} activado`);
      }
      loadData();
    } catch {
      toastError('Error al cambiar estado del usuario');
    }
  };

  const roleOptions = roles.map((r) => ({
    value: r.id,
    label: roleLabels[r.name] || r.name,
  }));

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Gestión de Usuarios</h2>
            <p className="text-sm text-gray-500 mt-1">
              Administra los usuarios del sistema
            </p>
          </div>
          <Button
            variant="primary"
            leftIcon={<UserPlus className="w-4 h-4" />}
            onClick={openCreateModal}
          >
            Nuevo Usuario
          </Button>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="flex justify-center py-16">
              <Spinner size="lg" />
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-16">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No hay usuarios registrados</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {['Nombre', 'Usuario', 'Email', 'Rol', 'Estado', 'Creado', 'Acciones'].map(
                      (h) => (
                        <th
                          key={h}
                          className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {users.map((user, idx) => (
                    <tr
                      key={user.id}
                      className={`hover:bg-gray-50 transition-colors ${idx % 2 === 1 ? 'bg-gray-50/50' : ''}`}
                    >
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {user.full_name}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 font-mono">
                        {user.username}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {user.email}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="indigo">
                          {user.role ? roleLabels[user.role.name] || user.role.name : '—'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={user.is_active ? 'success' : 'gray'}>
                          {user.is_active ? 'Activo' : 'Inactivo'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                        {new Date(user.created_at).toLocaleDateString('es-GT')}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            leftIcon={<Edit className="w-3.5 h-3.5" />}
                            onClick={() => openEditModal(user)}
                          >
                            Editar
                          </Button>
                          <Button
                            size="sm"
                            variant={user.is_active ? 'danger' : 'success'}
                            leftIcon={
                              user.is_active ? (
                                <UserX className="w-3.5 h-3.5" />
                              ) : (
                                <UserCheck className="w-3.5 h-3.5" />
                              )
                            }
                            onClick={() => handleToggleActive(user)}
                          >
                            {user.is_active ? 'Desactivar' : 'Activar'}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
        size="md"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              isLoading={isSaving}
              onClick={handleSubmit}
            >
              {editingUser ? 'Actualizar' : 'Crear Usuario'}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Nombre Completo"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            error={formErrors.full_name}
            required
            placeholder="Ej. Juan García"
          />
          <Input
            label="Nombre de Usuario"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
            error={formErrors.username}
            required
            disabled={!!editingUser}
            placeholder="Ej. jgarcia"
          />
          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            error={formErrors.email}
            required
            placeholder="Ej. jgarcia@empresa.com"
          />
          <Input
            label={editingUser ? 'Nueva Contraseña (dejar vacío para no cambiar)' : 'Contraseña'}
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            error={formErrors.password}
            required={!editingUser}
            placeholder="••••••••"
          />
          <Select
            label="Rol"
            value={formData.role_id}
            onChange={(e) => setFormData({ ...formData, role_id: e.target.value })}
            options={roleOptions}
            placeholder="Selecciona un rol"
            error={formErrors.role_id}
            required
          />
        </form>
      </Modal>
    </>
  );
};
