'use client';

/**
 * Chat Page - AI-powered task management (Phase III)
 * User Story 1: Natural Language Task Creation (MVP)
 * Fully responsive - mobile optimized
 */

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getCurrentUser } from '@/lib/auth';
import { sendChatMessage, streamChatMessage, getCurrentUserId } from '@/services/chat-api';
import { useToast } from '@/lib/toast';
import { Navigation, Sidebar } from '@/components';
import { useTheme } from '@/components/ThemeProvider';
import type { ChatRequest, SSEChunk, ToolCall } from '@/services/chat-api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  tool_calls?: ToolCall[];
}

// Quick reply options for task creation
const PRIORITY_OPTIONS = ['Low', 'Medium', 'High', 'Urgent'];
const STATUS_OPTIONS = ['To Do', 'In Progress', 'Done'];

export default function ChatPage() {
  const router = useRouter();
  const { showToast } = useToast();
  const { theme } = useTheme();
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/signin');
      return;
    }
    const currentUser = getCurrentUser();
    setUser(currentUser);
    const currentUserId = getCurrentUserId();
    setUserId(currentUserId);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Detect if AI is asking for priority or status (PRIORITY FIRST)
  const detectQuestionType = (content: string): 'priority' | 'status' | null => {
    const lower = content.toLowerCase();

    // Priority detection - must come first in flow
    if (
      (lower.includes('priority') || lower.includes('Priority')) &&
      (lower.includes('what') || lower.includes('select') || lower.includes('choose'))
    ) {
      return 'priority';
    }

    // Status detection - only if priority question NOT detected
    if (
      (lower.includes('status') || lower.includes('Status')) &&
      (lower.includes('what') || lower.includes('select') || lower.includes('choose'))
    ) {
      return 'status';
    }

    return null;
  };

  const handleQuickReply = (value: string) => {
    setInputValue(value);
    setTimeout(() => handleSendMessage(), 100);
  };

  const handleSendMessage = async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || !userId || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: trimmedInput,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Use streaming for better UX
      const eventSource = streamChatMessage(
        userId,
        {
          message: trimmedInput,
          conversation_id: conversationId,
        },
        // onChunk
        (chunk: SSEChunk) => {
          if (chunk.type === 'token' && chunk.content) {
            setMessages((prev) => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.role === 'assistant' && lastMessage.id === 'streaming') {
                // Update existing streaming message
                return [
                  ...prev.slice(0, -1),
                  {
                    ...lastMessage,
                    content: lastMessage.content + (chunk.content || ''),
                  },
                ];
              } else {
                // Create new streaming message
                return [
                  ...prev,
                  {
                    id: 'streaming',
                    role: 'assistant',
                    content: chunk.content || '',
                    timestamp: new Date(),
                  },
                ];
              }
            });
          }
        },
        // onDone
        (response) => {
          setConversationId(response.conversation_id);
          setMessages((prev) => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.role === 'assistant' && lastMessage.id === 'streaming') {
              // Replace streaming message with final message
              return [
                ...prev.slice(0, -1),
                {
                  id: Date.now().toString(),
                  role: 'assistant',
                  content: response.response,
                  timestamp: new Date(),
                  tool_calls: response.tool_calls,
                },
              ];
            }
            return prev;
          });
          setIsLoading(false);
        },
        // onError
        (error) => {
          showToast(error.message || 'Failed to send message', 'error');
          setMessages((prev) => {
            // Remove the streaming message if exists
            const filtered = prev.filter((m) => m.id !== 'streaming');
            // Add error message
            return [
              ...filtered,
              {
                id: Date.now().toString(),
                role: 'assistant',
                content: "Sorry, I encountered an error. Please try again.",
                timestamp: new Date(),
              },
            ];
          });
          setIsLoading(false);
        }
      );
    } catch (error: any) {
      showToast(error.message || 'Failed to send message', 'error');
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!user) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <span className="spinner" style={{ width: 48, height: 48, borderWidth: 3 }} />
      </div>
    );
  }

  return (
    <>
      <Navigation />
      <Sidebar />
      <div className="chat-content" style={{ minHeight: '100vh', background: 'var(--bg-primary)', marginLeft: '260px' }}>
        {/* Header */}
        <div className="chat-header">
          <div className="container" style={{ maxWidth: '100%' }}>
            <div className="chat-header-content">
              <div className="chat-header-text">
                <h1 className="chat-title">ActionMind AI</h1>
                <p className="chat-subtitle">
                  AI-powered task management • {messages.length} {messages.length === 1 ? 'message' : 'messages'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Chat Main */}
        <main className="container chat-main" style={{ maxWidth: '900px', margin: '0 auto', padding: 'var(--space-8) var(--space-4)', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 200px)' }}>
          {/* Messages Container */}
          <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-4)', background: 'var(--bg-card)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--border-subtle)' }}>
            {messages.length === 0 ? (
              <div className="chat-empty-state">
                <svg
                  width={80}
                  height={80}
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.5}
                  className="chat-empty-icon"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  <path d="M8 10h.01" />
                  <path d="M12 10h.01" />
                  <path d="M16 10h.01" />
                </svg>
                <h3 className="chat-empty-title">Start a conversation</h3>
                <p className="chat-empty-text">
                  Try saying things like:
                </p>
                <ul className="chat-empty-examples">
                  <li>"Add a task to buy groceries"</li>
                  <li>"Remember to call mom on Saturday"</li>
                  <li>"Create a task for the meeting tomorrow"</li>
                </ul>
              </div>
            ) : (
              messages.map((message) => {
                const questionType = message.role === 'assistant' ? detectQuestionType(message.content) : null;

                return (
                <div
                  key={message.id}
                  className={`chat-message ${message.role === 'user' ? 'chat-message-user' : 'chat-message-assistant'}`}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: message.role === 'user' ? 'flex-end' : 'flex-start',
                    marginBottom: 'var(--space-4)',
                  }}
                >
                  <div
                    className="chat-message-bubble"
                    style={{
                      maxWidth: '80%',
                      padding: 'var(--space-4) var(--space-5)',
                      borderRadius: 'var(--radius-lg)',
                      background: message.role === 'user'
                        ? (theme === 'light' ? '#5c3d2e' : '#2c1810')
                        : 'var(--bg-secondary)',
                      color: message.role === 'user' ? '#ffffff' : 'var(--text-primary)',
                      boxShadow: theme === 'light' && message.role === 'user' ? '0 2px 12px rgba(92, 61, 46, 0.3)' : '0 2px 8px rgba(0,0,0,0.15)',
                    }}
                  >
                    {/* Parse and format task lists from content */}
                    {message.role === 'assistant' && message.content.includes('Title:') ? (
                      <div className="chat-message-content">
                        {message.content.split('\n\n').map((section, idx) => {
                          // Check if this section contains task listings
                          if (section.includes('Title:') && section.includes('Status:')) {
                            return (
                              <div key={idx}>
                                <p style={{ margin: '0 0 var(--space-2) 0', lineHeight: 1.6, fontWeight: 500, fontSize: '15px' }}>
                                  {section.includes('Here is your task list') ? 'Here is your task list:' : ''}
                                </p>
                                <ul className="chat-tasks-list">
                                  {section.split('•').filter(line => line.trim()).map((taskLine, taskIdx) => {
                                    // Parse task info from line like "Title: nn Status: To Do Completed: No"
                                    const titleMatch = taskLine.match(/Title:\s*([^\s]+)/);
                                    const statusMatch = taskLine.match(/Status:\s*([^\s]+)/);
                                    const title = titleMatch ? titleMatch[1] : 'Task';
                                    const status = statusMatch ? statusMatch[1] : '';

                                    return (
                                      <li key={taskIdx} className="chat-task-item">
                                        <span className="chat-task-bullet">•</span>
                                        <span className="chat-task-title">{title}</span>
                                        {status && (
                                          <span className="chat-task-priority">
                                            [{status === 'Done' ? '✓' : status}]
                                          </span>
                                        )}
                                      </li>
                                    );
                                  })}
                                </ul>
                              </div>
                            );
                          }
                          return (
                            <p key={idx} style={{ margin: idx === 0 ? '0 0 var(--space-2) 0' : 'var(--space-2) 0 0 0', lineHeight: 1.6, fontWeight: 500, fontSize: '15px' }}>
                              {section}
                            </p>
                          );
                        })}
                      </div>
                    ) : (
                      <p style={{ margin: 0, lineHeight: 1.6, fontWeight: 500, fontSize: '15px' }}>{message.content}</p>
                    )}

                    {message.tool_calls && message.tool_calls.length > 0 && (
                      <div className="chat-tool-calls" style={{ marginTop: 'var(--space-3)', paddingTop: 'var(--space-3)', borderTop: message.role === 'user' ? '1px solid rgba(255,255,255,0.3)' : '1px solid var(--border-subtle)' }}>
                        <small style={{ opacity: 0.95, fontSize: 'var(--text-xs)' }}>
                          ✓ Used {message.tool_calls.length === 1 ? 'tool' : 'tools'}: {message.tool_calls.map(t => t.tool).join(', ')}
                        </small>
                      </div>
                    )}
                  </div>

                  {/* Quick Reply Buttons for Priority/Status */}
                  {questionType && (
                    <div style={{ marginTop: 'var(--space-2)', display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)', maxWidth: '80%' }}>
                      {(questionType === 'priority' ? PRIORITY_OPTIONS : STATUS_OPTIONS).map((option) => (
                        <button
                          key={option}
                          onClick={() => handleQuickReply(option)}
                          disabled={isLoading}
                          className="quick-reply-btn"
                          style={{
                            padding: 'var(--space-2) var(--space-4)',
                            borderRadius: 'var(--radius-md)',
                            background: 'var(--bg-card)',
                            border: '1px solid var(--accent-primary)',
                            color: 'var(--accent-primary)',
                            fontSize: 'var(--text-sm)',
                            fontWeight: 600,
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            opacity: isLoading ? 0.6 : 1,
                            transition: 'all 0.2s ease',
                          }}
                          onMouseEnter={(e) => {
                            if (!isLoading) {
                              e.currentTarget.style.background = 'var(--accent-primary)';
                              e.currentTarget.style.color = 'white';
                            }
                          }}
                          onMouseLeave={(e) => {
                            if (!isLoading) {
                              e.currentTarget.style.background = 'var(--bg-card)';
                              e.currentTarget.style.color = 'var(--accent-primary)';
                            }
                          }}
                        >
                          {option}
                        </button>
                      ))}
                    </div>
                  )}

                  <span className="chat-message-time" style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginTop: 'var(--space-1)' }}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                );
              })
            )}

            {isLoading && (
              <div className="chat-message chat-message-assistant" style={{ alignItems: 'flex-start', marginBottom: 'var(--space-4)' }}>
                <div
                  className="chat-message-bubble chat-message-loading"
                  style={{
                    padding: 'var(--space-4) var(--space-5)',
                    borderRadius: 'var(--radius-lg)',
                    background: 'var(--bg-secondary)',
                  }}
                >
                  <div className="chat-typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="chat-input-container" style={{ marginTop: 'var(--space-4)', display: 'flex', gap: 'var(--space-3)', alignItems: 'flex-end' }}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type a message... (e.g., Add a task to buy groceries)"
              disabled={isLoading}
              className="chat-input"
              style={{
                flex: 1,
                padding: 'var(--space-4) var(--space-5)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--border-subtle)',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: 'var(--text-base)',
              }}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="btn chat-send-btn"
              style={{
                padding: 'var(--space-4) var(--space-6)',
                borderRadius: 'var(--radius-lg)',
                background: isLoading || !inputValue.trim() ? 'var(--text-muted)' : 'var(--accent-primary)',
                color: 'white',
                fontWeight: 600,
                minWidth: '80px',
              }}
            >
              {isLoading ? (
                <span className="spinner chat-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
              ) : (
                <>
                  Send
                  <svg width={16} height={16} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} style={{ marginLeft: 'var(--space-2)', verticalAlign: 'text-bottom' }}>
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </main>
      </div>

      {/* Inline Styles */}
      <style jsx>{`
        .chat-header {
          background: linear-gradient(135deg, var(--coffee-latte) 0%, var(--accent-primary) 100%);
          padding: var(--space-8) var(--space-4);
        }

        .chat-header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .chat-header-text h1 {
          color: white;
          margin-bottom: var(--space-2);
          font-size: var(--text-3xl);
        }

        .chat-subtitle {
          color: rgba(255, 255, 255, 0.9);
          margin: 0;
        }

        .chat-empty-state {
          text-align: center;
          padding: var(--space-16);
          color: var(--text-muted);
        }

        .chat-empty-icon {
          margin: 0 auto var(--space-6);
          opacity: 0.4;
        }

        .chat-empty-title {
          font-size: var(--text-lg);
          margin-bottom: var(--space-2);
          color: var(--text-secondary);
        }

        .chat-empty-text {
          margin-bottom: var(--space-4);
        }

        .chat-empty-examples {
          list-style: none;
          padding: 0;
          text-align: left;
          max-width: 400px;
          margin: '0 auto';
        }

        .chat-empty-examples li {
          padding: 'var(--space-2) var(--space-3)',
          background: 'var(--bg-secondary)',
          borderRadius: 'var(--radius-md)',
          margin-bottom: 'var(--space-2)',
          font-size: 'var(--text-sm)',
          color: 'var(--text-secondary)';
        }

        .chat-typing-indicator {
          display: flex;
          gap: 4px;
        }

        .chat-typing-indicator span {
          width: 8px;
          height: 8px;
          borderRadius: '50%';
          background: 'var(--text-muted)';
          animation: typing 1.4s infinite ease-in-out both;
        }

        .chat-typing-indicator span:nth-child(1) {
          animation-delay: 0s;
        }

        .chat-typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .chat-typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.4;
          }
          30% {
            transform: translateY(-10px);
            opacity: 1;
          }
        }

        .chat-spinner {
          display: inline-block;
          vertical-align: middle;
        }

        /* Mobile Responsive - Improved */
        @media (max-width: 767px) {
          .chat-content {
            margin-left: 0 !important;
            width: 100% !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            padding-bottom: 80px !important; /* Space for input */
          }

          .chat-header {
            padding: var(--space-4) var(--space-3) !important;
          }

          .chat-title {
            font-size: var(--text-xl) !important;
          }

          .chat-subtitle {
            font-size: var(--text-sm) !important;
          }

          .chat-main {
            padding: var(--space-3) !important;
            height: calc(100vh - 140px) !important;
          }

          .chat-messages {
            padding: var(--space-3) !important;
            border-radius: var(--radius-lg) !important;
          }

          .chat-message-bubble {
            max-width: 90% !important;
            padding: var(--space-3) var(--space-4) !important;
            font-size: var(--text-sm) !important;
          }

          .quick-reply-btn {
            padding: var(--space-2) var(--space-3) !important;
            font-size: var(--text-xs) !important;
            flex: 1 1 calc(50% - var(--space-2)) !important;
            min-width: calc(50% - var(--space-2)) !important;
          }

          .chat-input-container {
            flex-direction: row !important;
            gap: var(--space-2) !important;
          }

          .chat-input {
            font-size: 16px !important; /* Prevent iOS zoom */
            padding: var(--space-3) var(--space-4) !important;
          }

          .chat-send-btn {
            padding: var(--space-3) var(--space-4) !important;
            min-width: 70px !important;
            font-size: var(--text-sm) !important;
          }

          .chat-empty-state {
            padding: var(--space-8) var(--space-4) !important;
          }

          .chat-empty-examples {
            max-width: 100% !important;
          }

          .chat-empty-examples li {
            font-size: var(--text-xs) !important;
            padding: var(--space-2) !important;
          }

          .chat-message-time {
            font-size: 10px !important;
          }

          .chat-tasks-list {
            font-size: var(--text-xs) !important;
          }

          .chat-task-item {
            font-size: var(--text-xs) !important;
          }

          .chat-task-title {
            font-size: var(--text-xs) !important;
          }

          .chat-task-priority {
            font-size: 10px !important;
          }

          .chat-task-desc {
            font-size: var(--text-xs) !important;
          }
        }

        /* Tablet Responsive */
        @media (min-width: 768px) and (max-width: 1023px) {
          .chat-content {
            padding-bottom: 40px;
          }

          .chat-main {
            padding: var(--space-4) var(--space-5) !important;
          }
        }

        /* Chat Tasks List - Simple Bulleted List */
        .chat-tasks-list {
          list-style: none;
          margin: var(--space-3) 0 0 0;
          padding: 0;
        }

        .chat-task-item {
          display: flex;
          align-items: flex-start;
          gap: var(--space-2);
          padding: var(--space-1) 0;
          font-size: var(--text-sm);
          line-height: 1.5;
          color: var(--text-primary);
        }

        .chat-task-bullet {
          color: var(--accent-primary);
          font-weight: bold;
          flex-shrink: 0;
        }

        .chat-task-title {
          font-weight: 500;
        }

        .chat-task-priority {
          font-size: 11px;
          font-weight: 600;
          color: var(--accent-primary);
          margin-left: var(--space-1);
        }

        .chat-task-desc {
          color: var(--text-secondary);
          font-size: var(--text-sm);
          font-weight: 400;
        }
      `}</style>
    </>
  );
}
