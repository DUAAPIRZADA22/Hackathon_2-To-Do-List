/**
 * API client base configuration for ActionMind AI.
 *
 * This module configures the axios instance with base URL,
 * authorization header interceptor, and error handling.
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { ErrorResponse, ApiError } from '@/types/api';

// Get API URL from environment variable or use default
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = process.env.NEXT_PUBLIC_API_PREFIX || '/api';

/**
 * Get the stored JWT token from localStorage
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * Store the JWT token in localStorage
 */
export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('access_token', token);
}

/**
 * Remove the JWT token from localStorage
 */
export function removeToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
}

/**
 * Create and configure the axios instance
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}${API_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
  // Note: withCredentials removed to avoid CORS issues with error responses
});

/**
 * Request interceptor to add Authorization header
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle 401 errors and format API errors
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ErrorResponse>) => {
    // Handle 401 Unauthorized - remove token
    if (error.response?.status === 401) {
      removeToken();
    }

    // Convert to ApiError for consistent error handling
    if (error.response?.data) {
      const apiError = new ApiError(
        error.response.status,
        error.response.data
      );
      return Promise.reject(apiError);
    }

    // Network error or no response data
    return Promise.reject(error);
  }
);

export default apiClient;
