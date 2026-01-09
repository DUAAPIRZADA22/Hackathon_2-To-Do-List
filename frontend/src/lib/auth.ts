/**
 * Authentication state management for ActionMind AI.
 *
 * Handles JWT token storage, retrieval, and user state.
 */

import { signup, signin, signout as apiSignout } from '@/services/auth';
import type { UserSignupRequest, UserSigninRequest, UserData } from '@/types/api';

const TOKEN_KEY = 'access_token';
const USER_KEY = 'user_data';

/**
 * Get the stored JWT token
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store the JWT token
 */
export function setToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove the JWT token
 */
export function removeToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Get the stored user data
 */
export function getUserData(): UserData | null {
  if (typeof window === 'undefined') return null;
  const data = localStorage.getItem(USER_KEY);
  return data ? JSON.parse(data) : null;
}

/**
 * Store user data
 */
export function setUserData(user: UserData): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/**
 * Remove user data
 */
export function removeUserData(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(USER_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * Sign up a new user
 */
export async function signUp(data: UserSignupRequest): Promise<void> {
  const response = await signup(data);
  setToken(response.access_token);
  setUserData(response.user);
}

/**
 * Sign in an existing user
 */
export async function signIn(data: UserSigninRequest): Promise<void> {
  const response = await signin(data);
  setToken(response.access_token);
  setUserData(response.user);
}

/**
 * Sign out the current user
 *
 * Clears token and user data, then redirects to landing page.
 */
export async function signOut(): Promise<void> {
  await apiSignout();
  removeToken();
  removeUserData();

  // Redirect to landing page
  if (typeof window !== 'undefined') {
    window.location.href = '/';
  }
}

/**
 * Get the current authenticated user
 */
export function getCurrentUser(): UserData | null {
  return getUserData();
}
