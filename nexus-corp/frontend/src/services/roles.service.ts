import api from './api';
import { Role } from '../types';

export const rolesService = {
  async getRoles(): Promise<Role[]> {
    const response = await api.get<Role[]>('/roles');
    return response.data;
  },

  async getRole(id: string): Promise<Role> {
    const response = await api.get<Role>(`/roles/${id}`);
    return response.data;
  },
};
