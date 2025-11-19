"""
Quick script to display the SQL needed for retry logic migration
"""

print("\n" + "="*70)
print("SUPABASE SQL MIGRATION - RETRY LOGIC (SIM-118)")
print("="*70)
print("\n📋 Copy and paste this SQL into your Supabase SQL Editor:\n")
print("-"*70)

sql = """
-- Add retry logic columns to subscriptions table
ALTER TABLE subscriptions 
ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS retry_date DATE,
ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;

-- Create index for efficient retry processing
CREATE INDEX IF NOT EXISTS idx_subscriptions_retry_date 
ON subscriptions(retry_date) 
WHERE status = 'payment_failed';

-- Add documentation
COMMENT ON COLUMN subscriptions.retry_count IS 'Number of payment retry attempts (0-3)';
COMMENT ON COLUMN subscriptions.retry_date IS 'Date when next payment retry should be attempted';
COMMENT ON COLUMN subscriptions.cancellation_reason IS 'Reason for subscription cancellation';
"""

print(sql)
print("-"*70)
print("\n✅ After running this SQL, your test subscription insert will work!")
print("\n📍 Location: Supabase Dashboard → SQL Editor → New Query\n")
print("="*70 + "\n")
