/**
 * Type definitions for ActionMind AI
 */

export interface User {
  id: number;
  email: string;
  name?: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  status: 'todo' | 'in_progress' | 'done';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
  // Phase V fields
  recurrence_rule?: RecurrenceRule;
  reminder_settings?: ReminderSettings;
}

export interface RecurrenceRule {
  frequency: 'daily' | 'weekly' | 'monthly';
  interval?: number;
  days?: string[];
  month_day?: number;
  end_date?: string;
  count?: number;
}

export interface ReminderSettings {
  reminder_times: string[]; // e.g., ["1h", "1d", "1w"]
  notification_method: 'email' | 'push';
  enabled: boolean;
}

export interface TaskCreateInput {
  title: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'done';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
  recurrence_rule?: RecurrenceRule;
  reminder_settings?: ReminderSettings;
}

export interface TaskUpdateInput {
  title?: string;
  description?: string;
  completed?: boolean;
  status?: 'todo' | 'in_progress' | 'done';
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  due_date?: string;
  recurrence_rule?: RecurrenceRule;
  reminder_settings?: ReminderSettings;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  tool_calls?: string;
}

export interface Conversation {
  id: string;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ChatResponse {
  message: string;
  tasks?: Task[];
}

export interface ErrorResponse {
  detail: string;
  status_code?: number;
}
