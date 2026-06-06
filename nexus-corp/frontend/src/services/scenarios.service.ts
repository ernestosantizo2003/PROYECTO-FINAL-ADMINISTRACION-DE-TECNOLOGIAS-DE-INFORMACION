import api from './api';
import { Scenario, PaginatedResponse } from '../types';

export interface CreateScenarioDto {
  name: string;
  description: string;
  stock_level: number;
  demand_level: 'bajo' | 'medio' | 'alto';
  risk_level: 'bajo' | 'medio' | 'alto';
}

export const scenariosService = {
  async getScenarios(page = 1, size = 50): Promise<PaginatedResponse<Scenario>> {
    const response = await api.get<PaginatedResponse<Scenario>>('/scenarios', {
      params: { page, size },
    });
    return response.data;
  },

  async getScenario(id: string): Promise<Scenario> {
    const response = await api.get<Scenario>(`/scenarios/${id}`);
    return response.data;
  },

  async createScenario(data: CreateScenarioDto): Promise<Scenario> {
    const response = await api.post<Scenario>('/scenarios', data);
    return response.data;
  },

  async deleteScenario(id: string): Promise<void> {
    await api.delete(`/scenarios/${id}`);
  },
};
