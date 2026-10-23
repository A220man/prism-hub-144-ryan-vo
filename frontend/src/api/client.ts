// API Client
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import type { Prompt, PromptCreate, PromptUpdate, PromptListResponse, HealthResponse } from './types';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Request interceptor for auth
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        if (this.accessToken && config.headers) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error: AxiosError) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.clearToken();
          // Could redirect to login here
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string | null) {
    this.accessToken = token;
  }

  clearToken() {
    this.accessToken = null;
  }

  // Health
  async getHealth(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  // Prompts
  async listPrompts(params?: {
    page?: number;
    page_size?: number;
    model_name?: string;
    search?: string;
    is_default?: boolean;
  }): Promise<PromptListResponse> {
    const response = await this.client.get<PromptListResponse>('/prompts', { params });
    return response.data;
  }

  async getPrompt(id: number): Promise<Prompt> {
    const response = await this.client.get<Prompt>(`/prompts/${id}`);
    return response.data;
  }

  async getDefaultPrompt(modelName: string): Promise<Prompt> {
    const response = await this.client.get<Prompt>(`/prompts/default/${encodeURIComponent(modelName)}`);
    return response.data;
  }

  async createPrompt(data: PromptCreate): Promise<Prompt> {
    const response = await this.client.post<Prompt>('/prompts', data);
    return response.data;
  }

  async updatePrompt(id: number, data: PromptUpdate): Promise<Prompt> {
    const response = await this.client.patch<Prompt>(`/prompts/${id}`, data);
    return response.data;
  }

  async deletePrompt(id: number): Promise<void> {
    await this.client.delete(`/prompts/${id}`);
  }

  async importPrompts(prompts: PromptCreate[]): Promise<Prompt[]> {
    const response = await this.client.post<Prompt[]>('/prompts/import', prompts);
    return response.data;
  }

  async exportPrompts(modelName?: string): Promise<Prompt[]> {
    const response = await this.client.get<Prompt[]>('/prompts/export/all', {
      params: { model_name: modelName },
    });
    return response.data;
  }
}

export const api = new ApiClient();