import api from './api';
import { Decision, PaginatedResponse, WhatIfRequest } from '../types';

export const decisionsService = {
  async getDecisions(params?: {
    page?: number;
    size?: number;
    status?: string;
  }): Promise<PaginatedResponse<Decision>> {
    const response = await api.get<PaginatedResponse<Decision>>('/decisions', { params });
    return response.data;
  },

  async getDecision(id: string): Promise<Decision> {
    const response = await api.get<Decision>(`/decisions/${id}`);
    return response.data;
  },

  async analyzeWhatIf(data: WhatIfRequest): Promise<Decision> {
    const response = await api.post<Decision>('/decisions/analyze', data);
    return response.data;
  },

  async updateDecisionStatus(
    id: string,
    status: 'pendiente' | 'aceptada' | 'rechazada',
    notes?: string
  ): Promise<Decision> {
    const response = await api.patch<Decision>(`/decisions/${id}/status`, { status, notes });
    return response.data;
  },

  async saveDecision(data: WhatIfRequest): Promise<Decision> {
    const response = await api.post<Decision>('/decisions', data);
    return response.data;
  },
};
