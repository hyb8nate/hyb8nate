import axios, { AxiosError } from 'axios';
import type {
  LoginRequest,
  Token,
  DeploymentInfo,
  Schedule,
  ScheduleCreate,
  ScheduleUpdate,
  ApiError,
} from '../types';

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API - Simple admin password authentication
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<Token> => {
    const response = await api.post<Token>('/auth/login', credentials);
    return response.data;
  },
};

// Schedules API
export const schedulesAPI = {
  getAll: async (): Promise<Schedule[]> => {
    const response = await api.get<Schedule[]>('/schedules');
    return response.data;
  },

  getById: async (id: number): Promise<Schedule> => {
    const response = await api.get<Schedule>(`/schedules/${id}`);
    return response.data;
  },

  create: async (schedule: ScheduleCreate): Promise<Schedule> => {
    const response = await api.post<Schedule>('/schedules', schedule);
    return response.data;
  },

  update: async (id: number, schedule: ScheduleUpdate): Promise<Schedule> => {
    const response = await api.patch<Schedule>(`/schedules/${id}`, schedule);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/schedules/${id}`);
  },
};

// K8s API (Simplified - single cluster)
export const k8sAPI = {
  getNamespaces: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/namespaces');
    return response.data;
  },

  getDeployments: async (namespace: string): Promise<DeploymentInfo[]> => {
    const response = await api.get<DeploymentInfo[]>(
      `/namespaces/${namespace}/deployments`
    );
    return response.data;
  },
};

export default api;
