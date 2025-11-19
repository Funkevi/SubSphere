"""
Manual Testing Script for Retry Logic (SIM-118)
Run this script to manually verify retry logic functionality

Prerequisites:
- Backend server running
- Valid Supabase credentials in .env
- Test subscriptions in database

Usage:
    python tests/manual/test_retry_logic_manual.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timezone, date, timedelta
from src.auth.supabase_auth import supabase_auth
from src.workers.renewal_worker import RenewalWorker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetryLogicManualTester:
    """Manual testing helper for retry logic"""
    
    def __init__(self):
        self.db = supabase_auth.service_client
        self.test_user_email = "retry_test@example.com"
        self.test_plan_id = None
        self.test_subscription_id = None
    
    def setup_test_data(self):
        """Create test user, plan, and subscription"""
        logger.info("\n=== Setting Up Test Data ===")
        
        # 1. Create test plan
        try:
            plan_response = self.db.table("subscription_plans").insert({
                "name": "Test Retry Plan",
                "price": 19.99,
                "duration_days": 30,
                "features": {"test": "feature"}
            }).execute()
            
            self.test_plan_id = plan_response.data[0]["id"]
            logger.info(f"✓ Created test plan: {self.test_plan_id}")
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            return False
        
        # 2. Create test subscription with payment_failed status
        try:
            subscription_response = self.db.table("subscriptions").insert({
                "user_id": "test-user-" + str(int(datetime.now().timestamp())),
                "plan_id": self.test_plan_id,
                "status": "payment_failed",
                "retry_count": 0,
                "retry_date": date.today().isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            self.test_subscription_id = subscription_response.data[0]["id"]
            logger.info(f"✓ Created test subscription: {self.test_subscription_id}")
            logger.info(f"  - Status: payment_failed")
            logger.info(f"  - Retry count: 0")
            logger.info(f"  - Retry date: {date.today()}")
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            return False
        
        return True
    
    def test_scenario_1_first_retry_success(self):
        """Scenario 1: First retry attempt succeeds"""
        logger.info("\n=== Scenario 1: First Retry Success ===")
        
        # Create subscription with retry_count = 0
        sub = self.db.table("subscriptions").insert({
            "user_id": "test-user-scenario1",
            "plan_id": self.test_plan_id,
            "status": "payment_failed",
            "retry_count": 0,
            "retry_date": date.today().isoformat()
        }).execute()
        
        sub_id = sub.data[0]["id"]
        logger.info(f"Created subscription: {sub_id}")
        
        # Run worker
        worker = RenewalWorker()
        count = worker.process_retries()
        
        # Check result
        result = self.db.table("subscriptions").select("*").eq("id", sub_id).execute()
        final_status = result.data[0]["status"]
        
        logger.info(f"Retry count: {count}")
        logger.info(f"Final status: {final_status}")
        logger.info(f"Expected: status = 'active' or 'payment_failed'")
        
        return result.data[0]
    
    def test_scenario_2_retry_progression(self):
        """Scenario 2: Track retry progression through multiple failures"""
        logger.info("\n=== Scenario 2: Retry Progression ===")
        
        # Create subscription at retry_count = 0
        sub = self.db.table("subscriptions").insert({
            "user_id": "test-user-scenario2",
            "plan_id": self.test_plan_id,
            "status": "payment_failed",
            "retry_count": 0,
            "retry_date": date.today().isoformat()
        }).execute()
        
        sub_id = sub.data[0]["id"]
        logger.info(f"Created subscription: {sub_id} (retry_count=0)")
        
        worker = RenewalWorker()
        
        # Simulate multiple retry attempts
        for attempt in range(1, 4):
            logger.info(f"\n--- Retry Attempt {attempt} ---")
            
            # Get current state
            current = self.db.table("subscriptions").select("*").eq("id", sub_id).execute()
            current_data = current.data[0]
            
            logger.info(f"Before: retry_count={current_data.get('retry_count', 0)}, status={current_data['status']}")
            
            # Process retry
            result = worker.retry_payment(current_data)
            
            # Check updated state
            updated = self.db.table("subscriptions").select("*").eq("id", sub_id).execute()
            updated_data = updated.data[0]
            
            logger.info(f"After:  retry_count={updated_data.get('retry_count', 0)}, status={updated_data['status']}")
            logger.info(f"Payment result: {'SUCCESS' if result else 'FAILED'}")
            
            if updated_data["status"] == "cancelled":
                logger.warning("⚠ Subscription cancelled after max retries")
                break
        
        return updated_data
    
    def test_scenario_3_max_retries_cancellation(self):
        """Scenario 3: Subscription cancelled after 3 failed retries"""
        logger.info("\n=== Scenario 3: Max Retries Cancellation ===")
        
        # Create subscription at retry_count = 3
        sub = self.db.table("subscriptions").insert({
            "user_id": "test-user-scenario3",
            "plan_id": self.test_plan_id,
            "status": "payment_failed",
            "retry_count": 3,
            "retry_date": date.today().isoformat()
        }).execute()
        
        sub_id = sub.data[0]["id"]
        logger.info(f"Created subscription: {sub_id} (retry_count=3)")
        
        # Run worker
        worker = RenewalWorker()
        count = worker.process_retries()
        
        # Check result
        result = self.db.table("subscriptions").select("*").eq("id", sub_id).execute()
        final_data = result.data[0]
        
        logger.info(f"Final status: {final_data['status']}")
        logger.info(f"Cancellation reason: {final_data.get('cancellation_reason', 'N/A')}")
        logger.info(f"Expected: status = 'cancelled', reason = 'payment_failed_max_retries'")
        
        assert final_data["status"] == "cancelled"
        assert final_data["cancellation_reason"] == "payment_failed_max_retries"
        logger.info("✓ Test passed!")
        
        return final_data
    
    def verify_retry_intervals(self):
        """Verify retry date intervals follow pattern: 1, 3, 7 days"""
        logger.info("\n=== Verifying Retry Intervals ===")
        
        worker = RenewalWorker()
        
        test_cases = [
            (0, 1, "First retry"),
            (1, 3, "Second retry"),
            (2, 7, "Third retry")
        ]
        
        for retry_count, expected_days, description in test_cases:
            sub = self.db.table("subscriptions").insert({
                "user_id": f"test-interval-{retry_count}",
                "plan_id": self.test_plan_id,
                "status": "payment_failed",
                "retry_count": retry_count,
                "retry_date": date.today().isoformat()
            }).execute()
            
            sub_id = sub.data[0]["id"]
            
            # Force payment failure
            import random
            original_random = random.random
            random.random = lambda: 0.95  # Force failure
            
            worker.retry_payment(sub.data[0])
            
            random.random = original_random
            
            # Check retry date
            result = self.db.table("subscriptions").select("*").eq("id", sub_id).execute()
            retry_date = result.data[0].get("retry_date")
            
            if retry_date:
                retry_date_parsed = datetime.fromisoformat(retry_date.replace('Z', '+00:00')).date()
                expected_date = date.today() + timedelta(days=expected_days)
                
                logger.info(f"{description}:")
                logger.info(f"  Expected interval: {expected_days} days")
                logger.info(f"  Scheduled for: {retry_date_parsed}")
                logger.info(f"  Expected: {expected_date}")
                logger.info(f"  Match: {'✓' if retry_date_parsed == expected_date else '✗'}")
    
    def cleanup_test_data(self):
        """Remove test data"""
        logger.info("\n=== Cleaning Up Test Data ===")
        
        try:
            # Delete test subscriptions
            self.db.table("subscriptions").delete().like("user_id", "test-%").execute()
            logger.info("✓ Deleted test subscriptions")
            
            # Delete test plan
            if self.test_plan_id:
                self.db.table("subscription_plans").delete().eq("id", self.test_plan_id).execute()
                logger.info("✓ Deleted test plan")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def run_all_tests(self):
        """Run all manual tests"""
        logger.info("\n" + "="*60)
        logger.info("RETRY LOGIC MANUAL TESTING - SIM-118")
        logger.info("="*60)
        
        if not self.setup_test_data():
            logger.error("Setup failed, aborting tests")
            return
        
        try:
            self.test_scenario_1_first_retry_success()
            self.test_scenario_2_retry_progression()
            self.test_scenario_3_max_retries_cancellation()
            self.verify_retry_intervals()
        finally:
            self.cleanup_test_data()
        
        logger.info("\n" + "="*60)
        logger.info("MANUAL TESTING COMPLETE")
        logger.info("="*60)


def main():
    """Run manual tests"""
    tester = RetryLogicManualTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
