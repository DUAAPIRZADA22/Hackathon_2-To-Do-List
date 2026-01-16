'use client';

/**
 * Sign Up Page - Coffee Theme
 * Warm, welcoming registration experience
 */

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { signUp } from '@/lib/auth';
import { useToast } from '@/lib/toast';

export default function SignUpPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await signUp({ username, email, password });
      showToast('Account created successfully! Welcome to ActionMind AI', 'success');
      router.push('/dashboard');
    } catch (error: any) {
      // Handle Zod/Pydantic validation errors safely
      let errorMessage = 'Failed to create account';

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
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <line x1="20" y1="8" x2="20" y2="14" />
            <line x1="23" y1="11" x2="17" y2="11" />
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
            Join ActionMind AI
          </h1>
          <p style={{ color: 'var(--text-muted)', marginBottom: 0, fontSize: 'clamp(var(--text-sm), 2.5vw, var(--text-base))' }}>
            Start amplifying your productivity today
          </p>
        </div>

        {/* Sign Up Card */}
        <div
          className="card card-elevated"
          style={{ width: '100%', maxWidth: '420px', animation: 'scaleIn 0.3s ease-out', padding: 'clamp(var(--space-6), 4vw, var(--space-8))' }}
        >
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'clamp(var(--space-4), 3vw, var(--space-5))' }}>
            {/* Username Field */}
            <div>
              <label
                htmlFor="username"
                style={{
                  display: 'block',
                  fontSize: 'var(--text-sm)',
                  fontWeight: 500,
                  marginBottom: 'var(--space-2)',
                  color: 'var(--text-primary)',
                }}
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                minLength={3}
                className="input"
                placeholder="johndoe"
                disabled={isLoading}
                style={{ fontSize: '16px' }}
              />
            </div>

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
                style={{ fontSize: '16px' }}
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
                minLength={6}
                className="input"
                placeholder="••••••••"
                disabled={isLoading}
                style={{ fontSize: '16px' }}
              />
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 'var(--space-1)', marginBottom: 0 }}>
                Must be at least 6 characters
              </p>
            </div>

            {/* Terms */}
            <div style={{ display: 'flex', gap: 'var(--space-2)', fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
              <input type="checkbox" required id="terms" style={{ marginTop: 2 }} />
              <label htmlFor="terms" style={{ margin: 0, lineHeight: 1.5 }}>
                I agree to the{' '}
                <Link href="/terms" style={{ color: 'var(--accent-primary)', fontWeight: 500 }}>
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link href="/privacy" style={{ color: 'var(--accent-primary)', fontWeight: 500 }}>
                  Privacy Policy
                </Link>
              </label>
            </div>

            {/* Sign Up Button */}
            <button
              type="submit"
              disabled={isLoading || !username.trim() || !email.trim() || !password.trim()}
              className="btn btn-primary"
              style={{
                width: '100%',
                marginTop: 'var(--space-2)',
                minHeight: '48px',
                fontSize: 'clamp(var(--text-base), 2.5vw, var(--text-lg))',
              }}
            >
              {isLoading ? (
                <>
                  <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="divider" style={{ margin: 'var(--space-6) 0' }} />

          {/* Sign In Link */}
          <p style={{ textAlign: 'center', margin: 0, fontSize: 'var(--text-sm)', color: 'var(--text-secondary)' }}>
            Already have an account?{' '}
            <Link
              href="/signin"
              style={{
                color: 'var(--accent-primary)',
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              Sign in instead
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
          Your productivity journey starts here
        </p>
      </div>
    </div>
  );
}
