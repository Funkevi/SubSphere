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
        should_succeed = random.random() < 0.9
        
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
        """Process payment retries"""
        # Placeholder for retry logic
        return 0
    
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
