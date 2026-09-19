"""
Unit tests for Renewal Worker Retry Logic (SIM-118)
Tests the payment retry functionality with proper mocking
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime, timezone, timedelta
import pytest


class TestRetryLogic(unittest.TestCase):
    """Test cases for payment retry logic"""
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_retries_success(self, mock_supabase):
        """Test process_retries finds and processes failed payments"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Mock subscriptions with failed payments
        mock_response = Mock()
        mock_response.data = [
            {
                "id": "sub-123",
                "user_id": "user-456",
                "plan_id": "plan-789",
                "status": "payment_failed",
                "retry_count": 0,
                "retry_date": date.today().isoformat()
            },
            {
                "id": "sub-456",
                "user_id": "user-789",
                "plan_id": "plan-789",
                "status": "payment_failed",
                "retry_count": 1,
                "retry_date": date.today().isoformat()
            }
        ]
        
        # Mock plan fetch
        mock_plan = Mock()
        mock_plan.data = {"id": "plan-789", "price": 49.99, "duration_days": 30}
        
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan
        mock_supabase.service_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = Mock()
        
        worker = RenewalWorker()
        
        # Mock retry_payment to succeed
        with patch.object(worker, 'retry_payment', return_value=True):
            count = worker.process_retries()
        
        assert count == 2
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_retries_no_retries_due(self, mock_supabase):
        """Test process_retries when no retries are due today"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Mock subscriptions with future retry dates
        mock_response = Mock()
        future_date = (date.today() + timedelta(days=1)).isoformat()
        mock_response.data = [
            {
                "id": "sub-123",
                "status": "payment_failed",
                "retry_count": 0,
                "retry_date": future_date
            }
        ]
        
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        worker = RenewalWorker()
        count = worker.process_retries()
        
        assert count == 0
    
    @patch('random.random')
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_retry_payment_first_attempt_success(self, mock_supabase, mock_random):
        """Test retry_payment succeeds on first retry"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Mock payment success
        mock_random.return_value = 0.5
        
        # Mock plan fetch
        mock_plan = Mock()
        mock_plan.data = {"id": "plan-123", "price": 29.99, "duration_days": 30}
        
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan
        mock_supabase.service_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = Mock()
        
        worker = RenewalWorker()
        
        subscription = {
            "id": "sub-123",
            "user_id": "user-456",
            "plan_id": "plan-123",
            "retry_count": 0
        }
        
        result = worker.retry_payment(subscription)
        
        assert result is True
        
        # Verify subscription was updated to active
        update_call = mock_supabase.service_client.table.return_value.update
        update_call.assert_called()
        update_args = update_call.call_args[0][0]
        assert update_args["status"] == "active"
        assert update_args["retry_count"] == 0
        assert update_args["retry_date"] is None
    
    @patch('random.random')
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_retry_payment_second_attempt_fails(self, mock_supabase, mock_random):
        """Test retry_payment fails and schedules next retry"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Mock payment failure
        mock_random.return_value = 0.95
        
        # Mock plan fetch
        mock_plan = Mock()
        mock_plan.data = {"id": "plan-123", "price": 29.99, "duration_days": 30}
        
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan
        mock_supabase.service_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = Mock()
        
        worker = RenewalWorker()
        
        subscription = {
            "id": "sub-123",
            "user_id": "user-456",
            "plan_id": "plan-123",
            "retry_count": 1
        }
        
        result = worker.retry_payment(subscription)
        
        assert result is False
        
        # Verify retry count incremented and retry date set
        update_call = mock_supabase.service_client.table.return_value.update
        update_call.assert_called()
        update_args = update_call.call_args[0][0]
        assert update_args["retry_count"] == 2
        assert update_args["retry_date"] is not None
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_retry_payment_max_retries_cancels(self, mock_supabase):
        """Test subscription is cancelled after 3 failed retries"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_supabase.service_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = Mock()
        
        worker = RenewalWorker()
        
        subscription = {
            "id": "sub-123",
            "user_id": "user-456",
            "plan_id": "plan-123",
            "retry_count": 3
        }
        
        result = worker.retry_payment(subscription)
        
        assert result is False
        
        # Verify cancel_subscription_after_retries was called
        update_call = mock_supabase.service_client.table.return_value.update
        update_call.assert_called()
        update_args = update_call.call_args[0][0]
        assert update_args["status"] == "cancelled"
        assert update_args["cancellation_reason"] == "payment_failed_max_retries"
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_cancel_subscription_after_retries(self, mock_supabase):
        """Test cancel_subscription_after_retries sets correct fields"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_supabase.service_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = Mock()
        
        worker = RenewalWorker()
        
        subscription = {
            "id": "sub-123",
            "user_id": "user-456"
        }
        
        worker.cancel_subscription_after_retries(subscription)
        
        # Verify subscription was cancelled
        update_call = mock_supabase.service_client.table.return_value.update
        update_call.assert_called()
        update_args = update_call.call_args[0][0]
        assert update_args["status"] == "cancelled"
        assert update_args["cancellation_reason"] == "payment_failed_max_retries"
        assert "cancelled_at" in update_args
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_retry_intervals_progression(self, mock_supabase):
        """Test retry intervals follow pattern: 1, 3, 7 days"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Mock plan fetch
        mock_plan = Mock()
        mock_plan.data = {"id": "plan-123", "price": 29.99, "duration_days": 30}
        
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan
        mock_supabase.service_client.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = Mock()
        
        worker = RenewalWorker()
        
        # Mock payment failure
        with patch('random.random', return_value=0.95):
            # First retry
            subscription = {"id": "sub-123", "plan_id": "plan-123", "retry_count": 0}
            worker.retry_payment(subscription)
            
            update_call = mock_supabase.service_client.table.return_value.update
            update_args = update_call.call_args[0][0]
            retry_date_1 = datetime.fromisoformat(update_args["retry_date"])
            expected_1 = datetime.now(timezone.utc) + timedelta(days=1)
            assert abs((retry_date_1 - expected_1).total_seconds()) < 5
            
            # Second retry
            subscription["retry_count"] = 1
            worker.retry_payment(subscription)
            
            update_args = update_call.call_args[0][0]
            retry_date_2 = datetime.fromisoformat(update_args["retry_date"])
            expected_2 = datetime.now(timezone.utc) + timedelta(days=3)
            assert abs((retry_date_2 - expected_2).total_seconds()) < 5
            
            # Third retry
            subscription["retry_count"] = 2
            worker.retry_payment(subscription)
            
            update_args = update_call.call_args[0][0]
            retry_date_3 = datetime.fromisoformat(update_args["retry_date"])
            expected_3 = datetime.now(timezone.utc) + timedelta(days=7)
            assert abs((retry_date_3 - expected_3).total_seconds()) < 5
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_retries_exception_handling(self, mock_supabase):
        """Test process_retries handles exceptions gracefully"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")
        
        worker = RenewalWorker()
        count = worker.process_retries()
        
        assert count == 0
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_retry_payment_plan_not_found(self, mock_supabase):
        """Test retry_payment handles missing plan gracefully"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Mock plan not found
        mock_plan = Mock()
        mock_plan.data = None
        
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan
        
        worker = RenewalWorker()
        
        subscription = {
            "id": "sub-123",
            "plan_id": "nonexistent-plan",
            "retry_count": 0
        }
        
        result = worker.retry_payment(subscription)
        
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
