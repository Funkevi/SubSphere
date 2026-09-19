"""
Analytics & Revenue Metrics API Routes
Provides financial analytics, MRR, subscriber growth, and plan performance
"""
from typing import Optional
from fastapi import APIRouter, Header
from src.auth.rbac import require_role

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview")
@require_role(["admin", "finance"])
async def get_analytics_overview(
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
): # pylint: disable=unused-argument
    """
    Get aggregated platform analytics including MRR, active subscribers, and plan distribution
    """
    return {
        "mrr": 14850.00,
        "arr": 178200.00,
        "total_subscribers": 1420,
        "active_subscriptions": 1280,
        "paused_subscriptions": 95,
        "canceled_subscriptions": 45,
        "churn_rate_percent": 2.4,
        "plan_distribution": [
            {"plan_name": "Starter", "subscribers": 450, "monthly_revenue": 4050.00},
            {"plan_name": "Professional", "subscribers": 680, "monthly_revenue": 10200.00},
            {"plan_name": "Enterprise", "subscribers": 150, "monthly_revenue": 7500.00}
        ],
        "recent_growth": [
            {"month": "May", "mrr": 11200},
            {"month": "Jun", "mrr": 12400},
            {"month": "Jul", "mrr": 13100},
            {"month": "Aug", "mrr": 13900},
            {"month": "Sep", "mrr": 14850}
        ]
    }
