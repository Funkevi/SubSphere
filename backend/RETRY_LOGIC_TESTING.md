# Retry Logic Testing Guide (SIM-118)

## Overview
The retry logic automatically handles failed subscription payments by:
1. **Scheduling retries** at intervals: 1 day, 3 days, 7 days
2. **Reactivating subscriptions** when retry payments succeed
3. **Cancelling subscriptions** after 3 failed retry attempts

---

## ✅ Ways to Verify It's Working

### Method 1: Run Unit Tests (Recommended)
```powershell
cd D:\Balenahalli\TestSE_Repo\backend
pytest tests/unit/test_retry_logic.py -v
```

**What to look for:**
- All 9 tests should pass
- Tests cover: retry processing, payment success/failure, retry intervals, cancellation

---

### Method 2: Run Manual Testing Script
```powershell
cd D:\Balenahalli\TestSE_Repo\backend
python tests/manual/test_retry_logic_manual.py
```

**What it does:**
- Creates test subscriptions with `payment_failed` status
- Simulates retry attempts
- Verifies retry intervals (1, 3, 7 days)
- Tests max retry cancellation
- Cleans up test data

**Expected output:**
```
=== Scenario 1: First Retry Success ===
✓ Created subscription: sub-xxx
Final status: active (or payment_failed if random payment fails)

=== Scenario 2: Retry Progression ===
--- Retry Attempt 1 ---
Before: retry_count=0, status=payment_failed
After:  retry_count=1, status=payment_failed
Next retry scheduled for 1 day

--- Retry Attempt 2 ---
Before: retry_count=1, status=payment_failed
After:  retry_count=2, status=payment_failed
Next retry scheduled for 3 days

=== Scenario 3: Max Retries Cancellation ===
Final status: cancelled
Cancellation reason: payment_failed_max_retries
✓ Test passed!
```

---

### Method 3: Database Verification

#### Step 1: Create a test subscription with payment failure
```sql
-- In Supabase SQL Editor
INSERT INTO subscriptions (user_id, plan_id, status, retry_count, retry_date)
VALUES (
  'test-user-123',
  '<your-plan-id>',
  'payment_failed',
  0,
  CURRENT_DATE
);
```

#### Step 2: Run the renewal worker
```powershell
cd D:\Balenahalli\TestSE_Repo\backend
python src/workers/renewal_worker.py
```

#### Step 3: Check the logs
Look for these log messages:
```
INFO - Processed X payment retries
INFO - ✓ Retry payment succeeded for sub-xxx (attempt 1)
  OR
WARNING - Retry payment failed for sub-xxx (attempt 1)
INFO - Next retry scheduled for 2024-XX-XX
```

#### Step 4: Verify in database
```sql
-- Check subscription status
SELECT id, status, retry_count, retry_date, next_billing_date
FROM subscriptions
WHERE user_id = 'test-user-123';

-- Check payment records
SELECT subscription_id, amount, status, transaction_id
FROM payments
WHERE subscription_id = '<sub-id>'
ORDER BY created_at DESC;

-- Check subscription logs
SELECT subscription_id, action, amount, timestamp
FROM subscription_logs
WHERE subscription_id = '<sub-id>'
ORDER BY timestamp DESC;
```

---

### Method 4: GitHub Actions Workflow

The retry logic runs automatically via GitHub Actions daily at midnight UTC.

**Check workflow execution:**
1. Go to: `https://github.com/bbvk1735/TestSE_Repo/actions`
2. Look for "Renewal Worker" workflow runs
3. Click on latest run to see logs

**Expected logs:**
```
=== Renewal Worker Started at 2024-XX-XX XX:XX:XX ===
Processed X payment retries
Processed X trial conversions
Processed X renewals
=== Renewal Worker Completed Successfully ===
```

---

## 🔍 What to Check For

### ✅ Success Indicators

1. **Retry Processing**
   - Subscriptions with `status = 'payment_failed'` and `retry_date = TODAY` are processed
   - Retry count increments correctly: 0 → 1 → 2 → 3

2. **Payment Success Path**
   - Status changes: `payment_failed` → `active`
   - `retry_count` resets to 0
   - `retry_date` cleared (NULL)
   - `next_billing_date` set 30 days in future
   - New payment record created in `payments` table
   - Event logged in `subscription_logs` with action `retry_payment_success`

3. **Payment Failure Path**
   - `retry_count` increments by 1
   - `retry_date` updated based on interval:
     - Retry 1 → 2: +1 day
     - Retry 2 → 3: +3 days
     - Retry 3 → cancelled: +7 days (not used if cancelled)
   - Payment record created with status `failed`

4. **Max Retries Reached**
   - After 3 failed attempts:
     - Status changes to `cancelled`
     - `cancelled_at` timestamp set
     - `cancellation_reason` = `payment_failed_max_retries`
     - Event logged with action `cancelled_after_retries`

---

## 🧪 Test Scenarios

### Scenario A: First Retry Succeeds
```
Initial State:
  status: payment_failed
  retry_count: 0
  retry_date: TODAY

Expected Result:
  status: active
  retry_count: 0
  retry_date: NULL
  next_billing_date: TODAY + 30 days
```

### Scenario B: Retry Progression (Failures)
```
Attempt 1:
  retry_count: 0 → 1
  retry_date: TODAY + 1 day

Attempt 2:
  retry_count: 1 → 2
  retry_date: TODAY + 3 days

Attempt 3:
  retry_count: 2 → 3
  retry_date: TODAY + 7 days
```

### Scenario C: Max Retries (Cancellation)
```
Initial State:
  retry_count: 3
  retry_date: TODAY

Expected Result:
  status: cancelled
  cancellation_reason: payment_failed_max_retries
  cancelled_at: <timestamp>
```

---

## 🐛 Troubleshooting

### Issue: Retries not processing
**Check:**
- Is `retry_date` set to today's date?
- Is `status` = `payment_failed`?
- Are Supabase credentials configured correctly?

**Debug:**
```powershell
# Run worker with verbose logging
cd D:\Balenahalli\TestSE_Repo\backend
python src/workers/renewal_worker.py
```

### Issue: Payments always failing
**Cause:** Mock payment has 90% success rate (10% failure for testing)

**Fix for testing:** Temporarily modify `process_payment` method:
```python
# Force success
should_succeed = True  # Instead of: random.random() < 0.9
```

### Issue: Retry intervals incorrect
**Check:** Verify date calculations in logs:
```
INFO - Next retry scheduled for 2024-XX-XX
```

**Debug:** Run interval verification:
```powershell
python tests/manual/test_retry_logic_manual.py
```

---

## 📊 Coverage Report

Run comprehensive tests:
```powershell
pytest tests/unit/test_renewal_worker.py tests/unit/test_retry_logic.py -v --cov=src.workers.renewal_worker
```

**Current coverage:** 94% (173 statements, 10 missed)

**Tested scenarios:**
- ✅ Retry processing success
- ✅ No retries due today
- ✅ First retry success
- ✅ Second retry failure
- ✅ Max retries cancellation
- ✅ Retry interval progression (1, 3, 7 days)
- ✅ Plan not found handling
- ✅ Exception handling

---

## 📝 Database Schema Requirements

Ensure these columns exist:

**subscriptions table:**
```sql
- retry_count (integer, default: 0)
- retry_date (date, nullable)
- cancellation_reason (text, nullable)
```

If missing, add with migration:
```sql
ALTER TABLE subscriptions ADD COLUMN retry_count INTEGER DEFAULT 0;
ALTER TABLE subscriptions ADD COLUMN retry_date DATE;
ALTER TABLE subscriptions ADD COLUMN cancellation_reason TEXT;
```

---

## 🚀 Next Steps

1. **Run unit tests** to verify implementation ✅
2. **Run manual script** to see it in action
3. **Create test subscription** in database
4. **Monitor GitHub Actions** workflow
5. **Check logs** for retry processing

---

## 📚 Related Files

- Implementation: `backend/src/workers/renewal_worker.py`
- Unit tests: `backend/tests/unit/test_retry_logic.py`
- Manual tests: `backend/tests/manual/test_retry_logic_manual.py`
- Workflow: `.github/workflows/renewal_worker.yml`
