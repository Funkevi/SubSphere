"""
CRON Worker for Subscription Renewals and Trial Conversions
SIM-108: Runs daily at midnight to process renewals
"""
import os
import sys
from datetime import datetime, timezone, date, timedelta
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.auth.supabase_auth import supabase_auth

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RenewalWorker:
    """Handles subscription renewals and trial conversions"""
    
    def __init__(self):
        self.db = supabase_auth.service_client
        self.today = date.today()
        logger.info(f"RenewalWorker initialized for {self.today}")
    
    def run(self):
        """Main execution method"""
        logger.info(f"=== Renewal Worker Started at {datetime.now(timezone.utc)} ===")
        
        try:
            # Process retries first
            retry_count = self.process_retries()
            logger.info(f"Processed {retry_count} payment retries")
            
            # Process trial conversions
            trial_count = self.process_trial_conversions()
            logger.info(f"Processed {trial_count} trial conversions")
            
            # Process renewals
            renewal_count = self.process_renewals()
            logger.info(f"Processed {renewal_count} renewals")
            
            logger.info("=== Renewal Worker Completed Successfully ===\n")
            
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
            raise
    
    def process_trial_conversions(self) -> int:
        """Convert trials ending today to paid subscriptions"""
        try:
            response = self.db.table("subscriptions").select(
                "*"
            ).eq("status", "trial").execute()
            
            count = 0
            for subscription in response.data:
                if subscription.get("trial_end"):
                    trial_end = datetime.fromisoformat(
                        subscription["trial_end"].replace('Z', '+00:00')
                    ).date()
                    
                    if trial_end == self.today:
                        success = self.convert_trial_to_paid(subscription)
                        if success:
                            count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error processing trial conversions: {e}")
            return 0
    
    def convert_trial_to_paid(self, subscription) -> bool:
        """Convert single trial to paid subscription"""
        try:
            subscription_id = subscription["id"]
            plan_id = subscription["plan_id"]
            
            # Get plan details
            plan_response = self.db.table("subscription_plans").select(
                "*"
            ).eq("id", plan_id).single().execute()
            
            if not plan_response.data:
                logger.warning(f"Plan not found for subscription {subscription_id}")
                return False
            
            plan = plan_response.data
            
            # Process payment
            payment_success = self.process_payment(subscription_id, plan["price"])
            
            if payment_success:
                # Update subscription to active
                next_billing = datetime.now(timezone.utc) + timedelta(days=30)  # Default 30 days
                
                self.db.table("subscriptions").update({
                    "status": "active",
                    "next_billing_date": next_billing.isoformat(),
                    "converted_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", subscription_id).execute()
                
                # Log event
                self.log_event(subscription_id, "trial_converted", plan["price"])
                
                logger.info(f"✓ Converted trial subscription {subscription_id} to paid")
                return True
            else:
                logger.warning(f"Payment failed for subscription {subscription_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error converting trial {subscription['id']}: {e}")
            return False
    
    def process_renewals(self) -> int:
        """Process subscriptions due for renewal today"""
        try:
            response = self.db.table("subscriptions").select(
                "*"
            ).eq("status", "active").execute()
            
            count = 0
            for subscription in response.data:
                if subscription.get("next_billing_date"):
                    billing_date = datetime.fromisoformat(
                        subscription["next_billing_date"].replace('Z', '+00:00')
                    ).date()
                    
                    if billing_date == self.today:
                        success = self.renew_subscription(subscription)
                        if success:
                            count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error processing renewals: {e}")
            return 0
    
    def renew_subscription(self, subscription) -> bool:
        """Renew single subscription"""
        try:
            subscription_id = subscription["id"]
            plan_id = subscription["plan_id"]
            
            # Get plan details
            plan_response = self.db.table("subscription_plans").select(
                "*"
            ).eq("id", plan_id).single().execute()
            
            if not plan_response.data:
                logger.warning(f"Plan not found for subscription {subscription_id}")
                return False
            
            plan = plan_response.data
            
            # Process payment
            payment_success = self.process_payment(subscription_id, plan["price"])
            
            if payment_success:
                # Extend billing date
                current_billing = datetime.fromisoformat(
                    subscription["next_billing_date"].replace('Z', '+00:00')
                )
                next_billing = current_billing + timedelta(days=30)  # Default 30 days
                
                self.db.table("subscriptions").update({
                    "next_billing_date": next_billing.isoformat(),
                    "last_renewed_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", subscription_id).execute()
                
                # Log event
                self.log_event(subscription_id, "renewed", plan["price"])
                
                logger.info(f"✓ Renewed subscription {subscription_id}")
                return True
            else:
                # Payment failed - initiate retry logic
                logger.warning(f"Payment failed for renewal {subscription_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error renewing subscription {subscription['id']}: {e}")
            return False
    
    def process_payment(self, subscription_id: str, amount: float) -> bool:
        """Mock payment processing"""
        import random
        
        # 90% success rate for testing
        should_succeed = random.random() < 0.9  # nosec B311 - Mock payment for testing only
        
        try:
            payment_data = {
                "subscription_id": subscription_id,
                "amount": float(amount),
                "status": "success" if should_succeed else "failed",
                "transaction_id": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "payment_method": "mock"
            }
            
            self.db.table("payments").insert(payment_data).execute()
            logger.info(f"Payment {'succeeded' if should_succeed else 'failed'} for {subscription_id}")
            
            return should_succeed
            
        except Exception as e:
            logger.error(f"Error processing payment: {e}")
            return False
    
    def process_retries(self) -> int:
        """Process payment retries for failed renewals (SIM-118)"""
        try:
            # Find subscriptions with failed payments due for retry
            response = self.db.table("subscriptions").select(
                "*"
            ).eq("status", "payment_failed").execute()
            
            count = 0
            for subscription in response.data:
                if subscription.get("retry_date"):
                    retry_date = datetime.fromisoformat(
                        subscription["retry_date"].replace('Z', '+00:00')
                    ).date()
                    
                    if retry_date == self.today:
                        success = self.retry_payment(subscription)
                        if success:
                            count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error processing retries: {e}")
            return 0
    
    def retry_payment(self, subscription) -> bool:
        """Retry payment for failed subscription (SIM-118)"""
        try:
            subscription_id = subscription["id"]
            retry_count = subscription.get("retry_count", 0)
            
            # Max 3 retries
            if retry_count >= 3:
                logger.warning(f"Max retries reached for {subscription_id}, cancelling...")
                self.cancel_subscription_after_retries(subscription)
                return False
            
            # Get plan for amount
            plan_response = self.db.table("subscription_plans").select(
                "*"
            ).eq("id", subscription["plan_id"]).single().execute()
            
            if not plan_response.data:
                return False
            
            plan = plan_response.data
            
            # Attempt payment
            payment_success = self.process_payment(subscription_id, plan["price"])
            
            if payment_success:
                # Payment succeeded - reactivate subscription
                next_billing = datetime.now(timezone.utc) + timedelta(days=plan.get("duration_days", 30))
                
                self.db.table("subscriptions").update({
                    "status": "active",
                    "retry_count": 0,
                    "retry_date": None,
                    "next_billing_date": next_billing.isoformat()
                }).eq("id", subscription_id).execute()
                
                # Log event
                self.log_event(subscription_id, "retry_payment_success", plan["price"])
                
                logger.info(f"✓ Retry payment succeeded for {subscription_id} (attempt {retry_count + 1})")
                return True
            else:
                # Payment failed - schedule next retry
                new_retry_count = retry_count + 1
                
                # Retry intervals: day 1, 3, 7 after failure
                retry_intervals = {1: 1, 2: 3, 3: 7}
                days_until_retry = retry_intervals.get(new_retry_count, 7)
                
                next_retry_date = datetime.now(timezone.utc) + timedelta(days=days_until_retry)
                
                self.db.table("subscriptions").update({
                    "retry_count": new_retry_count,
                    "retry_date": next_retry_date.isoformat()
                }).eq("id", subscription_id).execute()
                
                logger.warning(f"Retry payment failed for {subscription_id} (attempt {new_retry_count})")
                logger.info(f"Next retry scheduled for {next_retry_date.date()}")
                
                return False
                
        except Exception as e:
            logger.error(f"Error retrying payment for {subscription['id']}: {e}")
            return False
    
    def cancel_subscription_after_retries(self, subscription) -> None:
        """Cancel subscription after max retry attempts (SIM-118)"""
        try:
            subscription_id = subscription["id"]
            
            self.db.table("subscriptions").update({
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
                "cancellation_reason": "payment_failed_max_retries"
            }).eq("id", subscription_id).execute()
            
            # Log event
            self.log_event(subscription_id, "cancelled_after_retries", 0)
            
            logger.warning(f"⚠ Cancelled subscription {subscription_id} after 3 failed payment attempts")
            
        except Exception as e:
            logger.error(f"Error cancelling subscription {subscription['id']}: {e}")
    
    def log_event(self, subscription_id: str, action: str, amount: float) -> None:
        """Log subscription event"""
        try:
            log_data = {
                "subscription_id": subscription_id,
                "action": action,
                "amount": float(amount),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            self.db.table("subscription_logs").insert(log_data).execute()
            
        except Exception as e:
            logger.error(f"Error logging event: {e}")


if __name__ == "__main__":
    worker = RenewalWorker()
    worker.run()
