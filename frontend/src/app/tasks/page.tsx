'use client';

/**
 * Tasks Page - View and manage all tasks
 * Fully responsive - mobile optimized
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
        <div className="tasks-page-header">
          <div className="container" style={{ maxWidth: '100%' }}>
            <div className="tasks-header-content">
              <div className="tasks-header-text">
                <h1 className="tasks-title">My Tasks</h1>
                <p className="tasks-subtitle">
                  {stats.total} {stats.total === 1 ? 'task' : 'tasks'} • {stats.completed} completed
                </p>
              </div>
              <button
                onClick={() => router.push('/dashboard')}
                className="btn tasks-create-btn"
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
        <main className="container tasks-main" style={{ maxWidth: '1200px', margin: '0 auto', padding: 'var(--space-8) var(--space-4)' }}>
          {/* Stats Cards */}
          <div className="tasks-stats-grid">
            <div className="card tasks-stat-card">
              <div className="tasks-stat-number tasks-stat-total">{stats.total}</div>
              <div className="tasks-stat-label">Total Tasks</div>
            </div>
            <div className="card tasks-stat-card">
              <div className="tasks-stat-number tasks-stat-completed">{stats.completed}</div>
              <div className="tasks-stat-label">Completed</div>
            </div>
            <div className="card tasks-stat-card">
              <div className="tasks-stat-number tasks-stat-progress">{stats.inProgress}</div>
              <div className="tasks-stat-label">In Progress</div>
            </div>
            <div className="card tasks-stat-card">
              <div className="tasks-stat-number tasks-stat-pending">{stats.pending}</div>
              <div className="tasks-stat-label">Pending</div>
            </div>
          </div>

          {/* Filter Tabs */}
          <div className="tasks-filter-section">
            <h2 className="tasks-filter-title">All Tasks</h2>

            <div className="tasks-filter-buttons">
              {(['all', 'todo', 'in_progress', 'done'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`tasks-filter-btn ${filter === f ? 'tasks-filter-active' : ''}`}
                >
                  {f === 'all' ? 'All' : f.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Tasks List */}
          <div className="tasks-list">
            {filteredTasks.length === 0 ? (
              <div className="card tasks-empty-state">
                <svg
                  width={80}
                  height={80}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.5}
                  className="tasks-empty-icon"
                >
                  <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
                  <rect x="9" y="3" width="6" height="4" rx="1" />
                </svg>
                <h3 className="tasks-empty-title">No tasks found</h3>
                <p className="tasks-empty-text">
                  {filter === 'all' ? (
                    <>
                      No tasks yet.{' '}
                      <button
                        onClick={() => router.push('/dashboard')}
                        className="tasks-empty-link"
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
                    className="btn btn-secondary tasks-empty-btn"
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
                    className="card tasks-item-card"
                    style={{
                      animation: `slideUp 0.3s ease-out ${index * 0.05}s both`,
                    }}
                  >
                    <div className="tasks-item-content">
                      {/* Status Checkbox */}
                      <button
                        onClick={() =>
                          handleUpdateTask(task.id, {
                            status: task.status === 'done' ? 'todo' : 'done',
                          })
                        }
                        className="tasks-checkbox"
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
                      <div className="tasks-item-text">
                        <div className="tasks-item-header">
                          <h3
                            className="tasks-item-title"
                            style={{
                              textDecoration: task.status === 'done' ? 'line-through' : 'none',
                              color: task.status === 'done' ? 'var(--text-muted)' : 'var(--text-primary)',
                            }}
                          >
                            {task.title}
                          </h3>
                          <span
                            className="badge tasks-item-badge"
                            style={{
                              background: priorityColors.bg,
                              color: priorityColors.text,
                              border: `1px solid ${priorityColors.border}`,
                            }}
                          >
                            {task.priority}
                          </span>
                          <span
                            className="badge tasks-item-badge"
                            style={{
                              background: statusColors.bg,
                              color: statusColors.text,
                              border: `1px solid ${statusColors.border}`,
                            }}
                          >
                            {task.status.replace('_', ' ')}
                          </span>
                        </div>

                        {task.description && (
                          <p className="tasks-item-description">{task.description}</p>
                        )}

                        <div className="tasks-item-meta">
                          <span className="tasks-meta-item">
                            <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                              <line x1="16" y1="2" x2="16" y2="6" />
                              <line x1="8" y1="2" x2="8" y2="6" />
                              <line x1="3" y1="10" x2="21" y2="10" />
                            </svg>
                            Created {new Date(task.created_at).toLocaleDateString()}
                          </span>
                          {task.due_date && (
                            <span className="tasks-meta-item">
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
                      <div className="tasks-item-actions">
                        <select
                          value={task.status}
                          onChange={(e) => handleUpdateTask(task.id, { status: e.target.value as any })}
                          className="select tasks-status-select"
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="done">Done</option>
                        </select>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="btn btn-danger btn-sm tasks-delete-btn"
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

      {/* Inline base styles */}
      <style jsx>{`
        .tasks-page-header {
          background: linear-gradient(135deg, var(--coffee-latte) 0%, var(--accent-primary) 100%);
          padding: var(--space-8) var(--space-4);
        }

        .tasks-header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: var(--space-4);
        }

        .tasks-header-text h1 {
          color: white;
          margin-bottom: var(--space-2);
          font-size: var(--text-3xl);
        }

        .tasks-subtitle {
          color: rgba(255, 255, 255, 0.9);
          margin-bottom: 0;
          font-size: var(--text-base);
        }

        .tasks-create-btn {
          background: white;
          color: var(--accent-primary);
          padding: var(--space-4) var(--space-6);
          font-weight: 600;
          font-size: var(--text-base);
          min-height: 46px;
        }

        .tasks-stats-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: var(--space-6);
          margin-bottom: var(--space-10);
        }

        .tasks-stat-card {
          padding: var(--space-6);
          text-align: center;
        }

        .tasks-stat-number {
          font-size: var(--text-3xl);
          font-weight: 700;
        }

        .tasks-stat-total { color: var(--accent-primary); }
        .tasks-stat-completed { color: var(--success); }
        .tasks-stat-progress { color: var(--info); }
        .tasks-stat-pending { color: var(--warning); }

        .tasks-stat-label {
          font-size: var(--text-sm);
          color: var(--text-muted);
          margin-top: var(--space-1);
        }

        .tasks-filter-section {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: var(--space-8);
          flex-wrap: wrap;
          gap: var(--space-4);
        }

        .tasks-filter-title {
          font-size: var(--text-2xl);
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }

        .tasks-filter-buttons {
          display: flex;
          gap: var(--space-2);
          background: var(--bg-card);
          padding: var(--space-2);
          border-radius: var(--radius-xl);
          border: 1px solid var(--border-subtle);
        }

        .tasks-filter-btn {
          flex: 1 1 auto;
          padding: var(--space-3) var(--space-5);
          border-radius: var(--radius-lg);
          background: transparent;
          color: var(--text-secondary);
          font-weight: 500;
          font-size: var(--text-sm);
          transition: all var(--transition-fast);
          min-height: 42px;
          border: none;
          cursor: pointer;
        }

        .tasks-filter-active {
          background: var(--accent-light);
          color: var(--accent-primary);
          font-weight: 600;
        }

        .tasks-list {
          display: flex;
          flex-direction: column;
          gap: var(--space-4);
        }

        .tasks-item-card {
          padding: var(--space-6);
        }

        .tasks-item-content {
          display: flex;
          gap: var(--space-4);
          align-items: start;
        }

        .tasks-item-text {
          flex: 1;
          min-width: 0;
        }

        .tasks-item-header {
          display: flex;
          align-items: center;
          gap: var(--space-2);
          margin-bottom: var(--space-3);
          flex-wrap: wrap;
        }

        .tasks-item-title {
          font-size: var(--text-lg);
          font-weight: 600;
          margin: 0;
        }

        .tasks-item-badge {
          font-size: var(--text-xs);
          padding: var(--space-1) var(--space-3);
        }

        .tasks-item-description {
          font-size: var(--text-sm);
          color: var(--text-secondary);
          margin-bottom: var(--space-3);
          margin-top: 0;
          line-height: 1.6;
        }

        .tasks-item-meta {
          display: flex;
          align-items: center;
          gap: var(--space-6);
          font-size: var(--text-xs);
          color: var(--text-muted);
        }

        .tasks-meta-item {
          display: flex;
          align-items: center;
          gap: var(--space-1);
        }

        .tasks-item-actions {
          display: flex;
          gap: var(--space-2);
          align-items: center;
        }

        .tasks-status-select {
          padding: var(--space-2) var(--space-3);
          font-size: var(--text-sm);
          border-radius: var(--radius-md);
        }

        .tasks-delete-btn {
          padding: var(--space-2) var(--space-3);
          border-radius: var(--radius-md);
        }

        .tasks-empty-state {
          text-align: center;
          padding: var(--space-16);
          color: var(--text-muted);
        }

        .tasks-empty-icon {
          margin: 0 auto var(--space-6);
          opacity: 0.4;
        }

        .tasks-empty-title {
          font-size: var(--text-lg);
          margin-bottom: var(--space-2);
          color: var(--text-secondary);
        }

        .tasks-empty-text {
          margin: 0;
        }

        .tasks-empty-link {
          background: none;
          border: none;
          color: var(--accent-primary);
          font-weight: 600;
          cursor: pointer;
          text-decoration: underline;
        }

        .tasks-empty-btn {
          margin-top: var(--space-6);
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>

      {/* Mobile Responsive CSS */}
      <style jsx>{`
        @media (max-width: 767px) {
          .tasks-content {
            margin-left: 0 !important;
            width: 100% !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
          }
        }

        @media (max-width: 639px) {
          .tasks-content {
            margin-left: 0 !important;
            width: 100% !important;
          }

          .tasks-main {
            padding: var(--space-4) var(--space-3) !important;
            width: 100% !important;
          }

          .tasks-stats-grid {
            width: 100% !important;
          }

          .tasks-title {
            font-size: var(--text-2xl) !important;
          }

          .tasks-create-btn {
            padding: var(--space-3) var(--space-5) !important;
            font-size: var(--text-sm) !important;
          }

          .tasks-stats-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: var(--space-4) !important;
          }

          .tasks-stat-card {
            padding: var(--space-4) !important;
          }

          .tasks-filter-section {
            flex-direction: column !important;
            align-items: stretch !important;
            gap: var(--space-4) !important;
          }

          .tasks-filter-buttons {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
          }

          .tasks-filter-btn {
            flex: 0 0 auto !important;
            padding: var(--space-3) var(--space-4) !important;
            font-size: var(--text-xs) !important;
            white-space: nowrap !important;
          }

          .tasks-item-card {
            padding: var(--space-4) !important;
          }

          .tasks-item-content {
            flex-direction: column !important;
            gap: var(--space-3) !important;
          }

          .tasks-checkbox {
            width: 32px !important;
            height: 32px !important;
            align-self: flex-start !important;
          }

          .tasks-item-actions {
            width: 100% !important;
            justify-content: space-between !important;
            margin-top: var(--space-2) !important;
          }

          .tasks-status-select {
            flex: 1 !important;
            padding: var(--space-3) !important;
          }

          .tasks-delete-btn {
            min-width: 44px !important;
            min-height: 44px !important;
            padding: var(--space-3) !important;
          }

          .tasks-item-header {
            flex-wrap: wrap !important;
          }

          .tasks-item-title {
            font-size: var(--text-base) !important;
            width: 100% !important;
          }

          .tasks-item-badge {
            font-size: 10px !important;
            padding: 2px 6px !important;
          }

          .tasks-item-meta {
            flex-wrap: wrap !important;
            gap: var(--space-3) !important;
            font-size: 11px !important;
          }

          .tasks-empty-state {
            padding: var(--space-8) !important;
          }

          .tasks-empty-icon {
            width: 60px !important;
            height: 60px !important;
          }
        }

        @media (min-width: 640px) and (max-width: 767px) {
          .tasks-main {
            padding: var(--space-6) var(--space-4) !important;
          }

          .tasks-stats-grid {
            grid-template-columns: repeat(2, 1fr) !important;
          }
        }

        @media (min-width: 768px) and (max-width: 1023px) {
          .tasks-main {
            padding: var(--space-6) var(--space-5) !important;
          }

          .tasks-stats-grid {
            gap: var(--space-4) !important;
          }
        }
      `}</style>
    </>
  );
}
