import api from './api';
import { User, PaginatedResponse } from '../types';

export interface CreateUserDto {
  email: string;
  username: string;
  full_name: string;
  password: string;
  role_id: string;
}

export interface UpdateUserDto {
  email?: string;
  full_name?: string;
  role_id?: string;
  password?: string;
}

export const usersService = {
  async getUsers(page = 1, size = 50): Promise<PaginatedResponse<User>> {
    const response = await api.get<PaginatedResponse<User>>('/users', {
      params: { page, size },
    });
    return response.data;
  },

  async getUser(id: string): Promise<User> {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },

  async createUser(data: CreateUserDto): Promise<User> {
    const response = await api.post<User>('/users', data);
    return response.data;
  },

  async updateUser(id: string, data: UpdateUserDto): Promise<User> {
    const response = await api.put<User>(`/users/${id}`, data);
    return response.data;
  },

  async deactivateUser(id: string): Promise<User> {
    const response = await api.patch<User>(`/users/${id}/deactivate`);
    return response.data;
  },

  async activateUser(id: string): Promise<User> {
    const response = await api.patch<User>(`/users/${id}/activate`);
    return response.data;
  },
};
