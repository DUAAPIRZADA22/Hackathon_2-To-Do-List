/**
 * API type definitions for ActionMind AI
 */

// ==================== User Types ====================
export interface UserData {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface UserSignupRequest {
  email: string;
  username: string;
  password: string;
}

export interface UserSigninRequest {
  email: string;
  password: string;
}

// ==================== Auth Types ====================
export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserData;
}

export interface AuthResponse {
  message: string;
}

// ==================== Task Types ====================
export type TaskStatus = 'todo' | 'in_progress' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  user_id: number;
  created_at: string;
  updated_at: string | null;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
}

// ==================== Error Types ====================
export interface ErrorResponse {
  detail: string;
  status_code?: number;
}

export class ApiError extends Error {
  public status: number;
  public detail: string;

  constructor(status: number, response: ErrorResponse) {
    super(response.detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = response.detail;
  }
}
