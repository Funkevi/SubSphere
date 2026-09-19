-- ================================================================
-- Retry Logic Migration (SIM-118)
-- Add retry columns to subscriptions table
-- ================================================================

-- Add retry logic columns
ALTER TABLE subscriptions 
ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS retry_date DATE,
ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;

-- Create index for efficient retry processing
CREATE INDEX IF NOT EXISTS idx_subscriptions_retry_date 
ON subscriptions(retry_date) 
WHERE status = 'payment_failed';

-- Add documentation comments
COMMENT ON COLUMN subscriptions.retry_count IS 'Number of payment retry attempts (0-3)';
COMMENT ON COLUMN subscriptions.retry_date IS 'Date when next payment retry should be attempted';
COMMENT ON COLUMN subscriptions.cancellation_reason IS 'Reason for subscription cancellation (e.g., payment_failed_max_retries)';

-- ================================================================
-- Verification Query
-- ================================================================

-- Run this to verify columns were added:
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'subscriptions'
AND column_name IN ('retry_count', 'retry_date', 'cancellation_reason')
ORDER BY column_name;

-- ================================================================
-- Test Data (Optional)
-- ================================================================

-- Uncomment to create a test subscription for retry testing:
/*
INSERT INTO subscriptions (user_id, plan_id, status, retry_count, retry_date)
VALUES (
    'test-user-123',
    (SELECT id FROM subscription_plans LIMIT 1),  -- Uses first available plan
    'payment_failed',
    0,
    CURRENT_DATE
);
*/
