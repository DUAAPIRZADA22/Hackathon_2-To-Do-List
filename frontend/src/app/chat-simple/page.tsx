'use client';

/**
 * Simple Chat Page - No ChatKit Dependency
 *
 * Direct integration with /api/{user_id}/chat endpoint.
 * Plain UI that always works.
 */

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getCurrentUser, getToken } from '@/lib/auth';
import { Navigation, Sidebar } from '@/components';

export default function SimpleChatPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ username: string; id: number } | null>(null);
  const [mounted, setMounted] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    if (!isAuthenticated()) {
      router.push('/signin');
      return;
    }
    const currentUser = getCurrentUser();
    setUser(currentUser);
  }, [mounted, router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!mounted || !user) {
    return (
      <div className="loading-container">
        <span className="spinner" />
      </div>
    );
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const token = getToken();
      const response = await fetch(`http://localhost:8000/api/${user.id}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_id: null,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <Navigation />
      <Sidebar />
      <div className="chat-page">
        <div className="chat-header">
          <div className="header-content">
            <h1>ActionMind AI</h1>
            <p>AI-powered task management</p>
          </div>
        </div>

        <main className="chat-main">
          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="empty-state">
                <p>Start a conversation...</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="message assistant">
                <div className="message-content loading">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input-container">
            <textarea
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              rows={1}
              disabled={isLoading}
            />
            <button
              className="send-button"
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? '...' : 'Send'}
            </button>
          </div>
        </main>
      </div>

      <style jsx>{`
        .loading-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
        }

        .spinner {
          width: 48px;
          height: 48px;
          border: 3px solid #f3f3f3;
          border-top: 3px solid #8B5A2B;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .chat-page {
          min-height: 100vh;
          margin-left: 260px;
          display: flex;
          flex-direction: column;
          background: #f5f5f5;
        }

        .chat-header {
          background: linear-gradient(135deg, #8B5A2B 0%, #6B4423 100%);
          padding: 20px;
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }

        .header-content h1 {
          color: white;
          margin: 0;
          font-size: 24px;
          font-weight: 600;
        }

        .header-content p {
          color: rgba(255, 255, 255, 0.9);
          margin: 4px 0 0 0;
          font-size: 14px;
        }

        .chat-main {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .empty-state {
          text-align: center;
          color: #888;
          margin-top: 100px;
        }

        .message {
          display: flex;
          max-width: 70%;
        }

        .message.user {
          align-self: flex-end;
        }

        .message.assistant {
          align-self: flex-start;
        }

        .message-content {
          padding: 12px 16px;
          border-radius: 12px;
          white-space: pre-wrap;
          word-wrap: break-word;
        }

        .message.user .message-content {
          background: #8B5A2B;
          color: white;
        }

        .message.assistant .message-content {
          background: white;
          color: #333;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .message-content.loading {
          display: flex;
          gap: 4px;
          padding: 12px 20px;
        }

        .dot {
          width: 8px;
          height: 8px;
          background: #888;
          border-radius: 50%;
          animation: bounce 1.4s infinite ease-in-out;
        }

        .dot:nth-child(1) { animation-delay: 0s; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
          40% { transform: scale(1); opacity: 1; }
        }

        .chat-input-container {
          display: flex;
          gap: 10px;
          padding: 20px;
          background: white;
          border-top: 1px solid #e0e0e0;
        }

        .chat-input {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 15px;
          font-family: inherit;
          resize: none;
          outline: none;
          transition: border-color 0.2s;
        }

        .chat-input:focus {
          border-color: #8B5A2B;
        }

        .chat-input:disabled {
          background: #f5f5f5;
        }

        .send-button {
          padding: 12px 24px;
          background: #8B5A2B;
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }

        .send-button:hover:not(:disabled) {
          background: #6B4423;
        }

        .send-button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
          .chat-page {
            margin-left: 0;
          }

          .chat-header {
            padding: 16px;
          }

          .header-content h1 {
            font-size: 20px;
          }

          .message {
            max-width: 85%;
          }
        }

        /* Tablet responsive */
        @media (min-width: 769px) and (max-width: 1024px) {
          .chat-page {
            margin-left: 200px;
          }
        }
      `}</style>
    </>
  );
}
