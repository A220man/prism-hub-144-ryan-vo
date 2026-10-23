// API Types
export interface Prompt {
  id: number;
  model_name: string;
  prompt_text: string;
  is_default: boolean;
  tags: string;
  created_at: string;
  updated_at: string;
}

export interface PromptCreate {
  model_name: string;
  prompt_text: string;
  is_default?: boolean;
  tags?: string;
}

export interface PromptUpdate {
  model_name?: string;
  prompt_text?: string;
  is_default?: boolean;
  tags?: string;
}

export interface PromptListResponse {
  items: Prompt[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  version: string;
  environment: string;
  database: string;
  demo_mode: boolean;
}