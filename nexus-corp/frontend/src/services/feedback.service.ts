import api from './api';
import { Feedback, PaginatedResponse } from '../types';

export interface CreateFeedbackDto {
  decision_id: string;
  rating: number;
  comment: string;
}

export interface FeedbackStats {
  total: number;
  average_rating: number;
  distribution: Array<{ rating: number; count: number }>;
}

export const feedbackService = {
  async getFeedback(page = 1, size = 50): Promise<PaginatedResponse<Feedback>> {
    const response = await api.get<PaginatedResponse<Feedback>>('/feedback', {
      params: { page, size },
    });
    return response.data;
  },

  async createFeedback(data: CreateFeedbackDto): Promise<Feedback> {
    const response = await api.post<Feedback>('/feedback', data);
    return response.data;
  },

  async getFeedbackStats(): Promise<FeedbackStats> {
    const response = await api.get<FeedbackStats>('/feedback/stats');
    return response.data;
  },

  async getFeedbackByDecision(decisionId: string): Promise<Feedback[]> {
    const response = await api.get<Feedback[]>(`/feedback/decision/${decisionId}`);
    return response.data;
  },
};
