'use client';

/**
 * Sidebar Component - Only shown on dashboard/settings when logged in
 * Left sidebar with navigation and user info
 * Mobile: Overlay drawer with backdrop
 */

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useTheme } from './ThemeProvider';
import { signOut, getCurrentUser } from '@/lib/auth';
import { useState, useEffect } from 'react';

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { theme } = useTheme();
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    setUser(getCurrentUser());

    // Check if mobile on mount and resize
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
      if (window.innerWidth < 1024) {
        setIsCollapsed(false);
        setIsMobileOpen(false);
      }
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleSignOut = async () => {
    await signOut();
    router.push('/');
  };

  const menuItems = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Tasks', href: '/tasks', icon: '✅' },
    { name: 'Settings', href: '/settings', icon: '⚙️' },
  ];

  // Mobile sidebar: overlay
  // Desktop sidebar: fixed on left
  if (isMobile) {
    return (
      <>
        {/* Mobile Toggle Button */}
        <button
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          style={{
            position: 'fixed',
            bottom: '20px',
            left: '20px',
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #8b5e3c 0%, #6b4423 100%)',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            boxShadow: '0 4px 12px rgba(107, 68, 35, 0.4)',
            transition: 'transform 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.1)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
            {isMobileOpen ? (
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

        {/* Backdrop */}
        {isMobileOpen && (
          <div
            onClick={() => setIsMobileOpen(false)}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.5)',
              zIndex: 999,
              animation: 'fadeIn 0.2s ease',
            }}
          />
        )}

        {/* Mobile Sidebar */}
        <aside
          style={{
            position: 'fixed',
            left: 0,
            top: 0,
            height: '100vh',
            width: '280px',
            background: theme === 'light' ? '#faf8f5' : '#1a1210',
            borderRight: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.15)' : 'rgba(160, 128, 96, 0.15)'),
            zIndex: 1000,
            display: 'flex',
            flexDirection: 'column',
            transform: isMobileOpen ? 'translateX(0)' : 'translateX(-100%)',
            transition: 'transform 0.3s ease',
          }}
        >
          {/* Close Header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '20px 16px',
              borderBottom: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.15)' : 'rgba(160, 128, 96, 0.15)'),
            }}
          >
            <span
              style={{
                fontSize: '18px',
                fontWeight: 600,
                color: theme === 'light' ? '#2c1810' : '#f5ebe0',
              }}
            >
              Menu
            </span>
            <button
              onClick={() => setIsMobileOpen(false)}
              style={{
                padding: '8px',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                color: theme === 'light' ? '#6b4c35' : '#d4c4b0',
                borderRadius: '8px',
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Navigation */}
          <nav style={{ flex: 1, padding: '16px', overflowY: 'auto' }}>
            <ul
              style={{
                listStyle: 'none',
                margin: 0,
                padding: 0,
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              {menuItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={() => setIsMobileOpen(false)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '14px 16px',
                        borderRadius: '12px',
                        textDecoration: 'none',
                        color: isActive
                          ? '#f5ebe0'
                          : theme === 'light'
                          ? '#6b4c35'
                          : '#d4c4b0',
                        background: isActive
                          ? 'linear-gradient(135deg, #8b5e3c 0%, #6b4423 100%)'
                          : 'transparent',
                        transition: 'all 0.15s ease',
                        fontSize: '16px',
                        fontWeight: isActive ? 600 : 500,
                      }}
                    >
                      <span style={{ fontSize: '20px' }}>{item.icon}</span>
                      <span>{item.name}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          {/* User Section */}
          <div
            style={{
              padding: '16px',
              borderTop: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.15)' : 'rgba(160, 128, 96, 0.15)'),
            }}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '12px',
              }}
            >
              <div
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #8b5e3c 0%, #6b4423 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '16px',
                  fontWeight: 600,
                }}
              >
                {user?.username?.charAt(0)?.toUpperCase() || 'U'}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p
                  style={{
                    margin: 0,
                    fontSize: '15px',
                    fontWeight: 500,
                    color: theme === 'light' ? '#2c1810' : '#f5ebe0',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {user?.username || 'User'}
                </p>
              </div>
            </div>
            <button
              onClick={handleSignOut}
              style={{
                width: '100%',
                padding: '12px 16px',
                background: 'transparent',
                border: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.3)' : 'rgba(160, 128, 96, 0.3)'),
                borderRadius: '10px',
                cursor: 'pointer',
                color: theme === 'light' ? '#6b4c35' : '#d4c4b0',
                fontSize: '15px',
                fontWeight: 500,
                transition: 'all 0.15s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
              Sign Out
            </button>
          </div>
        </aside>
      </>
    );
  }

  // Desktop sidebar
  return (
    <aside
      style={{
        position: 'fixed',
        left: 0,
        top: '64px',
        height: 'calc(100vh - 64px)',
        width: isCollapsed ? '80px' : '260px',
        background: theme === 'light' ? '#faf8f5' : '#1a1210',
        borderRight: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.15)' : 'rgba(160, 128, 96, 0.15)'),
        transition: 'width 0.3s ease',
        zIndex: 90,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Collapse Toggle */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        style={{
          position: 'absolute',
          top: '12px',
          right: '-12px',
          width: '24px',
          height: '24px',
          borderRadius: '50%',
          background: theme === 'light' ? '#fff' : '#2a2420',
          border: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.3)' : 'rgba(160, 128, 96, 0.3)'),
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          color: theme === 'light' ? '#6b4c35' : '#d4c4b0',
          transition: 'all 0.2s ease',
          zIndex: 100,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
        }}
        title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        {isCollapsed ? '→' : '←'}
      </button>

      {/* Navigation */}
      <nav
        style={{
          flex: 1,
          padding: isCollapsed ? '20px 12px' : '20px 16px',
          overflowY: 'auto',
        }}
      >
        <ul
          style={{
            listStyle: 'none',
            margin: 0,
            padding: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: '8px',
          }}
        >
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: isCollapsed ? '0' : '12px',
                    padding: isCollapsed ? '12px' : '12px 16px',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    color: isActive
                      ? '#f5ebe0'
                      : theme === 'light'
                      ? '#6b4c35'
                      : '#d4c4b0',
                    background: isActive
                      ? 'linear-gradient(135deg, #8b5e3c 0%, #6b4423 100%)'
                      : 'transparent',
                    transition: 'all 0.15s ease',
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                    fontSize: '14px',
                    fontWeight: isActive ? 600 : 500,
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background =
                        theme === 'light'
                          ? 'rgba(139, 94, 60, 0.08)'
                          : 'rgba(160, 128, 96, 0.15)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = 'transparent';
                    }
                  }}
                  title={isCollapsed ? item.name : ''}
                >
                  <span style={{ fontSize: '18px' }}>{item.icon}</span>
                  {!isCollapsed && <span>{item.name}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User Section */}
      {!isCollapsed && (
        <div
          style={{
            padding: '16px',
            borderTop: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.15)' : 'rgba(160, 128, 96, 0.15)'),
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '12px',
            }}
          >
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #8b5e3c 0%, #6b4423 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '14px',
                fontWeight: 600,
              }}
            >
              {user?.username?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div
              style={{
                flex: 1,
                minWidth: 0,
              }}
            >
              <p
                style={{
                  margin: 0,
                  fontSize: '14px',
                  fontWeight: 500,
                  color: theme === 'light' ? '#2c1810' : '#f5ebe0',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}
              >
                {user?.username || 'User'}
              </p>
            </div>
          </div>
          <button
            onClick={handleSignOut}
            style={{
              width: '100%',
              padding: '10px 16px',
              background: 'transparent',
              border: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.3)' : 'rgba(160, 128, 96, 0.3)'),
              borderRadius: '8px',
              cursor: 'pointer',
              color: theme === 'light' ? '#6b4c35' : '#d4c4b0',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.15s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background =
                theme === 'light'
                  ? 'rgba(107, 68, 35, 0.08)'
                  : 'rgba(212, 196, 176, 0.1)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            Sign Out
          </button>
        </div>
      )}

      {/* Collapsed User Avatar (just shows avatar) */}
      {isCollapsed && (
        <div
          style={{
            padding: '16px 12px',
            borderTop: '1px solid ' + (theme === 'light' ? 'rgba(196, 167, 125, 0.15)' : 'rgba(160, 128, 96, 0.15)'),
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #8b5e3c 0%, #6b4423 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
            onClick={handleSignOut}
            title={`${user?.username || 'User'} - Click to sign out`}
          >
            {user?.username?.charAt(0)?.toUpperCase() || 'U'}
          </div>
        </div>
      )}
    </aside>
  );
}
