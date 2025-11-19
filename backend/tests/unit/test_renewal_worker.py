"""
Unit tests for Renewal Worker
SIM-108: Daily subscription renewal and trial conversion processing
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timezone, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestRenewalWorker:
    """Test suite for RenewalWorker class"""
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_worker_initialization(self, mock_supabase):
        """Test worker initializes correctly"""
        from src.workers.renewal_worker import RenewalWorker
        
        worker = RenewalWorker()
        
        assert worker.db == mock_supabase.service_client
        assert worker.today == date.today()
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_run_executes_all_processes(self, mock_supabase):
        """Test run method executes all processing steps"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Mock empty responses
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        worker = RenewalWorker()
        
        # Should not raise exceptions
        worker.run()
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_trial_conversions_no_trials(self, mock_supabase):
        """Test processing when no trials exist"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        worker = RenewalWorker()
        count = worker.process_trial_conversions()
        
        assert count == 0
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_trial_conversions_trial_not_ending_today(self, mock_supabase):
        """Test trial not ending today is skipped"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Trial ending tomorrow
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        mock_response = Mock()
        mock_response.data = [{
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "status": "trial",
            "trial_end": tomorrow
        }]
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        worker = RenewalWorker()
        count = worker.process_trial_conversions()
        
        assert count == 0
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_trial_conversions_success(self, mock_supabase):
        """Test successful trial conversion"""
        from src.workers.renewal_worker import RenewalWorker
        
        today = date.today().isoformat()
        
        # Mock trial ending today
        mock_trials_response = Mock()
        mock_trials_response.data = [{
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "status": "trial",
            "trial_end": today
        }]
        
        # Mock plan response
        mock_plan_response = Mock()
        mock_plan_response.data = {
            "id": "plan123",
            "name": "Premium",
            "price": 29.99
        }
        
        # Mock subscription update
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123"}]
        
        # Mock payment insert
        mock_payment_response = Mock()
        mock_payment_response.data = [{"id": "pay123"}]
        
        # Mock log insert
        mock_log_response = Mock()
        mock_log_response.data = [{"id": "log123"}]
        
        mock_table = Mock()
        
        # Setup chained calls
        def table_side_effect(table_name):
            if table_name == "subscriptions":
                select_mock = Mock()
                select_mock.select.return_value.eq.return_value.execute.return_value = mock_trials_response
                select_mock.update.return_value.eq.return_value.execute.return_value = mock_update_response
                return select_mock
            elif table_name == "subscription_plans":
                plan_mock = Mock()
                plan_mock.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
                return plan_mock
            elif table_name == "payments":
                payment_mock = Mock()
                payment_mock.insert.return_value.execute.return_value = mock_payment_response
                return payment_mock
            elif table_name == "subscription_logs":
                log_mock = Mock()
                log_mock.insert.return_value.execute.return_value = mock_log_response
                return log_mock
            return Mock()
        
        mock_supabase.service_client.table.side_effect = table_side_effect
        
        with patch('random.random', return_value=0.5):  # Force payment success
            worker = RenewalWorker()
            count = worker.process_trial_conversions()
        
        assert count == 1
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_convert_trial_to_paid_plan_not_found(self, mock_supabase):
        """Test conversion fails when plan not found"""
        from src.workers.renewal_worker import RenewalWorker
        
        subscription = {
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "status": "trial"
        }
        
        # Mock plan not found
        mock_plan_response = Mock()
        mock_plan_response.data = None
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        
        worker = RenewalWorker()
        result = worker.convert_trial_to_paid(subscription)
        
        assert result is False
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_convert_trial_to_paid_payment_fails(self, mock_supabase):
        """Test conversion fails when payment fails"""
        from src.workers.renewal_worker import RenewalWorker
        
        subscription = {
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "status": "trial"
        }
        
        # Mock plan found
        mock_plan_response = Mock()
        mock_plan_response.data = {
            "id": "plan123",
            "price": 29.99
        }
        
        # Mock payment insert
        mock_payment_response = Mock()
        mock_payment_response.data = [{"id": "pay123"}]
        
        def table_side_effect(table_name):
            if table_name == "subscription_plans":
                plan_mock = Mock()
                plan_mock.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
                return plan_mock
            elif table_name == "payments":
                payment_mock = Mock()
                payment_mock.insert.return_value.execute.return_value = mock_payment_response
                return payment_mock
            return Mock()
        
        mock_supabase.service_client.table.side_effect = table_side_effect
        
        with patch('random.random', return_value=0.95):  # Force payment failure
            worker = RenewalWorker()
            result = worker.convert_trial_to_paid(subscription)
        
        assert result is False
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_renewals_no_subscriptions(self, mock_supabase):
        """Test processing when no renewals are due"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_response = Mock()
        mock_response.data = []
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        worker = RenewalWorker()
        count = worker.process_renewals()
        
        assert count == 0
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_renewals_not_due_today(self, mock_supabase):
        """Test renewal not due today is skipped"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Billing date tomorrow
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        
        mock_response = Mock()
        mock_response.data = [{
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "status": "active",
            "next_billing_date": tomorrow
        }]
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        worker = RenewalWorker()
        count = worker.process_renewals()
        
        assert count == 0
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_renewals_success(self, mock_supabase):
        """Test successful renewal processing"""
        from src.workers.renewal_worker import RenewalWorker
        
        today = date.today().isoformat()
        
        # Mock subscription due for renewal
        mock_subs_response = Mock()
        mock_subs_response.data = [{
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "status": "active",
            "next_billing_date": today
        }]
        
        # Mock plan response
        mock_plan_response = Mock()
        mock_plan_response.data = {
            "id": "plan123",
            "price": 29.99
        }
        
        # Mock subscription update
        mock_update_response = Mock()
        mock_update_response.data = [{"id": "sub123"}]
        
        # Mock payment insert
        mock_payment_response = Mock()
        mock_payment_response.data = [{"id": "pay123"}]
        
        # Mock log insert
        mock_log_response = Mock()
        mock_log_response.data = [{"id": "log123"}]
        
        def table_side_effect(table_name):
            if table_name == "subscriptions":
                subs_mock = Mock()
                subs_mock.select.return_value.eq.return_value.execute.return_value = mock_subs_response
                subs_mock.update.return_value.eq.return_value.execute.return_value = mock_update_response
                return subs_mock
            elif table_name == "subscription_plans":
                plan_mock = Mock()
                plan_mock.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
                return plan_mock
            elif table_name == "payments":
                payment_mock = Mock()
                payment_mock.insert.return_value.execute.return_value = mock_payment_response
                return payment_mock
            elif table_name == "subscription_logs":
                log_mock = Mock()
                log_mock.insert.return_value.execute.return_value = mock_log_response
                return log_mock
            return Mock()
        
        mock_supabase.service_client.table.side_effect = table_side_effect
        
        with patch('random.random', return_value=0.5):  # Force payment success
            worker = RenewalWorker()
            count = worker.process_renewals()
        
        assert count == 1
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_renew_subscription_plan_not_found(self, mock_supabase):
        """Test renewal fails when plan not found"""
        from src.workers.renewal_worker import RenewalWorker
        
        subscription = {
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "status": "active",
            "next_billing_date": date.today().isoformat()
        }
        
        # Mock plan not found
        mock_plan_response = Mock()
        mock_plan_response.data = None
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_response
        
        worker = RenewalWorker()
        result = worker.renew_subscription(subscription)
        
        assert result is False
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_payment_success(self, mock_supabase):
        """Test payment processing success"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_response = Mock()
        mock_response.data = [{"id": "pay123"}]
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        with patch('random.random', return_value=0.5):  # Force success
            worker = RenewalWorker()
            result = worker.process_payment("sub123", 29.99)
        
        assert result is True
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_payment_failure(self, mock_supabase):
        """Test payment processing failure"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_response = Mock()
        mock_response.data = [{"id": "pay123"}]
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        with patch('random.random', return_value=0.95):  # Force failure
            worker = RenewalWorker()
            result = worker.process_payment("sub123", 29.99)
        
        assert result is False
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_payment_exception(self, mock_supabase):
        """Test payment processing with exception"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_supabase.service_client.table.return_value.insert.side_effect = Exception("Database error")
        
        worker = RenewalWorker()
        result = worker.process_payment("sub123", 29.99)
        
        assert result is False
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_log_event_success(self, mock_supabase):
        """Test event logging success"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_response = Mock()
        mock_response.data = [{"id": "log123"}]
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value = mock_response
        
        worker = RenewalWorker()
        # Should not raise exception
        worker.log_event("sub123", "renewed", 29.99)
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_log_event_exception(self, mock_supabase):
        """Test event logging handles exception gracefully"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_supabase.service_client.table.return_value.insert.side_effect = Exception("Database error")
        
        worker = RenewalWorker()
        # Should not raise exception
        worker.log_event("sub123", "renewed", 29.99)
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_retries(self, mock_supabase):
        """Test process_retries placeholder"""
        from src.workers.renewal_worker import RenewalWorker
        
        worker = RenewalWorker()
        count = worker.process_retries()
        
        assert count == 0
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_trial_conversions_exception_handling(self, mock_supabase):
        """Test trial conversions handles exceptions"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        worker = RenewalWorker()
        count = worker.process_trial_conversions()
        
        assert count == 0
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_process_renewals_exception_handling(self, mock_supabase):
        """Test renewals handles exceptions"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        worker = RenewalWorker()
        count = worker.process_renewals()
        
        assert count == 0
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_run_with_exception(self, mock_supabase):
        """Test run method logs exceptions but doesn't re-raise"""
        from src.workers.renewal_worker import RenewalWorker
        
        mock_supabase.service_client.table.side_effect = Exception("Fatal error")
        
        worker = RenewalWorker()
        
        # Should not raise, just log the error
        try:
            worker.run()
        except Exception:
            pytest.fail("run() should not re-raise exceptions")
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_convert_trial_exception_handling(self, mock_supabase):
        """Test convert_trial_to_paid handles exceptions"""
        from src.workers.renewal_worker import RenewalWorker
        
        subscription = {
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123"
        }
        
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        worker = RenewalWorker()
        result = worker.convert_trial_to_paid(subscription)
        
        assert result is False
    
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_renew_subscription_exception_handling(self, mock_supabase):
        """Test renew_subscription handles exceptions"""
        from src.workers.renewal_worker import RenewalWorker
        
        subscription = {
            "id": "sub123",
            "user_id": "user123",
            "plan_id": "plan123",
            "next_billing_date": date.today().isoformat()
        }
        
        mock_supabase.service_client.table.side_effect = Exception("Database error")
        
        worker = RenewalWorker()
        result = worker.renew_subscription(subscription)
        
        assert result is False
    
    @patch('random.random')
    @patch('src.workers.renewal_worker.supabase_auth')
    def test_renew_subscription_payment_fails(self, mock_supabase, mock_random):
        """Test renew_subscription when payment fails"""
        from src.workers.renewal_worker import RenewalWorker
        
        # Mock plan fetch
        mock_plan_execute = Mock()
        mock_plan_execute.data = {'price': 99.99}
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_plan_execute
        
        # Mock payment failure (random > 0.9)
        mock_random.return_value = 0.95
        
        worker = RenewalWorker()
        result = worker.renew_subscription({
            'id': 'sub-123',
            'plan_id': 'plan-456',
            'next_billing_date': '2024-01-15'
        })
        
        assert result is False
