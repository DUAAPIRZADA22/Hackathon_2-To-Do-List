'use client';

/**
 * Sign In Page - Coffee Theme
 * Warm, inviting authentication experience
 */

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { signIn } from '@/lib/auth';
import { useToast } from '@/lib/toast';

export default function SignInPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await signIn({ email, password });
      showToast('Welcome back!', 'success');
      router.push('/dashboard');
    } catch (error: any) {
      // Handle Zod/Pydantic validation errors safely
      let errorMessage = 'Failed to sign in';

      if (error?.detail) {
        if (typeof error.detail === 'string') {
          errorMessage = error.detail;
        } else if (Array.isArray(error.detail) && error.detail.length > 0) {
          // Zod/Pydantic validation errors: [{type, loc, msg, input}, ...]
          errorMessage = error.detail[0]?.msg || errorMessage;
        } else if (error.detail?.msg) {
          errorMessage = error.detail.msg;
        } else if (error.message) {
          errorMessage = error.message;
        }
      } else if (error?.message) {
        errorMessage = error.message;
      }

      showToast(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-4)',
        background:
          'linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%)',
      }}
      className="animate-fade-in"
    >
      <div
        className="container-narrow"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          width: '100%',
          maxWidth: '480px',
        }}
      >
        {/* Productivity Icon Illustration */}
        <div
          style={{
            marginBottom: 'clamp(var(--space-6), 4vw, var(--space-8))',
            textAlign: 'center',
          }}
        >
          <svg
            width="64"
            height="64"
            viewBox="0 0 24 24"
            fill="none"
            stroke="var(--accent-primary)"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{ margin: '0 auto var(--space-3)' }}
          >
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <h1
            style={{
              fontSize: 'clamp(var(--text-2xl), 5vw, var(--text-3xl))',
              fontWeight: 700,
              marginBottom: 'var(--space-2)',
              background:
                'linear-gradient(135deg, var(--accent-primary) 0%, var(--coffee-mocha) 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            Welcome Back
          </h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: 0, fontSize: 'clamp(var(--text-sm), 2.5vw, var(--text-base))' }}>
            Sign in to continue to ActionMind AI
          </p>
        </div>

        {/* Sign In Card */}
        <div
          className="card card-elevated"
          style={{ width: '100%', maxWidth: '420px', animation: 'scaleIn 0.3s ease-out', padding: 'clamp(var(--space-6), 4vw, var(--space-8))' }}
        >
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'clamp(var(--space-4), 3vw, var(--space-5))' }}>
            {/* Email Field */}
            <div>
              <label
                htmlFor="email"
                style={{
                  display: 'block',
                  fontSize: 'var(--text-sm)',
                  fontWeight: 500,
                  marginBottom: 'var(--space-2)',
                  color: 'var(--text-primary)',
                }}
              >
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="input"
                placeholder="you@example.com"
                disabled={isLoading}
                style={{ fontSize: 'var(--text-base)' }}
              />
            </div>

            {/* Password Field */}
            <div>
              <label
                htmlFor="password"
                style={{
                  display: 'block',
                  fontSize: 'var(--text-sm)',
                  fontWeight: 500,
                  marginBottom: 'var(--space-2)',
                  color: 'var(--text-primary)',
                }}
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="input"
                placeholder="••••••••"
                disabled={isLoading}
                style={{ fontSize: 'var(--text-base)' }}
              />
            </div>

            {/* Forgot Password Link */}
            <div style={{ textAlign: 'right' }}>
              <Link
                href="/forgot-password"
                style={{
                  fontSize: 'var(--text-sm)',
                  color: 'var(--accent-primary)',
                  textDecoration: 'none',
                  fontWeight: 500,
                }}
              >
                Forgot password?
              </Link>
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              disabled={isLoading || !email.trim() || !password.trim()}
              className="btn btn-primary"
              style={{
                width: '100%',
                marginTop: 'var(--space-2)',
                minHeight: '48px',
                fontSize: 'clamp(var(--text-base), 2.5vw, var(--text-lg))',
                position: 'relative',
              }}
            >
              {isLoading ? (
                <>
                  <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="divider" style={{ margin: 'var(--space-6) 0' }} />

          {/* Sign Up Link */}
          <p style={{ textAlign: 'center', margin: 0, fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
            Don't have an account?{' '}
            <Link
              href="/signup"
              style={{
                color: 'var(--accent-primary)',
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              Sign up for free
            </Link>
          </p>
        </div>

        {/* Bottom Note */}
        <p
          style={{
            marginTop: 'var(--space-6)',
            fontSize: 'var(--text-sm)',
            color: 'var(--text-muted)',
            textAlign: 'center',
          }}
        >
          Your productivity journey continues here
        </p>
      </div>
    </div>
  );
}
