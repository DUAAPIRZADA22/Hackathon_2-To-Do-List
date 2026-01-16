-- Migration: 004_fix_user_id_types.sql
-- Purpose: Fix user_id type mismatch across all tables
-- Issue: users.id is INTEGER but Python models use VARCHAR
-- Solution: Change all user_id columns to VARCHAR(255) to match Python models
-- Database: Neon PostgreSQL (PostgreSQL 16+)

-- =====================================================
-- Step 1: Drop foreign key constraints that reference users.id
-- =====================================================
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_user_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_user_id_fkey;
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_user_id_fkey;

-- =====================================================
-- Step 2: Change users.id from INTEGER to VARCHAR(255)
-- =====================================================
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE users ALTER COLUMN id TYPE VARCHAR(255) USING id::TEXT;
ALTER TABLE users ADD PRIMARY KEY (id);

-- =====================================================
-- Step 3: Change all user_id columns to VARCHAR(255)
-- =====================================================
ALTER TABLE tasks ALTER COLUMN user_id TYPE VARCHAR(255) USING user_id::TEXT;
ALTER TABLE messages ALTER COLUMN user_id TYPE VARCHAR(255) USING user_id::TEXT;
ALTER TABLE conversations ALTER COLUMN user_id TYPE VARCHAR(255) USING user_id::TEXT;

-- =====================================================
-- Step 4: Recreate foreign key constraints
-- =====================================================
ALTER TABLE tasks ADD CONSTRAINT tasks_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE messages ADD CONSTRAINT messages_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE conversations ADD CONSTRAINT conversations_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- =====================================================
-- Verification
-- =====================================================
-- Run this to verify all columns are now VARCHAR:
-- SELECT table_name, column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name IN ('users', 'tasks', 'messages', 'conversations')
--   AND column_name = 'user_id'
--   OR (table_name = 'users' AND column_name = 'id')
-- ORDER BY table_name;
