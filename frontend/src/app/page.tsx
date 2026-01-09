'use client';

/**
 * Homepage - Modern, Attractive & Fully Responsive
 * Built with love by Duaa Pirzada
 */

import Link from 'next/link';
import { Navigation } from '@/components';

export default function HomePage() {
  return (
    <div>
      <Navigation />
      <div
        style={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--coffee-cream) 100%)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Hero Section */}
        <section
          className="hero-section"
          style={{
            minHeight: 'calc(100vh - 80px)',
            display: 'flex',
            alignItems: 'center',
            padding: 'var(--space-16) var(--space-6)',
            position: 'relative',
            zIndex: 1,
          }}
        >
          <div
            className="container"
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: 'var(--space-16)',
              alignItems: 'center',
            }}
          >
            {/* Left: Content */}
            <div className="hero-content" style={{ maxWidth: '600px', width: '100%' }}>
              {/* Badge */}
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                  padding: 'var(--space-2) var(--space-4)',
                  background: 'var(--accent-light)',
                  borderRadius: 'var(--radius-full)',
                  marginBottom: 'var(--space-6)',
                  boxShadow: '0 2px 8px rgba(139, 94, 60, 0.15)',
                }}
              >
                <span
                  className="badge-text"
                  style={{
                    fontWeight: 600,
                    color: 'var(--accent-primary)',
                    letterSpacing: '0.5px',
                  }}
                >
                  ✨ Transform Your Productivity
                </span>
              </div>

              {/* Heading */}
              <h1
                className="hero-title"
                style={{
                  fontWeight: 800,
                  lineHeight: 1.05,
                  marginBottom: 'var(--space-6)',
                  background: 'linear-gradient(135deg, var(--coffee-espresso) 0%, var(--coffee-mocha) 50%, var(--accent-primary) 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                  letterSpacing: '-0.02em',
                }}
              >
                Organize Tasks.
                <br />
                <span
                  style={{
                    background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--coffee-caramel) 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  Achieve More.
                </span>
              </h1>

              {/* Description */}
              <p
                className="hero-description"
                style={{
                  color: 'var(--text-secondary)',
                  marginBottom: 'var(--space-10)',
                  lineHeight: 1.8,
                  fontWeight: 400,
                }}
              >
                ActionMind AI is your intelligent task management companion. Organize your work,
                track progress, and reach your goals with beautiful analytics and smart insights.
              </p>

              {/* CTA Buttons */}
              <div
                className="cta-buttons"
                style={{
                  display: 'flex',
                  gap: 'var(--space-4)',
                  flexWrap: 'wrap',
                }}
              >
                <Link
                  href="/signup"
                  className="btn btn-primary btn-lg hero-btn-primary"
                  style={{
                    padding: 'var(--space-5) var(--space-10)',
                    fontWeight: 600,
                    boxShadow: '0 4px 14px rgba(139, 94, 60, 0.3)',
                    background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--coffee-mocha) 100%)',
                    border: 'none',
                    transition: 'all 0.3s ease',
                    display: 'inline-flex',
                    alignItems: 'center',
                    minWidth: '180px',
                    justifyContent: 'center',
                  }}
                >
                  Get Started Free
                  <svg
                    className="desktop-icon"
                    width={20}
                    height={20}
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={2.5}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    style={{ marginLeft: '8px' }}
                  >
                    <line x1="5" y1="12" x2="19" y2="12" />
                    <polyline points="12 5 19 12 12 19" />
                  </svg>
                </Link>
                <Link
                  href="/signin"
                  className="btn btn-secondary btn-lg hero-btn-secondary"
                  style={{
                    padding: 'var(--space-5) var(--space-10)',
                    fontWeight: 600,
                    borderWidth: '2px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    minWidth: '140px',
                    justifyContent: 'center',
                  }}
                >
                  Sign In
                </Link>
              </div>

              {/* Stats/Social Proof */}
              <div
                className="stats-grid"
                style={{
                  marginTop: 'var(--space-12)',
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: 'var(--space-8)',
                }}
              >
                <div>
                  <div
                    className="stat-number"
                    style={{
                      fontWeight: 700,
                      color: 'var(--accent-primary)',
                      marginBottom: 'var(--space-1)',
                    }}
                  >
                    1000+
                  </div>
                  <div
                    className="stat-label"
                    style={{
                      color: 'var(--text-muted)',
                    }}
                  >
                    Active Users
                  </div>
                </div>
                <div>
                  <div
                    className="stat-number"
                    style={{
                      fontWeight: 700,
                      color: 'var(--accent-primary)',
                      marginBottom: 'var(--space-1)',
                    }}
                  >
                    10K+
                  </div>
                  <div
                    className="stat-label"
                    style={{
                      color: 'var(--text-muted)',
                    }}
                  >
                    Tasks Completed
                  </div>
                </div>
                <div>
                  <div
                    className="stat-number"
                    style={{
                      fontWeight: 700,
                      color: 'var(--accent-primary)',
                      marginBottom: 'var(--space-1)',
                    }}
                  >
                    99%
                  </div>
                  <div
                    className="stat-label"
                    style={{
                      color: 'var(--text-muted)',
                    }}
                  >
                    Satisfaction
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Productivity Illustration */}
            <div className="hero-illustration">
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                }}
              >
                <div
                  style={{
                    position: 'relative',
                    width: '100%',
                    maxWidth: '500px',
                    aspectRatio: 1,
                  }}
                >
                  {/* Background glow */}
                  <div
                    style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      width: '100%',
                      height: '100%',
                      background: 'radial-gradient(circle, var(--accent-light) 0%, transparent 70%)',
                      borderRadius: '50%',
                      opacity: 0.5,
                    }}
                  />

                  {/* Abstract Productivity Icons SVG */}
                  <svg
                    viewBox="0 0 200 200"
                    style={{
                      width: '100%',
                      height: '100%',
                      filter: 'drop-shadow(0 20px 40px rgba(107, 68, 35, 0.2))',
                    }}
                  >
                    <defs>
                      <linearGradient id="taskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="var(--coffee-latte)" />
                        <stop offset="100%" stopColor="var(--coffee-mocha)" />
                      </linearGradient>
                      <linearGradient id="checkGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="var(--success)" />
                        <stop offset="100%" stopColor="#10b981" />
                      </linearGradient>
                    </defs>

                    {/* Central Task Card */}
                    <rect
                      x="40"
                      y="50"
                      width="120"
                      height="90"
                      rx="12"
                      fill="url(#taskGradient)"
                      stroke="var(--coffee-mocha)"
                      strokeWidth="2"
                      opacity="0.9"
                    />

                    {/* Checkmark icon in center */}
                    <circle cx="100" cy="95" r="25" fill="url(#checkGradient)" opacity="0.95">
                      <animate
                        attributeName="r"
                        values="25;27;25"
                        dur="2s"
                        repeatCount="indefinite"
                      />
                    </circle>
                    <path
                      d="M90 95 L97 102 L112 87"
                      stroke="white"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      fill="none"
                    />

                    {/* Floating tasks - top left */}
                    <g opacity="0.7">
                      <rect x="20" y="20" width="50" height="40" rx="8" fill="var(--accent-primary)" />
                      <line x1="30" y1="35" x2="60" y2="35" stroke="white" strokeWidth="2" opacity="0.5" />
                      <line x1="30" y1="45" x2="50" y2="45" stroke="white" strokeWidth="2" opacity="0.5" />
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; 0,-10; 0,0"
                        dur="3s"
                        repeatCount="indefinite"
                      />
                    </g>

                    {/* Floating tasks - top right */}
                    <g opacity="0.7">
                      <rect x="130" y="25" width="50" height="40" rx="8" fill="var(--coffee-latte)" />
                      <circle cx="145" cy="45" r="4" fill="var(--coffee-mocha)" opacity="0.6" />
                      <circle cx="160" cy="45" r="4" fill="var(--success)" opacity="0.8" />
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; 5,-8; 0,0"
                        dur="2.5s"
                        repeatCount="indefinite"
                      />
                    </g>

                    {/* Floating tasks - bottom */}
                    <g opacity="0.7">
                      <rect x="60" y="155" width="80" height="35" rx="8" fill="var(--coffee-caramel)" />
                      <rect x="75" y="168" width="12" height="12" rx="2" fill="white" opacity="0.8" />
                      <rect x="95" y="168" width="12" height="12" rx="2" fill="var(--success)" opacity="0.9" />
                      <rect x="115" y="168" width="12" height="12" rx="2" fill="white" opacity="0.6" />
                      <animateTransform
                        attributeName="transform"
                        type="translate"
                        values="0,0; 0,8; 0,0"
                        dur="2.8s"
                        repeatCount="indefinite"
                      />
                    </g>

                    {/* Progress indicator */}
                    <g>
                      <circle
                        cx="100"
                        cy="95"
                        r="32"
                        fill="none"
                        stroke="var(--accent-primary)"
                        strokeWidth="2"
                        opacity="0.3"
                        strokeDasharray="8 4"
                      >
                        <animateTransform
                          attributeName="transform"
                          type="rotate"
                          from="0 100 95"
                          to="360 100 95"
                          dur="8s"
                          repeatCount="indefinite"
                        />
                      </circle>
                    </g>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section
          className="features-section"
          style={{
            padding: 'clamp(var(--space-12), 6vw, var(--space-20)) var(--space-4)',
            background: 'var(--bg-card)',
          }}
        >
          <div className="container">
            <h2
              className="features-title"
              style={{
                textAlign: 'center',
                marginBottom: 'var(--space-4)',
                fontWeight: 700,
              }}
            >
              Everything You Need to Stay Productive
            </h2>
            <p
              className="features-subtitle"
              style={{
                textAlign: 'center',
                marginBottom: 'var(--space-12)',
                color: 'var(--text-muted)',
                maxWidth: '600px',
                marginLeft: 'auto',
                marginRight: 'auto',
              }}
            >
              Powerful features designed to help you manage tasks efficiently and achieve your goals.
            </p>

            <div
              className="features-grid"
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: 'var(--space-8)',
              }}
            >
              {/* Feature 1 */}
              <div className="card feature-card">
                <div
                  style={{
                    width: '56px',
                    height: '56px',
                    borderRadius: 'var(--radius-xl)',
                    background: 'var(--accent-light)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 'var(--space-5)',
                  }}
                >
                  <svg width={28} height={28} viewBox="0 0 24 24" fill="none" stroke="var(--accent-primary)" strokeWidth={2}>
                    <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                  </svg>
                </div>
                <h3 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-3)' }}>Smart Task Management</h3>
                <p style={{ fontSize: 'var(--text-sm)', lineHeight: 1.7, color: 'var(--text-secondary)' }}>
                  Create, organize, and prioritize tasks with ease. Set due dates, add descriptions, and track progress effortlessly.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="card feature-card">
                <div
                  style={{
                    width: '56px',
                    height: '56px',
                    borderRadius: 'var(--radius-xl)',
                    background: 'var(--success-light)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 'var(--space-5)',
                  }}
                >
                  <svg width={28} height={28} viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth={2}>
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                </div>
                <h3 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-3)' }}>Progress Tracking</h3>
                <p style={{ fontSize: 'var(--text-sm)', lineHeight: 1.7, color: 'var(--text-secondary)' }}>
                  Visualize your productivity with beautiful analytics. Track completion rates and monitor your progress over time.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="card feature-card">
                <div
                  style={{
                    width: '56px',
                    height: '56px',
                    borderRadius: 'var(--radius-xl)',
                    background: 'var(--info-light)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 'var(--space-5)',
                  }}
                >
                  <svg width={28} height={28} viewBox="0 0 24 24" fill="none" stroke="var(--info)" strokeWidth={2}>
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                    <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                    <line x1="12" y1="22.08" x2="12" y2="12" />
                  </svg>
                </div>
                <h3 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-3)' }}>Beautiful Design</h3>
                <p style={{ fontSize: 'var(--text-sm)', lineHeight: 1.7, color: 'var(--text-secondary)' }}>
                  Enjoy a clean, modern interface with warm colors. Dark mode support for comfortable use any time of day.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer
          className="footer"
          style={{
            padding: 'clamp(var(--space-8), 5vw, var(--space-12)) var(--space-4)',
            background: 'var(--bg-secondary)',
            borderTop: '1px solid var(--border-subtle)',
          }}
        >
          <div className="container">
            <div
              className="footer-grid"
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: 'var(--space-10)',
                marginBottom: 'var(--space-10)',
              }}
            >
              {/* Brand Section */}
              <div>
                <h3
                  style={{
                    fontSize: 'var(--text-xl)',
                    fontWeight: 700,
                    marginBottom: 'var(--space-4)',
                    background: 'linear-gradient(135deg, var(--accent-primary) 0%, var(--coffee-mocha) 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                  }}
                >
                  ActionMind AI
                </h3>
                <p
                  style={{
                    fontSize: 'var(--text-sm)',
                    color: 'var(--text-muted)',
                    lineHeight: 1.7,
                    marginBottom: 'var(--space-4)',
                  }}
                >
                  Your intelligent task management companion for achieving more every day.
                </p>
              </div>
            </div>

            {/* Bottom Bar */}
            <div
              className="footer-bottom"
              style={{
                paddingTop: 'var(--space-8)',
                borderTop: '1px solid var(--border-subtle)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 'var(--space-4)',
              }}
            >
              <p
                style={{
                  margin: 0,
                  fontSize: 'var(--text-sm)',
                  color: 'var(--text-muted)',
                }}
              >
                © 2025 ActionMind AI. All rights reserved.
              </p>
              <p
                style={{
                  margin: 0,
                  fontSize: 'var(--text-sm)',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-2)',
                }}
              >
                Made with
                <svg width={16} height={16} viewBox="0 0 24 24" fill="var(--danger)" stroke="var(--danger)" strokeWidth={2}>
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                </svg>
                by
                <Link
                  href="#"
                  style={{
                    color: 'var(--accent-primary)',
                    fontWeight: 600,
                    textDecoration: 'none',
                  }}
                >
                  Duaa Pirzada
                </Link>
              </p>
            </div>
          </div>
        </footer>

        {/* Responsive CSS */}
        <style jsx>{`
          /* Mobile styles (< 640px) */
          @media (max-width: 639px) {
            .hero-section {
              min-height: auto !important;
              padding: var(--space-10) var(--space-4) !important;
            }

            .container {
              display: block !important;
              gridTemplateColumns: 1fr !important;
              gap: var(--space-6) !important;
              text-align: center;
            }

            .hero-content {
              maxWidth: 100% !important;
            }

            .badge-text {
              fontSize: var(--text-xs) !important;
            }

            .hero-title {
              font-size: 1.75rem !important;
              line-height: 1.15 !important;
            }

            .hero-description {
              fontSize: 0.95rem !important;
            }

            .cta-buttons {
              flex-direction: column !important;
              width: 100% !important;
            }

            .hero-btn-primary,
            .hero-btn-secondary {
              width: 100% !important;
              padding: var(--space-4) var(--space-6) !important;
              font-size: var(--text-sm) !important;
              min-width: unset !important;
              justifyContent: center !important;
            }

            .desktop-icon {
              display: none !important;
            }

            .stats-grid {
              gridTemplateColumns: 1fr !important;
              gap: var(--space-4) !important;
            }

            .stat-number {
              fontSize: var(--text-xl) !important;
            }

            .stat-label {
              fontSize: var(--text-xs) !important;
            }

            .hero-illustration {
              display: none !important;
            }

            .features-section {
              padding: var(--space-10) var(--space-4) !important;
            }

            .features-grid {
              gridTemplateColumns: 1fr !important;
              gap: var(--space-6) !important;
            }

            .feature-card {
              padding: var(--space-5) !important;
            }

            .footer {
              padding: var(--space-8) var(--space-4) !important;
            }

            .footer-grid {
              gridTemplateColumns: 1fr !important;
              gap: var(--space-6) !important;
            }

            .footer-bottom {
              flex-direction: column !important;
              textAlign: center;
              gap: var(--space-3) !important;
            }
          }

          /* Small tablet (640px - 767px) */
          @media (min-width: 640px) and (max-width: 767px) {
            .hero-section {
              padding: var(--space-12) var(--space-5) !important;
            }

            .hero-title {
              font-size: 2rem !important;
            }

            .stats-grid {
              gridTemplateColumns: 1fr !important;
              gap: var(--space-4) !important;
            }

            .features-grid {
              gridTemplateColumns: 1fr !important;
            }
          }

          /* Tablet styles (768px - 1023px) */
          @media (min-width: 768px) and (max-width: 1023px) {
            .hero-section {
              padding: var(--space-14) var(--space-6) !important;
            }

            .hero-title {
              font-size: clamp(2rem, 5vw, 3rem) !important;
            }

            .hero-content {
              maxWidth: 100% !important;
            }

            .features-grid {
              gridTemplateColumns: repeat(auto-fit, minmax(240px, 1fr)) !important;
            }

            .container {
              gap: var(--space-12) !important;
            }
          }

          /* Animation keyframes */
          @keyframes float {
            0%,
            100% {
              transform: translateY(0);
            }
            50% {
              transform: translateY(-20px);
            }
          }
        `}</style>
      </div>
    </div>
  );
}
