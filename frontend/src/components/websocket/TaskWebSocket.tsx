/**
 * TaskWebSocket Component - Manages real-time task updates (T064)
 *
 * This component:
 * - Establishes WebSocket connection on mount
 * - Listens for task events and updates local state
 * - Shows notifications for task assignments (T068)
 * - Handles automatic reconnection
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { getWebSocketClient, TaskEventMessage } from '@/lib/websocket';
import { Task } from '@/types';

interface TaskWebSocketProps {
  onTasksUpdate?: (tasks: Task[]) => void;
  onTaskCreated?: (task: Task) => void;
  onTaskUpdated?: (task: Task) => void;
  onTaskDeleted?: (taskId: string) => void;
  onTaskCompleted?: (task: Task) => void;
  children?: React.ReactNode;
}

export function TaskWebSocket({
  onTasksUpdate,
  onTaskCreated,
  onTaskUpdated,
  onTaskDeleted,
  onTaskCompleted,
  children
}: TaskWebSocketProps) {
  const { toast } = useToast();
  const [isConnected, setIsConnected] = useState(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    const wsClient = getWebSocketClient();

    // Register event callback (T065)
    const unregister = wsClient.onTaskEvent((event: TaskEventMessage) => {
      if (!mountedRef.current) return;

      console.log('[TaskWebSocket] Received event:', event);

      switch (event.type) {
        case 'task_update':
          handleTaskUpdate(event);
          break;

        case 'reminder':
          handleReminder(event);
          break;

        case 'system_message':
          handleSystemMessage(event);
          break;

        default:
          console.log('[TaskWebSocket] Unknown event type:', event.type);
      }
    });

    // Connect to WebSocket
    wsClient.connect();
    setIsConnected(true);

    // Cleanup on unmount
    return () => {
      mountedRef.current = false;
      unregister();
      wsClient.disconnect();
      setIsConnected(false);
    };
  }, []);

  /**
   * Handle task update events
   */
  const handleTaskUpdate = (event: TaskEventMessage) => {
    const eventType = event.event_type;

    switch (eventType) {
      case 'task_created':
        if (event.data && onTaskCreated) {
          onTaskCreated(event.data as Task);
        }
        showNotification('Task Created', `New task: ${event.data?.title}`, 'info');
        break;

      case 'task_updated':
        if (event.data && onTaskUpdated) {
          onTaskUpdated(event.data as Task);
        }
        break;

      case 'task_deleted':
        if (event.task_id && onTaskDeleted) {
          onTaskDeleted(event.task_id);
        }
        showNotification('Task Deleted', 'A task has been deleted', 'info');
        break;

      case 'task_assigned':
        // Show visual notification for task assignment (T068)
        showNotification(
          'Task Assigned',
          `You've been assigned: ${event.data?.title}`,
          'info'
        );
        if (event.data && onTaskUpdated) {
          onTaskUpdated(event.data as Task);
        }
        break;

      case 'task_completed':
        if (event.data && onTaskCompleted) {
          onTaskCompleted(event.data as Task);
        }
        showNotification('Task Completed', `Great job! "${event.data?.title}" is done!`, 'success');
        break;

      case 'task_uncompleted':
        if (event.data && onTaskUpdated) {
          onTaskUpdated(event.data as Task);
        }
        break;
    }
  };

  /**
   * Handle reminder events
   */
  const handleReminder = (event: TaskEventMessage) => {
    showNotification(
      'Task Due Soon',
      event.data?.message || 'One of your tasks is due soon',
      'warning'
    );
  };

  /**
   * Handle system messages
   */
  const handleSystemMessage = (event: TaskEventMessage) => {
    if (event.level === 'error') {
      showNotification('System Message', event.message || 'An error occurred', 'error');
    } else if (event.level === 'warning') {
      showNotification('System Message', event.message || 'Warning', 'warning');
    } else {
      showNotification('System Message', event.message || 'Information', 'info');
    }
  };

  /**
   * Show toast notification
   */
  const showNotification = (title: string, message: string, variant: 'info' | 'success' | 'warning' | 'error') => {
    toast({
      title,
      description: message,
      variant,
    });
  };

  // Connection status indicator
  return (
    <>
      {children}
      {/* Optional: Show connection status */}
      {/* <div className={`fixed bottom-4 right-4 px-3 py-1 rounded-full text-xs font-medium ${isConnected ? 'bg-green-500' : 'bg-red-500'} text-white`}>
        {isConnected ? '● Connected' : '● Disconnected'}
      </div> */}
    </>
  );
}

export default TaskWebSocket;
