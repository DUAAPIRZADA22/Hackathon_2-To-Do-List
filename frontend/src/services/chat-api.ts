/**
 * Chat API service for Todo AI Chatbot (Phase III)
 *
 * Provides chat and chat-stream API calls with authentication.
 * Supports both regular HTTP and Server-Sent Events (SSE) streaming.
 */

import apiClient, { getToken } from '@/lib/api-client';

// =====================================================
// Types
// =====================================================

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, unknown>;
  result?: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
}

export interface SSEChunk {
  type: 'token' | 'done' | 'error';
  content?: string;
  conversation_id?: string;
  tool_calls?: ToolCall[];
}

// =====================================================
// Chat API (Non-Streaming)
// =====================================================

/**
 * Send a chat message to the AI assistant
 *
 * @param userId - User ID
 * @param request - Chat request with message and optional conversation_id
 * @returns Chat response with conversation_id, response text, and tool_calls
 */
export async function sendChatMessage(
  userId: string,
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await apiClient.post<ChatResponse>(
    `/api/${userId}/chat`,
    request
  );
  return response.data;
}

// =====================================================
// Chat API (SSE Streaming)
// =====================================================

/**
 * Send a chat message and stream the response via Server-Sent Events
 *
 * @param userId - User ID
 * @param request - Chat request with message and optional conversation_id
 * @param onChunk - Callback function for each SSE chunk
 * @param onDone - Callback function when stream completes
 * @param onError - Callback function for errors
 * @returns EventSource for the SSE stream (call .close() to cancel)
 */
export function streamChatMessage(
  userId: string,
  request: ChatRequest,
  onChunk: (chunk: SSEChunk) => void,
  onDone?: (response: ChatResponse) => void,
  onError?: (error: Error) => void
): EventSource {
  // Build URL with query parameters
  // Note: baseURL already includes /api, so we don't add it again
  const url = new URL(`${apiClient.defaults.baseURL}/${userId}/chat/stream`);

  // Add request body as query params (GET request for SSE)
  if (request.conversation_id) {
    url.searchParams.append('conversation_id', request.conversation_id);
  }
  url.searchParams.append('message', request.message);

  // Add token as query parameter (EventSource doesn't support custom headers)
  const token = getToken();
  if (token) {
    url.searchParams.append('token', token);
  }

  // Create EventSource
  const eventSource = new EventSource(url.toString());

  let fullResponse = '';
  let finalConversationId = '';
  let finalToolCalls: ToolCall[] = [];

  eventSource.onmessage = (event) => {
    try {
      const chunk: SSEChunk = JSON.parse(event.data);

      if (chunk.type === 'token') {
        // Accumulate response tokens
        fullResponse += chunk.content || '';
        onChunk(chunk);
      } else if (chunk.type === 'done') {
        // Stream complete
        finalConversationId = chunk.conversation_id || '';
        finalToolCalls = chunk.tool_calls || [];

        if (onDone) {
          onDone({
            conversation_id: finalConversationId,
            response: fullResponse,
            tool_calls: finalToolCalls
          });
        }

        eventSource.close();
      } else if (chunk.type === 'error') {
        // Error occurred
        if (onError) {
          onError(new Error(chunk.content || 'Unknown error'));
        }
        eventSource.close();
      }
    } catch (error) {
      console.error('Failed to parse SSE chunk:', error);
      if (onError) {
        onError(error as Error);
      }
      eventSource.close();
    }
  };

  eventSource.onerror = (error) => {
    console.error('EventSource error:', error);
    if (onError) {
      onError(new Error('Connection error'));
    }
    eventSource.close();
  };

  return eventSource;
}

// =====================================================
// Helper Functions
// =====================================================

/**
 * Get the current user ID from authentication
 * For Phase III, this extracts from JWT token
 *
 * @returns User ID or null if not authenticated
 */
export function getCurrentUserId(): string | null {
  // For Better Auth integration, extract user_id from JWT
  // This will be implemented when Better Auth is integrated
  const token = getToken();
  if (!token) return null;

  try {
    // Decode JWT payload (simple base64 decode)
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub || payload.userId || payload.user_id || null;
  } catch {
    return null;
  }
}

/**
 * Check if user is authenticated
 *
 * @returns True if user has valid token
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}
