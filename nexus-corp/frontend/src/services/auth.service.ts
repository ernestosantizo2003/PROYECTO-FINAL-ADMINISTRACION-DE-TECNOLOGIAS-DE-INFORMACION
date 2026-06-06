import api from './api';
import { AuthUser, LoginResponse } from '../types';

export const authService = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login', { username, password });
    return response.data;
  },

  async getMe(): Promise<AuthUser> {
    const response = await api.get<AuthUser>('/auth/me');
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('nexus_token');
    localStorage.removeItem('nexus_user');
  },
};
