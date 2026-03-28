-- Migration: 001_create_tasks_conversations_messages.sql
-- Purpose: Create core tables for Todo AI Chatbot (Phase III)
-- Entities: Task, Conversation, Message
-- Database: Neon PostgreSQL (PostgreSQL 16+)

-- =====================================================
-- Task Entity
-- =====================================================
-- Stores user tasks with completion tracking
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,

    -- Task content
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Task status
    completed BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT tasks_title_not_empty CHECK (LENGTH(TRIM(title)) > 0)
);

-- Indexes for Task table
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Comments
COMMENT ON TABLE tasks IS 'User tasks created via AI chat interface';
COMMENT ON COLUMN tasks.user_id IS 'Foreign key reference to users table (from Better Auth)';
COMMENT ON COLUMN tasks.completed IS 'Task completion status (false=pending, true=completed)';

-- =====================================================
-- Conversation Entity
-- =====================================================
-- Stores chat conversations with UUID for security
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for Conversation table
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_created ON conversations(user_id, created_at DESC);

-- Comments
COMMENT ON TABLE conversations IS 'Chat sessions between user and AI assistant';
COMMENT ON COLUMN conversations.id IS 'UUID for security - prevents enumeration attacks';
COMMENT ON COLUMN conversations.user_id IS 'Foreign key reference to users table (from Better Auth)';

-- =====================================================
-- Message Entity
-- =====================================================
-- Stores individual messages within conversations
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    conversation_id UUID NOT NULL,
    user_id VARCHAR(255) NOT NULL,

    -- Message content
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,

    -- Tool calling support (for AI agent responses)
    tool_calls JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT messages_role_valid CHECK (role IN ('user', 'assistant', 'system')),
    CONSTRAINT messages_content_not_empty CHECK (LENGTH(TRIM(content)) > 0),
    CONSTRAINT messages_conversation_fkey FOREIGN KEY (conversation_id)
        REFERENCES conversations(id) ON DELETE CASCADE
);

-- Indexes for Message table
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_conv_created ON messages(conversation_id, created_at ASC);

-- Comments
COMMENT ON TABLE messages IS 'Individual messages in chat conversations';
COMMENT ON COLUMN messages.role IS 'Message role: user, assistant, or system';
COMMENT ON COLUMN messages.tool_calls IS 'JSONB array of MCP tool calls made by AI agent';

-- =====================================================
-- Trigger: Update updated_at timestamp
-- =====================================================
-- Automatic timestamp updates for tasks table
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- Validation Summary
-- =====================================================
-- Run these queries to verify migration success:

-- 1. Check table creation:
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public'
--   AND tablename IN ('tasks', 'conversations', 'messages');

-- 2. Check indexes:
-- SELECT indexname FROM pg_indexes WHERE schemaname = 'public'
--   AND tablename IN ('tasks', 'conversations', 'messages');

-- 3. Check constraints:
-- SELECT conname FROM pg_constraint WHERE conrelid::regclass IN ('tasks'::regclass, 'conversations'::regclass, 'messages'::regclass);

-- 4. Test UUID generation:
-- SELECT gen_random_uuid() AS test_uuid;

-- 5. Verify JSONB column:
-- SELECT column_name, data_type FROM information_schema.columns
--   WHERE table_name = 'messages' AND column_name = 'tool_calls';

-- =====================================================
-- Rollback (if needed)
-- =====================================================
-- To rollback this migration, run:
-- DROP TABLE IF EXISTS messages CASCADE;
-- DROP TABLE IF EXISTS conversations CASCADE;
-- DROP TABLE IF EXISTS tasks CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
