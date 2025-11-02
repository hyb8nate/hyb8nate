export interface LoginRequest {
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface DeploymentInfo {
  name: string;
  namespace: string;
  replicas: number;
  available_replicas: number;
}

export interface Schedule {
  id: number;
  namespace: string;
  deployment_name: string;
  scale_down_time: string;
  scale_up_time: string;
  original_replicas: number;
  enabled: boolean;
  is_scaled_down: boolean;
  last_scaled_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ScheduleCreate {
  namespace: string;
  deployment_name: string;
  scale_down_time: string;
  scale_up_time: string;
}

export interface ScheduleUpdate {
  scale_down_time?: string;
  scale_up_time?: string;
  enabled?: boolean;
}

export interface ApiError {
  detail: string;
}
