"""
Unit tests for plan models and validation
"""
import pytest
from src.models.plan import CreatePlanRequest, UpdatePlanRequest, PlanFeature
from pydantic import ValidationError


class TestPlanModels:
    """Unit tests for plan validation"""

    def test_create_plan_valid(self):
        """Test valid plan creation data"""
        plan = CreatePlanRequest(
            name="Basic Plan",
            description="A basic subscription",
            price=9.99,
            duration_days=30,
            features=[
                PlanFeature(name="Feature 1", description="Description 1"),
                PlanFeature(name="Feature 2")
            ]
        )
        assert plan.name == "Basic Plan"
        assert plan.price == 9.99
        assert plan.duration_days == 30
        assert len(plan.features) == 2

    def test_create_plan_minimal(self):
        """Test plan with minimal required fields"""
        plan = CreatePlanRequest(
            name="Minimal Plan",
            price=5.00,
            duration_days=7
        )
        assert plan.name == "Minimal Plan"
        assert plan.features == []

    def test_create_plan_invalid_price_negative(self):
        """Test plan with negative price"""
        with pytest.raises(ValidationError) as exc_info:
            CreatePlanRequest(
                name="Plan",
                price=-9.99,  # Negative price
                duration_days=30
            )
        assert "greater than 0" in str(exc_info.value)

    def test_create_plan_invalid_price_zero(self):
        """Test plan with zero price"""
        with pytest.raises(ValidationError):
            CreatePlanRequest(
                name="Plan",
                price=0,  # Zero price
                duration_days=30
            )

    def test_create_plan_invalid_duration_zero(self):
        """Test plan with zero duration"""
        with pytest.raises(ValidationError):
            CreatePlanRequest(
                name="Plan",
                price=9.99,
                duration_days=0  # Invalid duration
            )

    def test_create_plan_invalid_duration_negative(self):
        """Test plan with negative duration"""
        with pytest.raises(ValidationError):
            CreatePlanRequest(
                name="Plan",
                price=9.99,
                duration_days=-30
            )

    def test_create_plan_empty_name(self):
        """Test plan with empty name"""
        with pytest.raises(ValidationError):
            CreatePlanRequest(
                name="",  # Empty name
                price=9.99,
                duration_days=30
            )

    def test_update_plan_partial(self):
        """Test update with partial fields"""
        update = UpdatePlanRequest(
            name="Updated Plan",
            price=19.99
        )
        assert update.name == "Updated Plan"
        assert update.price == 19.99
        assert update.duration_days is None  # Not updated

    def test_update_plan_is_active(self):
        """Test updating is_active status"""
        update = UpdatePlanRequest(is_active=False)
        assert update.is_active is False

    def test_plan_feature_valid(self):
        """Test valid plan feature"""
        feature = PlanFeature(
            name="Premium Feature",
            description="A premium feature"
        )
        assert feature.name == "Premium Feature"
        assert feature.description == "A premium feature"

    def test_plan_feature_without_description(self):
        """Test feature without description"""
        feature = PlanFeature(name="Basic Feature")
        assert feature.name == "Basic Feature"
        assert feature.description is None
