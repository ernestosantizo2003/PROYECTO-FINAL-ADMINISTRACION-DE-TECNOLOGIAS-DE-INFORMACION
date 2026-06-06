import api from './api';
import { KPI, DashboardStats, PaginatedResponse } from '../types';

export const kpisService = {
  async getKPIs(params?: { page?: number; size?: number; category?: string }): Promise<PaginatedResponse<KPI>> {
    const response = await api.get<PaginatedResponse<KPI>>('/kpis', { params });
    return response.data;
  },

  async getDashboard(): Promise<DashboardStats> {
    const response = await api.get<DashboardStats>('/kpis/dashboard');
    return response.data;
  },

  async getKPI(id: string): Promise<KPI> {
    const response = await api.get<KPI>(`/kpis/${id}`);
    return response.data;
  },
};
