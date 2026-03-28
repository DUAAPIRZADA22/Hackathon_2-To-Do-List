-- Migration: 002_add_conversation_title.sql
-- Purpose: Add missing 'title' column to conversations table
-- Issue: Model has title field but migration didn't create it
-- Database: Neon PostgreSQL (PostgreSQL 16+)

-- =====================================================
-- Add title column to conversations table
-- =====================================================
ALTER TABLE conversations
ADD COLUMN IF NOT EXISTS title VARCHAR(255) DEFAULT 'New Chat';

-- =====================================================
-- Update existing rows to have default title
-- =====================================================
UPDATE conversations
SET title = 'New Chat'
WHERE title IS NULL;

-- =====================================================
-- Add NOT NULL constraint after data is populated
-- =====================================================
ALTER TABLE conversations
ALTER COLUMN title SET NOT NULL;

-- =====================================================
-- Verification
-- =====================================================
-- Run this to verify the column was added:
-- SELECT column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'conversations' AND column_name = 'title';

-- =====================================================
-- Rollback (if needed)
-- =====================================================
-- To rollback this migration, run:
-- ALTER TABLE conversations DROP COLUMN IF EXISTS title;
