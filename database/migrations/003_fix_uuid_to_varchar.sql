-- Migration: 003_fix_uuid_to_varchar.sql
-- Purpose: Fix type mismatch between database (UUID) and Python models (VARCHAR)
-- Issue: Python models use str type but database has UUID type
-- Solution: Change UUID columns to VARCHAR(36) to match Python models
-- Database: Neon PostgreSQL (PostgreSQL 16+)

-- =====================================================
-- Fix conversations table: Change id from UUID to VARCHAR(36)
-- =====================================================
-- Step 1: Drop and recreate the id column as VARCHAR
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_pkey;

-- Step 2: Change id column type to VARCHAR(36)
ALTER TABLE conversations ALTER COLUMN id TYPE VARCHAR(36) USING id::TEXT;

-- Step 3: Recreate primary key
ALTER TABLE conversations ADD PRIMARY KEY (id);

-- =====================================================
-- Fix messages table: Change conversation_id from UUID to VARCHAR(36)
-- =====================================================
-- Step 1: Drop foreign key constraint
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_conversation_id_fkey;

-- Step 2: Change conversation_id column type to VARCHAR(36)
ALTER TABLE messages ALTER COLUMN conversation_id TYPE VARCHAR(36) USING conversation_id::TEXT;

-- Step 3: Recreate foreign key constraint
ALTER TABLE messages ADD CONSTRAINT messages_conversation_id_fkey
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;

-- =====================================================
-- Verification
-- =====================================================
-- Run this to verify the columns were changed:
-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name IN ('conversations', 'messages')
--   AND column_name IN ('id', 'conversation_id')
-- ORDER BY table_name, column_name;

-- =====================================================
-- Rollback (if needed)
-- =====================================================
-- To rollback this migration, run:
-- ALTER TABLE messages DROP CONSTRAINT messages_conversation_id_fkey;
-- ALTER TABLE messages ALTER COLUMN conversation_id TYPE UUID USING conversation_id::UUID;
-- ALTER TABLE messages ADD CONSTRAINT messages_conversation_id_fkey
--     FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;
--
-- ALTER TABLE conversations DROP CONSTRAINT conversations_pkey;
-- ALTER TABLE conversations ALTER COLUMN id TYPE UUID USING id::UUID;
-- ALTER TABLE conversations ADD PRIMARY KEY (id);
