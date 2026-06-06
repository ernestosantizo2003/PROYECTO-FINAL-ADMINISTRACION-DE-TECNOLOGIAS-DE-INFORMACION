import api from './api';
import { KnowledgeRule, PaginatedResponse } from '../types';

export interface CreateRuleDto {
  name: string;
  description: string;
  conditions: Record<string, { operator: string; value: string | number }>;
  action: string;
  priority: 1 | 2 | 3;
  category: string;
  is_active?: boolean;
}

export interface UpdateRuleDto extends Partial<CreateRuleDto> {}

export const rulesService = {
  async getRules(params?: {
    page?: number;
    size?: number;
    category?: string;
    is_active?: boolean;
  }): Promise<PaginatedResponse<KnowledgeRule>> {
    const response = await api.get<PaginatedResponse<KnowledgeRule>>('/rules', { params });
    return response.data;
  },

  async getRule(id: string): Promise<KnowledgeRule> {
    const response = await api.get<KnowledgeRule>(`/rules/${id}`);
    return response.data;
  },

  async createRule(data: CreateRuleDto): Promise<KnowledgeRule> {
    const response = await api.post<KnowledgeRule>('/rules', data);
    return response.data;
  },

  async updateRule(id: string, data: UpdateRuleDto): Promise<KnowledgeRule> {
    const response = await api.put<KnowledgeRule>(`/rules/${id}`, data);
    return response.data;
  },

  async deleteRule(id: string): Promise<void> {
    await api.delete(`/rules/${id}`);
  },

  async toggleRule(id: string, is_active: boolean): Promise<KnowledgeRule> {
    const response = await api.patch<KnowledgeRule>(`/rules/${id}/toggle`, { is_active });
    return response.data;
  },
};
