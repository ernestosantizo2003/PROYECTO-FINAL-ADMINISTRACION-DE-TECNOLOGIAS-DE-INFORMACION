export interface Role {
  id: string;
  name: 'admin_sistema' | 'admin_conocimiento' | 'decisor' | 'analista';
  description: string;
  permissions: string[];
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  role_id: string;
  role?: Role;
  created_at: string;
  updated_at: string;
}

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  role_id: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface KnowledgeRule {
  id: string;
  name: string;
  description: string;
  conditions: Record<string, { operator: string; value: string | number }>;
  action: string;
  priority: 1 | 2 | 3;
  category: string;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  stock_level: number;
  demand_level: 'bajo' | 'medio' | 'alto';
  risk_level: 'bajo' | 'medio' | 'alto';
  created_by: string;
  created_at: string;
}

export interface Recommendation {
  id: string;
  decision_id: string;
  rule_id: string;
  text: string;
  priority: number;
  justification: string;
  is_accepted: boolean;
}

export interface Decision {
  id: string;
  scenario_id: string;
  scenario?: Scenario;
  recommendations: Recommendation[];
  rules_fired: string[];
  status: 'pendiente' | 'aceptada' | 'rechazada';
  notes: string;
  created_by: string;
  created_at: string;
}

export interface Feedback {
  id: string;
  decision_id: string;
  user_id: string;
  rating: number;
  comment: string;
  created_at: string;
}

export interface KPI {
  id: string;
  name: string;
  value: number;
  unit: string;
  period: string;
  category: string;
  created_at: string;
}

export interface DashboardStats {
  total_rules: number;
  total_scenarios: number;
  total_decisions: number;
  accepted_recommendations: number;
  rejected_recommendations: number;
  avg_satisfaction: number;
  decisions_by_month: Array<{ month: string; count: number }>;
  rules_by_category: Array<{ category: string; count: number }>;
  feedback_distribution: Array<{ rating: number; count: number }>;
}

export interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  details: Record<string, unknown>;
  ip_address: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export interface WhatIfRequest {
  scenario_id?: string;
  name: string;
  description: string;
  stock_level: number;
  demand_level: 'bajo' | 'medio' | 'alto';
  risk_level: 'bajo' | 'medio' | 'alto';
}
