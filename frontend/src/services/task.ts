/**
 * Task service API calls
 */

import apiClient from '@/lib/api-client';
import type {
  Task,
  TaskCreateRequest,
  TaskUpdateRequest,
} from '@/types/api';


/**
 * Get all tasks for the current user
 */
export async function getTasks(skip = 0, limit = 100): Promise<Task[]> {
  const response = await apiClient.get<Task[]>('/tasks', {
    params: { skip, limit },
  });
  return response.data;
}


/**
 * Get a specific task by ID
 */
export async function getTask(taskId: number): Promise<Task> {
  const response = await apiClient.get<Task>(`/tasks/${taskId}`);
  return response.data;
}


/**
 * Create a new task
 */
export async function createTask(data: TaskCreateRequest): Promise<Task> {
  const response = await apiClient.post<Task>('/tasks', data);
  return response.data;
}


/**
 * Update an existing task
 */
export async function updateTask(taskId: number, data: TaskUpdateRequest): Promise<Task> {
  const response = await apiClient.put<Task>(`/tasks/${taskId}`, data);
  return response.data;
}


/**
 * Delete a task
 */
export async function deleteTask(taskId: number): Promise<void> {
  await apiClient.delete(`/tasks/${taskId}`);
}
