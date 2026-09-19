"""
Integration tests for payment API
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime, timedelta
import random
import time
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestPaymentFlow:
    """Integration tests for payment API"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def test_user_and_subscription(self, client):
        """Create real user and subscription for payment tests"""
        from src.auth.supabase_auth import supabase_auth
        
        # Create real user
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        random_num = random.randint(100000, 999999)
        email = f"paytest{timestamp}{random_num}@gmail.com"
        
        time.sleep(2)
        
        # Register user
        reg_response = client.post(
            "/api/auth/register",
            json={"email": email, "password": "PayTest123!"}
        )
        
        if reg_response.status_code in [400, 429]:
            pytest.skip("Rate limit hit")
        
        time.sleep(2)
        
        # Login to get user_id
        login_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": "PayTest123!"}
        )
        
        user_id = login_response.json()["user_id"]
        
        # Create test plan (if needed)
        plan_id = str(uuid.uuid4())  # Mock plan for now
        
        # Create subscription using real user_id
        subscription_data = {
            "user_id": user_id,
            "plan_id": plan_id,
            "status": "active",
            "started_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        sub_response = supabase_auth.service_client.table("subscriptions").insert(
            subscription_data
        ).execute()
        
        return {
            "user_id": user_id,
            "subscription_id": sub_response.data[0]["id"],
            "access_token": login_response.json()["access_token"]
        }

    # ===== TESTS USING REAL SUBSCRIPTION =====

    def test_mock_payment_success(self, client, test_user_and_subscription):
        """Test successful mock payment"""
        sub_id = test_user_and_subscription["subscription_id"]
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": sub_id,
                    "amount": 29.99,
                    "should_succeed": True
                }
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["transaction_id"] is not None

    def test_mock_payment_failure(self, client, test_user_and_subscription):
        """Test failed mock payment"""
        sub_id = test_user_and_subscription["subscription_id"]
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": sub_id,
                    "amount": 29.99,
                    "should_succeed": False
                }
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "failed"

    def test_mock_payment_large_amount(self, client, test_user_and_subscription):
        """Test payment with large amount"""
        sub_id = test_user_and_subscription["subscription_id"]
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": sub_id,
                    "amount": 9999.99,
                    "should_succeed": True
                }
            }
        )
        assert response.status_code == 201

    # ===== VALIDATION TESTS (Don't need real subscription) =====

    def test_mock_payment_invalid_amount_negative(self, client):
        """Test payment with negative amount"""
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": str(uuid.uuid4()),
                    "amount": -10.00,
                    "should_succeed": True
                }
            }
        )
        assert response.status_code == 422

    def test_mock_payment_invalid_amount_zero(self, client):
        """Test payment with zero amount"""
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": str(uuid.uuid4()),
                    "amount": 0,
                    "should_succeed": True
                }
            }
        )
        assert response.status_code == 422

    def test_mock_payment_missing_subscription_id(self, client):
        """Test payment without subscription_id"""
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "amount": 29.99
                }
            }
        )
        assert response.status_code == 422

    def test_get_payment_history_without_auth(self, client):
        """Test getting payment history without auth"""
        response = client.get(f"/api/payments/history/{uuid.uuid4()}")
        assert response.status_code in [401, 422]

    def test_get_payment_history_with_auth(self, client, test_user_and_subscription):
        """Test getting payment history with auth"""
        token = test_user_and_subscription["access_token"]
        sub_id = test_user_and_subscription["subscription_id"]
        
        response = client.get(
            f"/api/payments/history/{sub_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_get_payment_status_without_auth(self, client):
        """Test getting payment status without auth"""
        response = client.get(f"/api/payments/status/{uuid.uuid4()}")
        assert response.status_code in [401, 422]

    def test_get_payment_status_with_auth_not_found(self, client, test_user_and_subscription):
        """Test getting nonexistent payment status"""
        token = test_user_and_subscription["access_token"]
        
        response = client.get(
            f"/api/payments/status/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
