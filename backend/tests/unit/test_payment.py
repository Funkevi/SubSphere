"""
Unit tests for payment models and validation
"""
import pytest
from src.models.payment import CreatePaymentRequest
from pydantic import ValidationError


class TestPaymentModels:
    """Unit tests for payment validation"""

    def test_create_payment_valid(self):
        """Test valid payment creation"""
        payment = CreatePaymentRequest(
            subscription_id="550e8400-e29b-41d4-a716-446655440000",
            amount=29.99,
            should_succeed=True
        )
        assert payment.amount == 29.99
        assert payment.should_succeed is True
        assert payment.subscription_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_create_payment_default_success(self):
        """Test default should_succeed is True"""
        payment = CreatePaymentRequest(
            subscription_id="550e8400-e29b-41d4-a716-446655440000",
            amount=49.99
        )
        assert payment.should_succeed is True

    def test_create_payment_invalid_amount_negative(self):
        """Test payment with negative amount"""
        with pytest.raises(ValidationError) as exc_info:
            CreatePaymentRequest(
                subscription_id="550e8400-e29b-41d4-a716-446655440000",
                amount=-10.00
            )
        assert "greater than 0" in str(exc_info.value)

    def test_create_payment_invalid_amount_zero(self):
        """Test payment with zero amount"""
        with pytest.raises(ValidationError):
            CreatePaymentRequest(
                subscription_id="550e8400-e29b-41d4-a716-446655440000",
                amount=0
            )

    def test_create_payment_missing_subscription_id(self):
        """Test payment without subscription_id"""
        with pytest.raises(ValidationError):
            CreatePaymentRequest(amount=29.99)

    def test_create_payment_failure_flag(self):
        """Test payment with failure flag"""
        payment = CreatePaymentRequest(
            subscription_id="550e8400-e29b-41d4-a716-446655440000",
            amount=29.99,
            should_succeed=False
        )
        assert payment.should_succeed is False

    def test_create_payment_large_amount(self):
        """Test payment with large amount"""
        payment = CreatePaymentRequest(
            subscription_id="550e8400-e29b-41d4-a716-446655440000",
            amount=9999.99
        )
        assert payment.amount == 9999.99
