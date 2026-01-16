'use client';

/**
 * Dashboard Page - Create Task + Analytics
 * Task list moved to separate /tasks page
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getCurrentUser } from '@/lib/auth';
import { createTask } from '@/services/task';
import { useToast } from '@/lib/toast';
import { Navigation, Sidebar } from '@/components';
import type { TaskCreateRequest } from '@/types/api';

export default function DashboardPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [isCreating, setIsCreating] = useState(false);
  const [user, setUser] = useState<{ username: string } | null>(null);

  const [newTask, setNewTask] = useState<TaskCreateRequest>({
    title: '',
    description: '',
    status: 'todo',
    priority: 'medium',
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/signin');
      return;
    }
    const currentUser = getCurrentUser();
    setUser(currentUser);
  }, []);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;

    setIsCreating(true);
    try {
      await createTask(newTask);
      showToast('Task created successfully!', 'success');
      setNewTask({ title: '', description: '', status: 'todo', priority: 'medium' });
      // Redirect to tasks page after creating
      router.push('/tasks');
    } catch (error: any) {
      showToast(error.detail || 'Failed to create task', 'error');
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <>
      <Navigation />
      <Sidebar />
      <div className="dashboard-content" style={{ minHeight: '100vh', background: 'var(--bg-primary)', marginLeft: '260px' }}>
        {/* Dashboard Header */}
        <div
          style={{
            background:
              'linear-gradient(135deg, var(--coffee-latte) 0%, var(--accent-primary) 100%)',
            padding: 'var(--space-10) var(--space-4)',
            textAlign: 'center',
            color: 'white',
          }}
        >
          <div className="container" style={{ maxWidth: '100%' }}>
            <h1 style={{ color: 'white', marginBottom: 'var(--space-2)', fontSize: 'var(--text-3xl)' }}>
              Welcome back, {user?.username}!
            </h1>
            <p style={{ color: 'rgba(255,255,255,0.9)', marginBottom: 0, fontSize: 'var(--text-base)' }}>
              Ready to be productive today?
            </p>
          </div>
        </div>

        {/* Main Content */}
        <main className="dashboard-main" style={{ padding: 'var(--space-8) var(--space-4)' }}>
          <div className="container dashboard-grid" style={{ maxWidth: '1200px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'minmax(0, 1.2fr) minmax(280px, 350px)', gap: 'var(--space-8)', alignItems: 'start' }}>
            {/* Left: Create Task Form */}
            <div style={{ minWidth: 0 }}>
              {/* Create Task Section */}
              <section>
                <div
                  className="card card-elevated"
                  style={{
                    padding: 'var(--space-8)',
                    background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--bg-secondary) 100%)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', marginBottom: 'var(--space-8)', flexWrap: 'wrap' }}>
                    <div
                      style={{
                        width: '56px',
                        height: '56px',
                        borderRadius: 'var(--radius-xl)',
                        background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--coffee-mocha) 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: 'var(--shadow-md)',
                      }}
                    >
                      <svg width={28} height={28} viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth={2.5}>
                        <path d="M12 5v14M5 12h14" />
                      </svg>
                    </div>
                    <div>
                      <h2 style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, margin: 0, marginBottom: 'var(--space-1)', color: 'var(--text-primary)' }}>
                        Create New Task
                      </h2>
                      <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: 'var(--text-base)' }}>
                        Add a new task to your list
                      </p>
                    </div>
                  </div>

                  <form onSubmit={handleCreateTask} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
                    <div>
                      <label
                        style={{
                          display: 'block',
                          fontSize: 'var(--text-base)',
                          fontWeight: 600,
                          marginBottom: 'var(--space-3)',
                          color: 'var(--text-primary)',
                        }}
                      >
                        Task Title *
                      </label>
                      <input
                        type="text"
                        placeholder="What needs to be done?"
                        value={newTask.title}
                        onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                        className="input"
                        style={{
                          padding: 'var(--space-4) var(--space-5)',
                          fontSize: 'var(--text-base)',
                          borderRadius: 'var(--radius-lg)',
                        }}
                        required
                        disabled={isCreating}
                      />
                    </div>

                    <div>
                      <label
                        style={{
                          display: 'block',
                          fontSize: 'var(--text-base)',
                          fontWeight: 600,
                          marginBottom: 'var(--space-3)',
                          color: 'var(--text-primary)',
                        }}
                      >
                        Description
                      </label>
                      <textarea
                        placeholder="Add some details..."
                        value={newTask.description}
                        onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                        className="textarea"
                        rows={4}
                        style={{
                          padding: 'var(--space-4) var(--space-5)',
                          fontSize: 'var(--text-base)',
                          borderRadius: 'var(--radius-lg)',
                        }}
                        disabled={isCreating}
                      />
                    </div>

                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                        gap: 'var(--space-6)',
                      }}
                    >
                      <div>
                        <label
                          style={{
                            display: 'block',
                            fontSize: 'var(--text-base)',
                            fontWeight: 600,
                            marginBottom: 'var(--space-3)',
                            color: 'var(--text-primary)',
                          }}
                        >
                          Priority
                        </label>
                        <select
                          value={newTask.priority}
                          onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as any })}
                          className="select"
                          style={{
                            padding: 'var(--space-4) var(--space-5)',
                            fontSize: 'var(--text-base)',
                            borderRadius: 'var(--radius-lg)',
                          }}
                          disabled={isCreating}
                        >
                          <option value="low">Low</option>
                          <option value="medium">Medium</option>
                          <option value="high">High</option>
                          <option value="urgent">Urgent</option>
                        </select>
                      </div>

                      <div>
                        <label
                          style={{
                            display: 'block',
                            fontSize: 'var(--text-base)',
                            fontWeight: 600,
                            marginBottom: 'var(--space-3)',
                            color: 'var(--text-primary)',
                          }}
                        >
                          Status
                        </label>
                        <select
                          value={newTask.status}
                          onChange={(e) => setNewTask({ ...newTask, status: e.target.value as any })}
                          className="select"
                          style={{
                            padding: 'var(--space-4) var(--space-5)',
                            fontSize: 'var(--text-base)',
                            borderRadius: 'var(--radius-lg)',
                          }}
                          disabled={isCreating}
                        >
                          <option value="todo">To Do</option>
                          <option value="in_progress">In Progress</option>
                          <option value="done">Done</option>
                        </select>
                      </div>
                    </div>

                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={isCreating || !newTask.title.trim()}
                      style={{
                        width: '100%',
                        padding: 'var(--space-5)',
                        fontSize: 'var(--text-lg)',
                        fontWeight: 600,
                        borderRadius: 'var(--radius-lg)',
                        marginTop: 'var(--space-2)',
                        minHeight: '50px',
                      }}
                    >
                      {isCreating ? (
                        <>
                          <span className="spinner" style={{ width: 20, height: 20, borderWidth: 2.5 }} />
                          Creating...
                        </>
                      ) : (
                        <>
                          <svg width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                            <path d="M12 5v14M5 12h14" />
                          </svg>
                          Create Task
                        </>
                      )}
                    </button>
                  </form>
                </div>
              </section>

              {/* Quick Links */}
              <section style={{ marginTop: 'var(--space-8)' }}>
                <div
                  className="card"
                  style={{
                    padding: 'var(--space-6)',
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%)',
                  }}
                >
                  <h3 style={{ fontSize: 'var(--text-lg)', fontWeight: 600, marginBottom: 'var(--space-4)', color: 'var(--text-primary)' }}>
                    Want to see your tasks?
                  </h3>
                  <p style={{ color: 'var(--text-muted)', marginBottom: 'var(--space-5)' }}>
                    View and manage all your tasks in one place
                  </p>
                  <button
                    onClick={() => router.push('/tasks')}
                    className="btn btn-secondary"
                    style={{ padding: 'var(--space-4) var(--space-6)', fontSize: 'var(--text-base)' }}
                  >
                    <svg width={18} height={18} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                      <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
                      <rect x="9" y="3" width="6" height="4" rx="1" />
                    </svg>
                    View All Tasks
                  </button>
                </div>
              </section>
            </div>

            {/* Right: Analytics Sidebar */}
            <aside style={{ position: 'sticky', top: 'var(--space-6)', height: 'fit-content' }}>
              <div className="card" style={{ padding: 'var(--space-6)' }}>
                <h3
                  style={{
                    fontSize: 'var(--text-lg)',
                    fontWeight: 600,
                    marginBottom: 'var(--space-6)',
                    color: 'var(--text-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-2)',
                  }}
                >
                  <svg width={20} height={20} viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth={2}>
                    <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
                    <path d="M22 12A10 10 0 0 0 12 2v10z" />
                  </svg>
                  Quick Stats
                </h3>

                <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-6)' }}>
                  Create tasks and visit the Tasks page to see your analytics.
                </p>

                {/* Mini Stats Preview */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                  <div
                    style={{
                      background: 'var(--bg-secondary)',
                      borderRadius: 'var(--radius-lg)',
                      padding: 'var(--space-4)',
                      textAlign: 'center',
                    }}
                  >
                    <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: 'var(--accent-primary)' }}>
                      <svg width={32} height={32} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                        <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
                        <rect x="9" y="3" width="6" height="4" rx="1" />
                      </svg>
                    </div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 'var(--space-2)' }}>
                      Tasks
                    </div>
                  </div>

                  <div
                    style={{
                      background: 'var(--bg-secondary)',
                      borderRadius: 'var(--radius-lg)',
                      padding: 'var(--space-4)',
                      textAlign: 'center',
                      cursor: 'pointer',
                    }}
                    onClick={() => router.push('/tasks')}
                  >
                    <div style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, color: 'var(--success)' }}>
                      <svg width={32} height={32} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                        <polyline points="20 6 9 17 4 12" />
                      </svg>
                    </div>
                    <div style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 'var(--space-2)' }}>
                      Done
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    marginTop: 'var(--space-6)',
                    padding: 'var(--space-4)',
                    background: 'var(--accent-light)',
                    borderRadius: 'var(--radius-lg)',
                    textAlign: 'center',
                  }}
                >
                  <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--accent-primary)', fontWeight: 500 }}>
                    Go to Tasks page for full analytics
                  </p>
                </div>
              </div>
            </aside>
          </div>
        </main>
      </div>

      {/* Responsive CSS for mobile */}
      <style jsx>{`
        @media (max-width: 767px) {
          .dashboard-content {
            margin-left: 0 !important;
            width: 100% !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
          }
        }

        @media (max-width: 639px) {
          .dashboard-content {
            margin-left: 0 !important;
            width: 100% !important;
          }

          .dashboard-main {
            padding: var(--space-5) var(--space-3) !important;
          }

          .dashboard-grid {
            grid-template-columns: 1fr !important;
            gap: var(--space-5) !important;
            padding: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
          }

        @media (min-width: 640px) and (max-width: 767px) {
          .dashboard-grid {
            gridTemplateColumns: 1fr !important;
          }

          .dashboard-main {
            padding: var(--space-6) var(--space-4) !important;
          }

          aside {
            position: static !important;
          }
        }

        @media (min-width: 768px) and (max-width: 1023px) {
          .dashboard-grid {
            gridTemplateColumns: minmax(0, 1.2fr) minmax(280px, 350px) !important;
            gap: var(--space-6) !important;
          }

          .dashboard-main {
            padding: var(--space-6) var(--space-4) !important;
          }
        }
      `}</style>
    </>
  );
}
