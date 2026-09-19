# 🔧 Database Setup for Retry Logic (SIM-118)

## Quick Fix for Your Error

You're getting this error because the `subscriptions` table is missing the retry-related columns:
```
ERROR: column "retry_count" of relation "subscriptions" does not exist
```

---

## ✅ Solution: Run This SQL in Supabase

### **Step 1: Open Supabase SQL Editor**
1. Go to your Supabase dashboard
2. Navigate to **SQL Editor** (left sidebar)
3. Click **New Query**

### **Step 2: Copy and Run This SQL**

```sql
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
COMMENT ON COLUMN subscriptions.cancellation_reason IS 'Reason for subscription cancellation';
```

### **Step 3: Verify Columns Were Added**

Run this query to confirm:
```sql
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'subscriptions'
AND column_name IN ('retry_count', 'retry_date', 'cancellation_reason')
ORDER BY column_name;
```

**Expected output:**
```
column_name          | data_type | is_nullable | column_default
---------------------|-----------|-------------|---------------
cancellation_reason  | text      | YES         | 
retry_count          | integer   | YES         | 0
retry_date           | date      | YES         |
```

---

## 🧪 Now You Can Test!

### **Create Test Subscription**
```sql
INSERT INTO subscriptions (user_id, plan_id, status, retry_count, retry_date)
VALUES (
    'test-user-123',
    (SELECT id FROM subscription_plans LIMIT 1),  -- Uses first available plan
    'payment_failed',
    0,
    CURRENT_DATE
);
```

### **Verify Test Data**
```sql
SELECT id, user_id, status, retry_count, retry_date
FROM subscriptions
WHERE user_id = 'test-user-123';
```

---

## 🚀 Run Renewal Worker

Now you can test the retry logic:
```powershell
cd D:\Balenahalli\TestSE_Repo\backend
python src/workers/renewal_worker.py
```

**Expected logs:**
```
=== Renewal Worker Started at 2024-XX-XX XX:XX:XX ===
Processed 1 payment retries
✓ Retry payment succeeded for sub-xxx (attempt 1)
  OR
⚠ Retry payment failed for sub-xxx (attempt 1)
Next retry scheduled for 2024-XX-XX
```

---

## 📋 What These Columns Do

| Column | Type | Purpose |
|--------|------|---------|
| `retry_count` | INTEGER | Tracks number of retry attempts (0-3). Resets to 0 on success. |
| `retry_date` | DATE | Date when next payment retry should be attempted. NULL when not retrying. |
| `cancellation_reason` | TEXT | Reason for cancellation (e.g., `payment_failed_max_retries`). |

---

## 🔄 Rollback (If Needed)

To remove these columns:
```sql
DROP INDEX IF EXISTS idx_subscriptions_retry_date;
ALTER TABLE subscriptions 
DROP COLUMN IF EXISTS retry_count,
DROP COLUMN IF EXISTS retry_date,
DROP COLUMN IF EXISTS cancellation_reason;
```

---

## 🛠️ Alternative: Run Migration Script

You can also use the Python migration script:
```powershell
cd D:\Balenahalli\TestSE_Repo\backend
python src/database/migration_retry_logic.py
```

This will provide the SQL to run manually (Supabase doesn't allow direct DDL from Python clients).

---

## ✅ Migration Files Created

1. **`src/database/migration_retry_logic.py`** - Python migration script
2. **`src/database/migrations/001_add_retry_columns.sql`** - Ready-to-run SQL file

Both contain the same SQL statements you need to run.

---

## 🎯 Next Steps After Running SQL

1. ✅ Run the SQL above in Supabase SQL Editor
2. ✅ Verify columns with the verification query
3. ✅ Create test subscription (optional)
4. ✅ Run renewal worker to test retry logic
5. ✅ Check unit tests: `pytest tests/unit/test_retry_logic.py -v`

That's it! The retry logic will now work correctly. 🚀
