'use client';

/**
 * Tasks Page - View and manage all tasks
 * Separate page from dashboard for better organization
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getCurrentUser, signOut } from '@/lib/auth';
import { getTasks, updateTask, deleteTask } from '@/services/task';
import { useToast } from '@/lib/toast';
import { Navigation, Sidebar } from '@/components';
import type { Task, TaskUpdateRequest } from '@/types/api';

export default function TasksPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [filter, setFilter] = useState<'all' | 'todo' | 'in_progress' | 'done'>('all');

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/signin');
      return;
    }
    const currentUser = getCurrentUser();
    setUser(currentUser);
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (error: any) {
      showToast('Failed to load tasks', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateTask = async (taskId: number, updates: Partial<Task>) => {
    try {
      // Convert Partial<Task> to TaskUpdateRequest by removing null values
      const updateRequest: TaskUpdateRequest = {};
      if (updates.title !== undefined) updateRequest.title = updates.title;
      if (updates.description !== undefined) updateRequest.description = updates.description || undefined;
      if (updates.status !== undefined) updateRequest.status = updates.status;
      if (updates.priority !== undefined) updateRequest.priority = updates.priority;
      if (updates.due_date !== undefined) updateRequest.due_date = updates.due_date || undefined;

      await updateTask(taskId, updateRequest);
      showToast('Task updated!', 'success');
      loadTasks();
    } catch (error: any) {
      showToast(error.detail || 'Failed to update task', 'error');
    }
  };

  const handleDeleteTask = async (taskId: number) => {
    try {
      await deleteTask(taskId);
      showToast('Task deleted', 'success');
      loadTasks();
    } catch (error: any) {
      showToast(error.detail || 'Failed to delete task', 'error');
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return { bg: 'var(--danger-light)', text: 'var(--danger)', border: 'var(--danger)' };
      case 'high':
        return { bg: 'var(--warning-light)', text: 'var(--warning)', border: 'var(--warning)' };
      case 'medium':
        return { bg: 'var(--accent-light)', text: 'var(--accent-primary)', border: 'var(--accent-primary)' };
      case 'low':
        return { bg: 'var(--info-light)', text: 'var(--info)', border: 'var(--info)' };
      default:
        return { bg: 'var(--info-light)', text: 'var(--info)', border: 'var(--info)' };
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'done':
        return { bg: 'var(--success-light)', text: 'var(--success)', border: 'var(--success)' };
      case 'in_progress':
        return { bg: 'var(--info-light)', text: 'var(--info)', border: 'var(--info)' };
      case 'todo':
        return { bg: 'var(--bg-secondary)', text: 'var(--text-muted)', border: 'var(--border-default)' };
      default:
        return { bg: 'var(--bg-secondary)', text: 'var(--text-muted)', border: 'var(--border-default)' };
    }
  };

  const getFilteredTasks = () => {
    if (filter === 'all') return tasks;
    return tasks.filter((task) => task.status === filter);
  };

  // Calculate stats
  const stats = {
    total: tasks.length,
    completed: tasks.filter((t) => t.status === 'done').length,
    inProgress: tasks.filter((t) => t.status === 'in_progress').length,
    pending: tasks.filter((t) => t.status === 'todo').length,
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div style={{ textAlign: 'center' }}>
          <span className="spinner" style={{ width: 48, height: 48, borderWidth: 3 }} />
          <p style={{ marginTop: 'var(--space-4)', color: 'var(--text-muted)' }}>Loading...</p>
        </div>
      </div>
    );
  }

  const filteredTasks = getFilteredTasks();

  return (
    <>
      <Navigation />
      <Sidebar />
      <div className="tasks-content" style={{ minHeight: '100vh', background: 'var(--bg-primary)', marginLeft: '260px' }}>
        {/* Page Header */}
        <div
          style={{
            background: 'linear-gradient(135deg, var(--coffee-latte) 0%, var(--accent-primary) 100%)',
            padding: 'var(--space-8) var(--space-4)',
          }}
        >
          <div className="container" style={{ maxWidth: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
              <div>
                <h1 style={{ color: 'white', marginBottom: 'var(--space-2)', fontSize: 'var(--text-3xl)' }}>My Tasks</h1>
                <p style={{ color: 'rgba(255,255,255,0.9)', marginBottom: 0, fontSize: 'var(--text-base)' }}>
                  {stats.total} {stats.total === 1 ? 'task' : 'tasks'} • {stats.completed} completed
                </p>
              </div>
              <button
                onClick={() => router.push('/dashboard')}
                className="btn"
                style={{
                  background: 'white',
                  color: 'var(--accent-primary)',
                  padding: 'var(--space-4) var(--space-6)',
                  fontWeight: 600,
                  fontSize: 'var(--text-base)',
                  minHeight: '46px',
                }}
              >
                <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path d="M12 5v14M5 12h14" />
                </svg>
                Create New Task
              </button>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <main className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: 'var(--space-8) var(--space-4)' }}>
          {/* Stats Cards */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(4, 1fr)',
              gap: 'var(--space-6)',
              marginBottom: 'var(--space-10)',
            }}
          >
            <div className="card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--text-3xl)', fontWeight: 700, color: 'var(--accent-primary)' }}>
                {stats.total}
              </div>
              <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-1)' }}>
                Total Tasks
              </div>
            </div>
            <div className="card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--text-3xl)', fontWeight: 700, color: 'var(--success)' }}>
                {stats.completed}
              </div>
              <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-1)' }}>
                Completed
              </div>
            </div>
            <div className="card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--text-3xl)', fontWeight: 700, color: 'var(--info)' }}>
                {stats.inProgress}
              </div>
              <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-1)' }}>
                In Progress
              </div>
            </div>
            <div className="card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
              <div style={{ fontSize: 'var(--text-3xl)', fontWeight: 700, color: 'var(--warning)' }}>
                {stats.pending}
              </div>
              <div style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)', marginTop: 'var(--space-1)' }}>
                Pending
              </div>
            </div>
          </div>

          {/* Filter Tabs */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 'var(--space-8)',
              flexWrap: 'wrap',
              gap: 'var(--space-4)',
            }}
          >
            <h2 style={{ fontSize: 'var(--text-2xl)', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
              All Tasks
            </h2>

            <div
              style={{
                display: 'flex',
                gap: 'var(--space-2)',
                background: 'var(--bg-card)',
                padding: 'var(--space-2)',
                borderRadius: 'var(--radius-xl)',
                border: '1px solid var(--border-subtle)',
                flexWrap: 'wrap',
              }}
            >
              {(['all', 'todo', 'in_progress', 'done'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className="btn-ghost"
                  style={{
                    flex: '1 1 auto',
                    padding: 'var(--space-3) var(--space-5)',
                    borderRadius: 'var(--radius-lg)',
                    background: filter === f ? 'var(--accent-light)' : 'transparent',
                    color: filter === f ? 'var(--accent-primary)' : 'var(--text-secondary)',
                    fontWeight: filter === f ? 600 : 500,
                    fontSize: 'var(--text-sm)',
                    transition: 'all var(--transition-fast)',
                    minHeight: '42px',
                  }}
                >
                  {f === 'all' ? 'All' : f.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Tasks List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            {filteredTasks.length === 0 ? (
              <div
                className="card"
                style={{
                  textAlign: 'center',
                  padding: 'var(--space-16)',
                  color: 'var(--text-muted)',
                }}
              >
                <svg
                  width={80}
                  height={80}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.5}
                  style={{ margin: '0 auto var(--space-6)', opacity: 0.4 }}
                >
                  <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
                  <rect x="9" y="3" width="6" height="4" rx="1" />
                </svg>
                <h3 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--space-2)', color: 'var(--text-secondary)' }}>
                  No tasks found
                </h3>
                <p style={{ margin: 0 }}>
                  {filter === 'all' ? (
                    <>
                      No tasks yet.{' '}
                      <button
                        onClick={() => router.push('/dashboard')}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: 'var(--accent-primary)',
                          fontWeight: 600,
                          cursor: 'pointer',
                          textDecoration: 'underline',
                        }}
                      >
                        Create your first task
                      </button>
                      !
                    </>
                  ) : (
                    'No tasks match this filter.'
                  )}
                </p>
                {filter !== 'all' && (
                  <button
                    onClick={() => setFilter('all')}
                    className="btn btn-secondary"
                    style={{ marginTop: 'var(--space-6)' }}
                  >
                    View All Tasks
                  </button>
                )}
              </div>
            ) : (
              filteredTasks.map((task, index) => {
                const priorityColors = getPriorityColor(task.priority);
                const statusColors = getStatusColor(task.status);

                return (
                  <div
                    key={task.id}
                    className="card"
                    style={{
                      padding: 'var(--space-6)',
                      animation: `slideUp 0.3s ease-out ${index * 0.05}s both`,
                    }}
                  >
                    <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'start' }}>
                      {/* Status Checkbox */}
                      <button
                        onClick={() =>
                          handleUpdateTask(task.id, {
                            status: task.status === 'done' ? 'todo' : 'done',
                          })
                        }
                        style={{
                          flexShrink: 0,
                          width: '28px',
                          height: '28px',
                          borderRadius: '50%',
                          border: '2.5px solid',
                          borderColor: task.status === 'done' ? 'var(--success)' : 'var(--border-default)',
                          background: task.status === 'done' ? 'var(--success)' : 'transparent',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transition: 'all var(--transition-fast)',
                        }}
                      >
                        {task.status === 'done' && (
                          <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth={3}>
                            <polyline points="20 6 9 17 4 12" />
                          </svg>
                        )}
                      </button>

                      {/* Content */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--space-2)',
                            marginBottom: 'var(--space-3)',
                            flexWrap: 'wrap',
                          }}
                        >
                          <h3
                            style={{
                              fontSize: 'var(--text-lg)',
                              fontWeight: 600,
                              margin: 0,
                              textDecoration: task.status === 'done' ? 'line-through' : 'none',
                              color: task.status === 'done' ? 'var(--text-muted)' : 'var(--text-primary)',
                            }}
                          >
                            {task.title}
                          </h3>
                          <span
                            className="badge"
                            style={{
                              background: priorityColors.bg,
                              color: priorityColors.text,
                              border: `1px solid ${priorityColors.border}`,
                              fontSize: 'var(--text-xs)',
                              padding: 'var(--space-1) var(--space-3)',
                            }}
                          >
                            {task.priority}
                          </span>
                          <span
                            className="badge"
                            style={{
                              background: statusColors.bg,
                              color: statusColors.text,
                              border: `1px solid ${statusColors.border}`,
                              fontSize: 'var(--text-xs)',
                              padding: 'var(--space-1) var(--space-3)',
                            }}
                          >
                            {task.status.replace('_', ' ')}
                          </span>
                        </div>

                        {task.description && (
                          <p
                            style={{
                              fontSize: 'var(--text-sm)',
                              color: 'var(--text-secondary)',
                              marginBottom: 'var(--space-3)',
                              marginTop: 0,
                              lineHeight: 1.6,
                            }}
                          >
                            {task.description}
                          </p>
                        )}

                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 'var(--space-6)',
                            fontSize: 'var(--text-xs)',
                            color: 'var(--text-muted)',
                          }}
                        >
                          <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                            <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                              <line x1="16" y1="2" x2="16" y2="6" />
                              <line x1="8" y1="2" x2="8" y2="6" />
                              <line x1="3" y1="10" x2="21" y2="10" />
                            </svg>
                            Created {new Date(task.created_at).toLocaleDateString()}
                          </span>
                          {task.due_date && (
                            <span style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-1)' }}>
                              <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                                <circle cx="12" cy="12" r="10" />
                                <polyline points="12 6 12 12 16 14" />
                              </svg>
                              Due {new Date(task.due_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
                        <select
                          value={task.status}
                          onChange={(e) => handleUpdateTask(task.id, { status: e.target.value as any })}
                          className="select"
                          style={{
                            padding: 'var(--space-2) var(--space-3)',
                            fontSize: 'var(--text-sm)',
                            borderRadius: 'var(--radius-md)',
                          }}
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="done">Done</option>
                        </select>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="btn btn-danger btn-sm"
                          style={{
                            padding: 'var(--space-2) var(--space-3)',
                            borderRadius: 'var(--radius-md)',
                          }}
                          title="Delete task"
                        >
                          <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                            <polyline points="3 6 5 6 21 6" />
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </main>
      </div>

      {/* Responsive CSS for mobile */}
      <style jsx>{`
        @media (max-width: 767px) {
          .tasks-content {
            marginLeft: 0 !important;
          }
        }
      `}</style>
    </>
  );
}
