'use client';

/**
 * Navigation Component - Clean & Minimal
 * Coffee-inspired colors, productivity-focused design
 * Only shows logo and essential actions
 */

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTheme } from './ThemeProvider';
import { ThemeToggle } from './ThemeToggle';
import { signOut, isAuthenticated, getCurrentUser } from '@/lib/auth';
import { useState, useEffect } from 'react';

export function Navigation() {
  const pathname = usePathname();
  const { theme } = useTheme();
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const authenticated = isAuthenticated();
    setIsLoggedIn(authenticated);
    if (authenticated) {
      setUser(getCurrentUser());
    } else {
      setUser(null);
    }
  }, [pathname]);

  const handleSignOut = async () => {
    await signOut();
    setIsMenuOpen(false);
  };

  // Auth links shown based on login state and current page
  const authLinks = isLoggedIn
    ? [] // No nav links when logged in - sidebar handles this
    : pathname === '/signin'
    ? [{ name: 'Sign Up', href: '/signup' }] // Show Sign Up on Sign In page
    : pathname === '/signup'
    ? [{ name: 'Sign In', href: '/signin' }] // Show Sign In on Sign Up page
    : [
        { name: 'Sign In', href: '/signin' },
        { name: 'Sign Up', href: '/signup' },
      ]; // Show both on other pages

  return (
    <nav
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        background:
          theme === 'light'
            ? 'rgba(250, 248, 245, 0.95)'
            : 'rgba(26, 18, 16, 0.95)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.15)' : 'rgba(160, 128, 96, 0.15)'),
        transition: 'background 0.3s ease',
      }}
    >
      <div
        className="container"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: '64px',
        }}
      >
        {/* Logo */}
        <Link
          href="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            textDecoration: 'none',
          }}
        >
          {/* Abstract Logo Icon */}
          <svg
            width="32"
            height="32"
            viewBox="0 0 32 32"
            fill="none"
          >
            <rect
              x="2"
              y="2"
              width="28"
              height="28"
              rx="6"
              fill="url(#logoGradient)"
            />
            <path
              d="M9 16L14 21L23 11"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <defs>
              <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8b5e3c" />
                <stop offset="100%" stopColor="#6b4423" />
              </linearGradient>
            </defs>
          </svg>
          <span
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '18px',
              fontWeight: 600,
              color: theme === 'light' ? '#2c1810' : '#f5ebe0',
              letterSpacing: '-0.02em',
            }}
          >
            ActionMind
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '24px',
          }}
          className="desktop-nav"
        >
          {/* Auth Links (only when not logged in) */}
          {!isLoggedIn && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {authLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  style={{
                    fontSize: '14px',
                    fontWeight: 500,
                    color:
                      pathname === link.href
                        ? '#8b5e3c'
                        : theme === 'light'
                        ? '#6b4c35'
                        : '#d4c4b0',
                    textDecoration: 'none',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    transition: 'all 0.15s ease',
                    background:
                      pathname === link.href
                        ? theme === 'light'
                          ? 'rgba(139, 94, 60, 0.1)'
                          : 'rgba(160, 128, 96, 0.2)'
                        : 'transparent',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = theme === 'light'
                      ? 'rgba(139, 94, 60, 0.08)'
                      : 'rgba(160, 128, 96, 0.15)';
                  }}
                  onMouseLeave={(e) => {
                    if (pathname !== link.href) {
                      e.currentTarget.style.background = 'transparent';
                    }
                  }}
                >
                  {link.name}
                </Link>
              ))}
            </div>
          )}

          {/* Divider (only when showing links or theme toggle) */}
          {(!isLoggedIn || authLinks.length > 0) && (
            <div
              style={{
                width: '1px',
                height: '20px',
                background: theme === 'light' ? 'rgba(196, 167, 125, 0.2)' : 'rgba(160, 128, 96, 0.3)',
              }}
            />
          )}

          {/* Actions */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
            }}
          >
            <ThemeToggle />
          </div>
        </div>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="mobile-menu-btn"
          style={{
            display: 'none',
            padding: '12px',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            color: theme === 'light' ? '#2c1810' : '#f5ebe0',
            borderRadius: '8px',
            transition: 'background 0.2s ease',
            minWidth: '44px',
            minHeight: '44px',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = theme === 'light'
              ? 'rgba(139, 94, 60, 0.08)'
              : 'rgba(160, 128, 96, 0.15)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'transparent';
          }}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            {isMenuOpen ? (
              <path d="M18 6L6 18M6 6l12 12" />
            ) : (
              <>
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </>
            )}
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div
          style={{
            display: 'none',
            padding: '16px',
            background: theme === 'light' ? '#faf8f5' : '#1a1210',
            borderBottom: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.15)' : 'rgba(160, 128, 96, 0.15)'),
          }}
          className="mobile-menu"
        >
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}
          >
            {!isLoggedIn && authLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsMenuOpen(false)}
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  color:
                    pathname === link.href
                      ? '#8b5e3c'
                      : theme === 'light'
                      ? '#6b4c35'
                      : '#d4c4b0',
                  background:
                    pathname === link.href
                      ? theme === 'light'
                        ? 'rgba(139, 94, 60, 0.1)'
                        : 'rgba(160, 128, 96, 0.2)'
                      : 'transparent',
                  fontSize: '14px',
                  fontWeight: 500,
                }}
              >
                {link.name}
              </Link>
            ))}

            <div style={{ height: '1px', margin: '8px 0', background: theme === 'light' ? 'rgba(196, 167, 125, 0.2)' : 'rgba(160, 128, 96, 0.3)' }} />

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 0',
              }}
            >
              <span
                style={{
                  fontSize: '14px',
                  color: theme === 'light' ? '#6b4c35' : '#d4c4b0',
                }}
              >
                Theme
              </span>
              <ThemeToggle />
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        @media (max-width: 768px) {
          .desktop-nav {
            display: none !important;
          }
          .mobile-menu-btn {
            display: block !important;
          }
          .mobile-menu {
            display: block !important;
          }
        }
      `}</style>
    </nav>
  );
}
