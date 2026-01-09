/**
 * Authentication service API calls
 */

import apiClient from '@/lib/api-client';
import type {
  UserSignupRequest,
  UserSigninRequest,
  TokenResponse,
  AuthResponse,
  UserData
} from '@/types/api';


/**
 * Sign up a new user
 */
export async function signup(data: UserSignupRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>('/auth/signup', data);
  return response.data;
}


/**
 * Sign in an existing user
 */
export async function signin(data: UserSigninRequest): Promise<TokenResponse> {
  // OAuth2PasswordRequestForm requires application/x-www-form-urlencoded
  const params = new URLSearchParams();
  params.append('username', data.email);
  params.append('password', data.password);

  const response = await apiClient.post<TokenResponse>(
    '/auth/signin',
    params,
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    }
  );
  return response.data;
}


/**
 * Sign out the current user
 */
export async function signout(): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/auth/signout');
  return response.data;
}


/**
 * Get the current user
 */
export async function getCurrentUser(): Promise<UserData> {
  const response = await apiClient.get<UserData>('/auth/me');
  return response.data;
}
