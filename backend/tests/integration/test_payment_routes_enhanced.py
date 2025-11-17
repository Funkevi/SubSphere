"""
Enhanced integration tests for payment routes
Focus on mocking to avoid rate limits and test all error paths
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


class TestPaymentRoutesEnhanced:
    """Enhanced tests for payment routes with mocking"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from src.main import app
        return TestClient(app)

    @pytest.fixture
    def mock_supabase_service(self):
        """Mock Supabase service client"""
        with patch('src.api.payment_routes.supabase_auth.service_client') as mock:
            yield mock

    @pytest.fixture
    def valid_token(self):
        """Generate valid JWT token"""
        from src.auth.jwt_handler import JWTHandler
        return JWTHandler.generate_token("test-user-123", "subscriber")

    @pytest.fixture
    def admin_token(self):
        """Generate admin JWT token"""
        from src.auth.jwt_handler import JWTHandler
        return JWTHandler.generate_token("admin-user-123", "admin")

    # ===== MOCK PAYMENT ENDPOINT TESTS =====

    def test_mock_payment_success_with_mock(self, client, mock_supabase_service):
        """Test successful mock payment"""
        mock_response = MagicMock()
        mock_response.data = [{
            "id": str(uuid.uuid4()),
            "subscription_id": "sub-123",
            "amount": 29.99,
            "status": "success",
            "transaction_id": "TXN-12345678",
            "payment_method": "mock",
            "created_at": "2025-11-17T00:00:00Z"
        }]
        
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": "sub-123",
                    "amount": 29.99,
                    "should_succeed": True
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
        assert data["transaction_id"] is not None

    def test_mock_payment_failure_with_mock(self, client, mock_supabase_service):
        """Test failed mock payment"""
        mock_response = MagicMock()
        mock_response.data = [{
            "id": str(uuid.uuid4()),
            "subscription_id": "sub-123",
            "amount": 29.99,
            "status": "failed",
            "transaction_id": None,
            "payment_method": "mock",
            "created_at": "2025-11-17T00:00:00Z"
        }]
        
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": "sub-123",
                    "amount": 29.99,
                    "should_succeed": False
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "failed"
        assert data["transaction_id"] is None

    def test_mock_payment_database_insert_fails(self, client, mock_supabase_service):
        """Test payment when database insert fails"""
        mock_response = MagicMock()
        mock_response.data = None  # Simulate insert failure
        
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": "sub-123",
                    "amount": 29.99,
                    "should_succeed": True
                }
            }
        )
        
        assert response.status_code == 400
        assert "Failed to create payment record" in response.json()["detail"]

    def test_mock_payment_database_exception(self, client, mock_supabase_service):
        """Test payment when database raises exception"""
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.side_effect = Exception("Database error")
        mock_supabase_service.table.return_value = mock_table
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": "sub-123",
                    "amount": 29.99,
                    "should_succeed": True
                }
            }
        )
        
        assert response.status_code == 400
        assert "Error processing payment" in response.json()["detail"]

    def test_mock_payment_with_large_amount(self, client, mock_supabase_service):
        """Test payment with very large amount"""
        mock_response = MagicMock()
        mock_response.data = [{
            "id": str(uuid.uuid4()),
            "subscription_id": "sub-123",
            "amount": 99999.99,
            "status": "success",
            "transaction_id": "TXN-LARGE",
            "payment_method": "mock",
            "created_at": "2025-11-17T00:00:00Z"
        }]
        
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": "sub-123",
                    "amount": 99999.99,
                    "should_succeed": True
                }
            }
        )
        
        assert response.status_code == 201

    def test_mock_payment_with_small_amount(self, client, mock_supabase_service):
        """Test payment with small amount"""
        mock_response = MagicMock()
        mock_response.data = [{
            "id": str(uuid.uuid4()),
            "subscription_id": "sub-123",
            "amount": 0.01,
            "status": "success",
            "transaction_id": "TXN-SMALL",
            "payment_method": "mock",
            "created_at": "2025-11-17T00:00:00Z"
        }]
        
        mock_table = MagicMock()
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.post(
            "/api/payments/mock",
            json={
                "payment": {
                    "subscription_id": "sub-123",
                    "amount": 0.01,
                    "should_succeed": True
                }
            }
        )
        
        assert response.status_code == 201

    # ===== PAYMENT HISTORY ENDPOINT TESTS =====

    def test_get_payment_history_success(self, client, valid_token, mock_supabase_service):
        """Test getting payment history successfully"""
        mock_response = MagicMock()
        mock_response.data = [
            {
                "id": str(uuid.uuid4()),
                "subscription_id": "sub-123",
                "amount": 29.99,
                "status": "success",
                "created_at": "2025-11-17T00:00:00Z"
            },
            {
                "id": str(uuid.uuid4()),
                "subscription_id": "sub-123",
                "amount": 49.99,
                "status": "success",
                "created_at": "2025-11-16T00:00:00Z"
            }
        ]
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            "/api/payments/history/sub-123",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["subscription_id"] == "sub-123"
        assert data["total_payments"] == 2
        assert data["total_amount"] == 79.98

    def test_get_payment_history_empty(self, client, valid_token, mock_supabase_service):
        """Test getting payment history with no payments"""
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            "/api/payments/history/sub-empty",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_payments"] == 0
        assert data["total_amount"] == 0

    def test_get_payment_history_with_failed_payments(self, client, valid_token, mock_supabase_service):
        """Test payment history with mix of success and failed"""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": str(uuid.uuid4()), "subscription_id": "sub-123", "amount": 29.99, "status": "success"},
            {"id": str(uuid.uuid4()), "subscription_id": "sub-123", "amount": 49.99, "status": "failed"},
            {"id": str(uuid.uuid4()), "subscription_id": "sub-123", "amount": 19.99, "status": "success"}
        ]
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            "/api/payments/history/sub-123",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_payments"] == 3
        assert data["total_amount"] == 49.98  # Only successful payments

    def test_get_payment_history_database_error(self, client, valid_token, mock_supabase_service):
        """Test payment history when database fails"""
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception("DB Error")
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            "/api/payments/history/sub-123",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 400
        assert "Error fetching payment history" in response.json()["detail"]

    def test_get_payment_history_with_admin_token(self, client, admin_token, mock_supabase_service):
        """Test admin can access payment history"""
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            "/api/payments/history/sub-123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200

    # ===== PAYMENT STATUS ENDPOINT TESTS =====

    def test_get_payment_status_success(self, client, valid_token, mock_supabase_service):
        """Test getting payment status successfully"""
        payment_id = str(uuid.uuid4())
        mock_response = MagicMock()
        mock_response.data = {
            "id": payment_id,
            "subscription_id": "sub-123",
            "amount": 29.99,
            "status": "success",
            "transaction_id": "TXN-SUCCESS",
            "payment_method": "mock",
            "created_at": "2025-11-17T00:00:00Z"
        }
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            f"/api/payments/status/{payment_id}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == payment_id
        assert data["status"] == "success"

    def test_get_payment_status_not_found(self, client, valid_token, mock_supabase_service):
        """Test getting nonexistent payment status"""
        mock_response = MagicMock()
        mock_response.data = None
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            f"/api/payments/status/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 404
        assert "Payment not found" in response.json()["detail"]

    def test_get_payment_status_database_error(self, client, valid_token, mock_supabase_service):
        """Test payment status when database fails"""
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception("DB Error")
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            f"/api/payments/status/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 404

    def test_get_payment_status_with_admin_token(self, client, admin_token, mock_supabase_service):
        """Test admin can access payment status"""
        payment_id = str(uuid.uuid4())
        mock_response = MagicMock()
        mock_response.data = {
            "id": payment_id,
            "subscription_id": "sub-123",
            "amount": 29.99,
            "status": "success",
            "transaction_id": "TXN-SUCCESS",
            "payment_method": "mock",
            "created_at": "2025-11-17T00:00:00Z"
        }
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response
        mock_supabase_service.table.return_value = mock_table
        
        response = client.get(
            f"/api/payments/status/{payment_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200

    # ===== AUTH/RBAC TESTS =====

    def test_payment_history_without_auth_header(self, client):
        """Test payment history without auth"""
        response = client.get("/api/payments/history/sub-123")
        assert response.status_code in [401, 422]

    def test_payment_history_with_invalid_token(self, client):
        """Test payment history with invalid token"""
        response = client.get(
            "/api/payments/history/sub-123",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    def test_payment_status_without_auth_header(self, client):
        """Test payment status without auth"""
        response = client.get(f"/api/payments/status/{uuid.uuid4()}")
        assert response.status_code in [401, 422]

    def test_payment_status_with_invalid_token(self, client):
        """Test payment status with invalid token"""
        response = client.get(
            f"/api/payments/status/{uuid.uuid4()}",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    def test_payment_history_with_expired_token(self, client):
        """Test payment history with expired token"""
        import jwt
        from datetime import datetime, timedelta, timezone
        from src.config import settings
        
        expired_payload = {
            "user_id": "test-user",
            "role": "subscriber",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        }
        expired_token = jwt.encode(expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        response = client.get(
            "/api/payments/history/sub-123",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
