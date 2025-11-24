import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API Types
export type StatusType = 'GREEN' | 'YELLOW' | 'RED';

export interface ProjectState {
  status: StatusType;
  blockers: string[];
  risks: string[];
  completed_today: string[];
  last_updated: string;
  team_id?: string;
}

export interface Event {
  id: string;
  source: 'slack' | 'jira' | 'github' | 'calendar';
  type: string;
  timestamp: string;
  data: Record<string, any>;
  team_id?: string;
}

export interface Action {
  id: string;
  type: 'notify' | 'create_task' | 'generate_report';
  status: string;
  timestamp: string;
  payload: Record<string, any>;
}

export interface AgentStatus {
  is_running: boolean;
  next_run?: string;
  run_count: number;
  last_run?: string;
}

export interface AnalyticsSummary {
  total_events: number;
  risk_score: number;
  velocity: number;
  completion_rate: number;
  avg_response_time: number;
  events_24h_change?: number;
  active_blockers?: number;
  team_health?: string;
}
