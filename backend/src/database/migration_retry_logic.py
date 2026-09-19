"""
Database Migration for Retry Logic (SIM-118)
Adds retry-related columns to subscriptions table
"""

ADD_RETRY_COLUMNS = """
-- Add retry logic columns to subscriptions table
ALTER TABLE subscriptions 
ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS retry_date DATE,
ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;

-- Create index for retry processing
CREATE INDEX IF NOT EXISTS idx_subscriptions_retry_date 
ON subscriptions(retry_date) 
WHERE status = 'payment_failed';

-- Add comment for documentation
COMMENT ON COLUMN subscriptions.retry_count IS 'Number of payment retry attempts (0-3)';
COMMENT ON COLUMN subscriptions.retry_date IS 'Date when next payment retry should be attempted';
COMMENT ON COLUMN subscriptions.cancellation_reason IS 'Reason for subscription cancellation';
"""

ROLLBACK_RETRY_COLUMNS = """
-- Rollback: Remove retry logic columns
DROP INDEX IF EXISTS idx_subscriptions_retry_date;
ALTER TABLE subscriptions 
DROP COLUMN IF EXISTS retry_count,
DROP COLUMN IF EXISTS retry_date,
DROP COLUMN IF EXISTS cancellation_reason;
"""


def run_migration():
    """Execute migration to add retry columns"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.auth.supabase_auth import supabase_auth
    
    try:
        # Execute migration SQL
        response = supabase_auth.service_client.rpc(
            'exec_sql', 
            {'query': ADD_RETRY_COLUMNS}
        ).execute()
        
        print("✓ Retry logic columns added successfully")
        print("  - retry_count (INTEGER, default: 0)")
        print("  - retry_date (DATE)")
        print("  - cancellation_reason (TEXT)")
        print("  - idx_subscriptions_retry_date (INDEX)")
        return True
        
    except Exception as e:
        # Try alternative method using direct SQL execution
        print(f"⚠ RPC method failed: {e}")
        print("📝 Please run the following SQL manually in Supabase SQL Editor:")
        print("\n" + "="*60)
        print(ADD_RETRY_COLUMNS)
        print("="*60 + "\n")
        return False


def rollback_migration():
    """Rollback migration (remove retry columns)"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.auth.supabase_auth import supabase_auth
    
    try:
        response = supabase_auth.service_client.rpc(
            'exec_sql',
            {'query': ROLLBACK_RETRY_COLUMNS}
        ).execute()
        
        print("✓ Retry logic columns removed successfully")
        return True
        
    except Exception as e:
        print(f"⚠ RPC rollback failed: {e}")
        print("📝 Please run the following SQL manually in Supabase SQL Editor:")
        print("\n" + "="*60)
        print(ROLLBACK_RETRY_COLUMNS)
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("\n🔄 Rolling back retry logic migration...\n")
        rollback_migration()
    else:
        print("\n🚀 Running retry logic migration (SIM-118)...\n")
        run_migration()
