'use client';

/**
 * Settings Page - Coffee Theme
 * User profile and application preferences
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getCurrentUser, signOut } from '@/lib/auth';
import { useToast } from '@/lib/toast';
import { Navigation, Sidebar, ThemeToggle } from '@/components';

export default function SettingsPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const [user, setUser] = useState<{ username: string; email: string } | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'security' | 'preferences'>('profile');

  const [profileForm, setProfileForm] = useState({
    username: '',
    email: '',
  });

  const [passwordForm, setPasswordForm] = useState({
    current: '',
    new: '',
    confirm: '',
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/signin');
      return;
    }
    const currentUser = getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
      setProfileForm({
        username: currentUser.username,
        email: currentUser.email || '',
      });
    }
  }, []);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    // Simulate API call
    setTimeout(() => {
      showToast('Profile updated successfully!', 'success');
      setIsSaving(false);
    }, 1000);
  };

  const handlePasswordSave = async (e: React.FormEvent) => {
    e.preventDefault();

    if (passwordForm.new !== passwordForm.confirm) {
      showToast('Passwords do not match', 'error');
      return;
    }

    if (passwordForm.new.length < 6) {
      showToast('Password must be at least 6 characters', 'error');
      return;
    }

    setIsSaving(true);

    // Simulate API call
    setTimeout(() => {
      showToast('Password updated successfully!', 'success');
      setPasswordForm({ current: '', new: '', confirm: '' });
      setIsSaving(false);
    }, 1000);
  };

  const handleSignOut = async () => {
    await signOut();
  };

  return (
    <>
      <Navigation />
      <Sidebar />
      <div className="settings-content" style={{ minHeight: '100vh', background: 'var(--bg-primary)', marginLeft: '260px' }}>
        {/* Settings Header */}
        <div
          style={{
            background:
              'linear-gradient(135deg, var(--coffee-latte) 0%, var(--accent-primary) 100%)',
            padding: 'var(--space-8) var(--space-4)',
            textAlign: 'center',
            color: 'white',
          }}
        >
          <div className="container" style={{ maxWidth: '100%' }}>
            <h1 style={{ color: 'white', marginBottom: 'var(--space-2)', fontSize: 'var(--text-3xl)' }}>Settings</h1>
            <p style={{ color: 'rgba(255,255,255,0.9)', marginBottom: 0, fontSize: 'var(--text-base)' }}>
              Customize your ActionMind AI experience
            </p>
          </div>
        </div>

        {/* Main Content */}
        <main className="container" style={{ maxWidth: '1100px', margin: '0 auto', padding: 'var(--space-8) var(--space-4)' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(220px, 280px) minmax(0, 1fr)',
              gap: 'var(--space-10)',
              alignItems: 'start',
            }}
          >
            {/* Sidebar */}
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: 'var(--space-2)',
              }}
            >
              {(
                [
                  { id: 'profile', label: 'Profile', icon: 'user' },
                  { id: 'security', label: 'Security', icon: 'lock' },
                  { id: 'preferences', label: 'Preferences', icon: 'settings' },
                ] as const
              ).map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className="btn-ghost"
                  style={{
                    width: '100%',
                    justifyContent: 'flex-start',
                    padding: 'var(--space-4)',
                    borderRadius: 'var(--radius-lg)',
                    background: activeTab === tab.id ? 'var(--accent-light)' : 'transparent',
                    color:
                      activeTab === tab.id ? 'var(--accent-primary)' : 'var(--text-secondary)',
                    fontWeight: activeTab === tab.id ? 600 : 500,
                    textAlign: 'left',
                  }}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Content */}
            <div>
              {activeTab === 'profile' && (
                <div className="card card-elevated">
                  <h2 style={{ marginBottom: 'var(--space-6)' }}>Profile Settings</h2>

                  {/* Avatar Section */}
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 'var(--space-6)',
                      marginBottom: 'var(--space-8)',
                      paddingBottom: 'var(--space-8)',
                      borderBottom: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div
                      style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '50%',
                        background:
                          'linear-gradient(135deg, var(--accent-primary) 0%, var(--coffee-mocha) 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: 'var(--text-2xl)',
                        fontWeight: 700,
                      }}
                    >
                      {user?.username?.charAt(0)?.toUpperCase() || '?'}
                    </div>
                    <div>
                      <h3 style={{ marginBottom: 'var(--space-1)' }}>{user?.username || 'User'}</h3>
                      <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: 'var(--text-sm)' }}>
                        {user?.email}
                      </p>
                    </div>
                  </div>

                  <form onSubmit={handleProfileSave} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
                    <div>
                      <label
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
                        type="text"
                        value={profileForm.username}
                        onChange={(e) => setProfileForm({ ...profileForm, username: e.target.value })}
                        className="input"
                        disabled={isSaving}
                      />
                    </div>

                    <div>
                      <label
                        style={{
                          display: 'block',
                          fontSize: 'var(--text-sm)',
                          fontWeight: 500,
                          marginBottom: 'var(--space-2)',
                          color: 'var(--text-primary)',
                        }}
                      >
                        Email
                      </label>
                      <input
                        type="email"
                        value={profileForm.email}
                        onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                        className="input"
                        disabled={isSaving}
                      />
                    </div>

                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={isSaving}
                      style={{ marginTop: 'var(--space-2)' }}
                    >
                      {isSaving ? (
                        <>
                          <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                          Saving...
                        </>
                      ) : (
                        'Save Changes'
                      )}
                    </button>
                  </form>
                </div>
              )}

              {activeTab === 'security' && (
                <div className="card card-elevated">
                  <h2 style={{ marginBottom: 'var(--space-6)' }}>Security Settings</h2>

                  <form onSubmit={handlePasswordSave} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-5)' }}>
                    <div>
                      <label
                        style={{
                          display: 'block',
                          fontSize: 'var(--text-sm)',
                          fontWeight: 500,
                          marginBottom: 'var(--space-2)',
                          color: 'var(--text-primary)',
                        }}
                      >
                        Current Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.current}
                        onChange={(e) =>
                          setPasswordForm({ ...passwordForm, current: e.target.value })
                        }
                        className="input"
                        required
                        disabled={isSaving}
                      />
                    </div>

                    <div>
                      <label
                        style={{
                          display: 'block',
                          fontSize: 'var(--text-sm)',
                          fontWeight: 500,
                          marginBottom: 'var(--space-2)',
                          color: 'var(--text-primary)',
                        }}
                      >
                        New Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.new}
                        onChange={(e) => setPasswordForm({ ...passwordForm, new: e.target.value })}
                        className="input"
                        required
                        minLength={6}
                        disabled={isSaving}
                      />
                      <p style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 'var(--space-1)' }}>
                        Must be at least 6 characters
                      </p>
                    </div>

                    <div>
                      <label
                        style={{
                          display: 'block',
                          fontSize: 'var(--text-sm)',
                          fontWeight: 500,
                          marginBottom: 'var(--space-2)',
                          color: 'var(--text-primary)',
                        }}
                      >
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        value={passwordForm.confirm}
                        onChange={(e) =>
                          setPasswordForm({ ...passwordForm, confirm: e.target.value })
                        }
                        className="input"
                        required
                        minLength={6}
                        disabled={isSaving}
                      />
                    </div>

                    <button
                      type="submit"
                      className="btn btn-primary"
                      disabled={isSaving}
                      style={{ marginTop: 'var(--space-2)' }}
                    >
                      {isSaving ? (
                        <>
                          <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                          Updating...
                        </>
                      ) : (
                        'Update Password'
                      )}
                    </button>
                  </form>

                  {/* Danger Zone */}
                  <div
                    style={{
                      marginTop: 'var(--space-8)',
                      paddingTop: 'var(--space-8)',
                      borderTop: '1px solid var(--border-subtle)',
                    }}
                  >
                    <h3 style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-4)', color: 'var(--danger)' }}>
                      Danger Zone
                    </h3>
                    <button onClick={handleSignOut} className="btn btn-ghost" style={{ color: 'var(--danger)' }}>
                      Sign Out
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'preferences' && (
                <div className="card card-elevated">
                  <h2 style={{ marginBottom: 'var(--space-6)' }}>App Preferences</h2>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
                    {/* Theme */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        paddingBottom: 'var(--space-6)',
                        borderBottom: '1px solid var(--border-subtle)',
                      }}
                    >
                      <div>
                        <h3 style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-1)' }}>
                          Theme
                        </h3>
                        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>
                          Choose between light and dark mode
                        </p>
                      </div>
                      <ThemeToggle />
                    </div>

                    {/* Notifications */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        paddingBottom: 'var(--space-6)',
                        borderBottom: '1px solid var(--border-subtle)',
                      }}
                    >
                      <div>
                        <h3 style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-1)' }}>
                          Email Notifications
                        </h3>
                        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>
                          Receive task reminders via email
                        </p>
                      </div>
                      <label style={{ position: 'relative', display: 'inline-block', width: 48, height: 24 }}>
                        <input type="checkbox" defaultChecked style={{ opacity: 0, width: 0, height: 0 }} />
                        <span
                          style={{
                            position: 'absolute',
                            cursor: 'pointer',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            backgroundColor: 'var(--accent-primary)',
                            transition: 'var(--transition-base)',
                            borderRadius: 'var(--radius-full)',
                          }}
                        >
                          <span
                            style={{
                              position: 'absolute',
                              content: '""',
                              height: 18,
                              width: 18,
                              left: 3,
                              bottom: 3,
                              backgroundColor: 'white',
                              transition: 'var(--transition-base)',
                              borderRadius: '50%',
                            }}
                          />
                        </span>
                      </label>
                    </div>

                    {/* Language */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <h3 style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-1)' }}>
                          Language
                        </h3>
                        <p style={{ margin: 0, fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>
                          Select your preferred language
                        </p>
                      </div>
                      <select className="select" style={{ width: 'auto' }}>
                        <option value="en">English</option>
                        <option value="es">Español</option>
                        <option value="fr">Français</option>
                        <option value="de">Deutsch</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>

      {/* Responsive CSS for mobile */}
      <style jsx>{`
        @media (max-width: 767px) {
          .settings-content {
            marginLeft: 0 !important;
          }
        }

        @media (max-width: 639px) {
          .settings-content {
            marginLeft: 0 !important;
          }

          main {
            padding: var(--space-6) var(--space-4) !important;
          }

          main > .container {
            gridTemplateColumns: 1fr !important;
            gap: var(--space-6) !important;
          }

          .card {
            padding: var(--space-5) !important;
          }

          h1 {
            fontSize: var(--text-2xl) !important;
          }

          input,
          select,
          textarea {
            fontSize: 16px !important;
          }

          button[type='submit'] {
            fontSize: var(--text-base) !important;
            minHeight: 48px !important;
          }
        }

        @media (min-width: 640px) and (max-width: 767px) {
          main > .container {
            gridTemplateColumns: 1fr !important;
          }
        }

        @media (min-width: 768px) and (max-width: 1023px) {
          main > .container {
            gridTemplateColumns: minmax(200px, 240px) minmax(0, 1fr) !important;
            gap: var(--space-6) !important;
          }
        }
      `}</style>
    </>
  );
}
