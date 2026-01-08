'use client';

/**
 * Task Analytics Component
 * Displays task completion overview with pie chart and statistics
 * Uses warm/neutral theme colors without coffee-related content
 */

import { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { Task } from '@/types/api';

interface TaskAnalyticsProps {
  tasks: Task[];
}

interface StatCardProps {
  label: string;
  value: number;
  color: string;
  bgColor: string;
  icon: React.ReactNode;
  trend?: string;
}

const StatCard = ({ label, value, color, bgColor, icon, trend }: StatCardProps) => (
  <div
    style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-xl)',
      padding: 'var(--space-6)',
      textAlign: 'center',
      transition: 'all var(--transition-base)',
      position: 'relative',
      overflow: 'hidden',
    }}
    className="card"
  >
    {/* Background accent */}
    <div
      style={{
        position: 'absolute',
        top: -20,
        right: -20,
        width: 80,
        height: 80,
        background: bgColor,
        borderRadius: '50%',
        opacity: 0.15,
        pointerEvents: 'none',
      }}
    />

    {/* Icon */}
    <div
      style={{
        width: 48,
        height: 48,
        borderRadius: 'var(--radius-lg)',
        background: bgColor,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto var(--space-3)',
        color: color,
      }}
    >
      {icon}
    </div>

    {/* Value */}
    <div
      style={{
        fontSize: 'var(--text-3xl)',
        fontWeight: 700,
        color: color,
        marginBottom: 'var(--space-1)',
        fontFamily: 'var(--font-display)',
      }}
    >
      {value}
    </div>

    {/* Label */}
    <div
      style={{
        fontSize: 'var(--text-sm)',
        color: 'var(--text-secondary)',
        margin: 0,
        fontWeight: 500,
      }}
    >
      {label}
    </div>

    {/* Trend indicator */}
    {trend && (
      <div
        style={{
          fontSize: 'var(--text-xs)',
          color: 'var(--text-muted)',
          marginTop: 'var(--space-2)',
        }}
      >
        {trend}
      </div>
    )}
  </div>
);

export const TaskAnalytics = ({ tasks }: TaskAnalyticsProps) => {
  // Calculate task statistics
  const stats = useMemo(() => {
    const total = tasks.length;
    const completed = tasks.filter((t) => t.status === 'done').length;
    const inProgress = tasks.filter((t) => t.status === 'in_progress').length;
    const pending = tasks.filter((t) => t.status === 'todo').length;

    // Calculate overdue tasks
    const now = new Date();
    const overdue = tasks.filter(
      (t) => t.due_date && new Date(t.due_date) < now && t.status !== 'done'
    ).length;

    return { total, completed, inProgress, pending, overdue };
  }, [tasks]);

  // Prepare chart data
  const chartData = useMemo(() => {
    return [
      {
        name: 'Completed',
        value: stats.completed,
        color: 'var(--success)',
      },
      {
        name: 'In Progress',
        value: stats.inProgress,
        color: 'var(--info)',
      },
      {
        name: 'Pending',
        value: stats.pending,
        color: 'var(--warning)',
      },
    ].filter((item) => item.value > 0);
  }, [stats]);

  // Calculate completion rate
  const completionRate = useMemo(() => {
    if (stats.total === 0) return 0;
    return Math.round((stats.completed / stats.total) * 100);
  }, [stats]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const percentage = stats.total > 0
        ? Math.round((data.value / stats.total) * 100)
        : 0;

      return (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-lg)',
            padding: 'var(--space-3) var(--space-4)',
            boxShadow: 'var(--shadow-lg)',
          }}
        >
          <div
            style={{
              fontSize: 'var(--text-sm)',
              fontWeight: 500,
              color: 'var(--text-primary)',
              marginBottom: 'var(--space-1)',
            }}
          >
            {data.name}
          </div>
          <div
            style={{
              fontSize: 'var(--text-xs)',
              color: 'var(--text-muted)',
            }}
          >
            {data.value} tasks ({percentage}%)
          </div>
        </div>
      );
    }
    return null;
  };

  // Custom legend
  const CustomLegend = ({ payload }: any) => {
    return (
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 'var(--space-6)',
          justifyContent: 'center',
          marginTop: 'var(--space-6)',
        }}
      >
        {payload.map((entry: any, index: number) => (
          <div
            key={index}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-2)',
            }}
          >
            <div
              style={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                background: entry.color,
              }}
            />
            <span
              style={{
                fontSize: 'var(--text-sm)',
                color: 'var(--text-secondary)',
                fontWeight: 500,
              }}
            >
              {entry.value}
            </span>
          </div>
        ))}
      </div>
    );
  };

  // Empty state
  if (stats.total === 0) {
    return (
      <div
        className="card"
        style={{
          textAlign: 'center',
          padding: 'var(--space-12)',
          background: 'var(--bg-card)',
        }}
      >
        <svg
          width={64}
          height={64}
          viewBox="0 0 24 24"
          fill="none"
          stroke="var(--text-muted)"
          strokeWidth={1.5}
          style={{ margin: '0 auto var(--space-4)', opacity: 0.5 }}
        >
          <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
          <rect x="9" y="3" width="6" height="4" rx="1" />
        </svg>
        <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>
          No tasks yet. Create your first task to see analytics!
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
      {/* Stats Cards Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 'var(--space-4)',
        }}
      >
        <StatCard
          label="Total Tasks"
          value={stats.total}
          color="var(--accent-primary)"
          bgColor="var(--accent-light)"
          icon={
            <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
              <rect x="9" y="3" width="6" height="4" rx="1" />
            </svg>
          }
        />

        <StatCard
          label="Completed"
          value={stats.completed}
          color="var(--success)"
          bgColor="var(--success-light)"
          icon={
            <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          }
          trend={`${completionRate}% complete`}
        />

        <StatCard
          label="In Progress"
          value={stats.inProgress}
          color="var(--info)"
          bgColor="var(--info-light)"
          icon={
            <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          }
        />

        <StatCard
          label="Pending"
          value={stats.pending}
          color="var(--warning)"
          bgColor="var(--warning-light)"
          icon={
            <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          }
        />
      </div>

      {/* Pie Chart Section */}
      <div
        className="card"
        style={{
          background: 'var(--bg-card)',
          padding: 'var(--space-8)',
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 'var(--space-8)',
            alignItems: 'center',
          }}
        >
          {/* Chart */}
          <div>
            <h3
              style={{
                fontSize: 'var(--text-lg)',
                fontWeight: 600,
                marginBottom: 'var(--space-6)',
                color: 'var(--text-primary)',
                textAlign: 'center',
              }}
            >
              Task Distribution
            </h3>
            <ResponsiveContainer width="100%" aspect={1}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                  animationBegin={0}
                  animationDuration={800}
                  animationEasing="ease-out"
                >
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.color}
                      style={{
                        transition: 'opacity var(--transition-base)',
                        cursor: 'pointer',
                      }}
                      onMouseEnter={(e: any) => {
                        e.target.style.opacity = '0.8';
                      }}
                      onMouseLeave={(e: any) => {
                        e.target.style.opacity = '1';
                      }}
                    />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend content={<CustomLegend />} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Summary */}
          <div>
            <h3
              style={{
                fontSize: 'var(--text-lg)',
                fontWeight: 600,
                marginBottom: 'var(--space-6)',
                color: 'var(--text-primary)',
              }}
            >
              Summary
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              {/* Completion Rate */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: 'var(--space-4)',
                  background: 'var(--bg-secondary)',
                  borderRadius: 'var(--radius-lg)',
                }}
              >
                <div>
                  <div
                    style={{
                      fontSize: 'var(--text-sm)',
                      color: 'var(--text-muted)',
                      marginBottom: 'var(--space-1)',
                    }}
                  >
                    Completion Rate
                  </div>
                  <div
                    style={{
                      fontSize: 'var(--text-2xl)',
                      fontWeight: 700,
                      color: 'var(--success)',
                    }}
                  >
                    {completionRate}%
                  </div>
                </div>
                <svg
                  width={40}
                  height={40}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="var(--success)"
                  strokeWidth={2}
                  style={{ opacity: 0.8 }}
                >
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline points="22 4 12 14.01 9 11.01" />
                </svg>
              </div>

              {/* Breakdown */}
              {chartData.map((item) => {
                const percentage = stats.total > 0
                  ? Math.round((item.value / stats.total) * 100)
                  : 0;

                return (
                  <div
                    key={item.name}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--space-3)',
                      padding: 'var(--space-3)',
                      background: 'var(--bg-secondary)',
                      borderRadius: 'var(--radius-lg)',
                    }}
                  >
                    <div
                      style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        background: item.color,
                        flexShrink: 0,
                      }}
                    />
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          marginBottom: 'var(--space-1)',
                        }}
                      >
                        <span
                          style={{
                            fontSize: 'var(--text-sm)',
                            color: 'var(--text-primary)',
                            fontWeight: 500,
                          }}
                        >
                          {item.name}
                        </span>
                        <span
                          style={{
                            fontSize: 'var(--text-sm)',
                            color: 'var(--text-secondary)',
                          }}
                        >
                          {item.value}
                        </span>
                      </div>
                      <div
                        style={{
                          height: 4,
                          background: 'var(--bg-primary)',
                          borderRadius: 'var(--radius-full)',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            height: '100%',
                            width: `${percentage}%`,
                            background: item.color,
                            borderRadius: 'var(--radius-full)',
                            transition: 'width var(--transition-slow)',
                          }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Overdue warning */}
              {stats.overdue > 0 && (
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-3)',
                    padding: 'var(--space-4)',
                    background: 'var(--danger-light)',
                    borderRadius: 'var(--radius-lg)',
                    border: '1px solid var(--danger)',
                  }}
                >
                  <svg
                    width={20}
                    height={20}
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="var(--danger)"
                    strokeWidth={2}
                  >
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                  <div>
                    <div
                      style={{
                        fontSize: 'var(--text-sm)',
                        fontWeight: 600,
                        color: 'var(--danger)',
                      }}
                    >
                      {stats.overdue} Overdue
                    </div>
                    <div
                      style={{
                        fontSize: 'var(--text-xs)',
                        color: 'var(--text-muted)',
                      }}
                    >
                      Tasks past their due date
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
