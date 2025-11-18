"""
Payment API Routes
Mock payment processing endpoints for SIM-83
"""
from uuid import uuid4
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Body
from src.models.payment import CreatePaymentRequest, PaymentResponse
from src.auth.supabase_auth import supabase_auth
from src.auth.rbac import require_role

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/mock", response_model=PaymentResponse, status_code=201)
async def mock_payment(
    payment: CreatePaymentRequest = Body(..., embed=True)  # WRAPPED in "payment"
):
    """
    SIM-83: Mock payment endpoint for testing

    - Simulates payment processing without real gateway
    - Returns success or failure based on should_succeed flag
    - Public endpoint (no auth required for testing)
    """
    # Determine payment outcome
    if payment.should_succeed:
        status = "success"
        transaction_id = f"TXN-{str(uuid4())[:8].upper()}"
    else:
        status = "failed"
        transaction_id = None

    try:
        response = supabase_auth.service_client.table("payments").insert({
            "subscription_id": payment.subscription_id,
            "amount": payment.amount,
            "status": status,
            "transaction_id": transaction_id,
            "payment_method": "mock"
        }).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create payment record")

        payment_data = response.data[0]
        return PaymentResponse(**payment_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing payment: {str(e)}") from e


@router.get("/history/{subscription_id}")
@require_role(["admin", "subscriber"])
async def get_payment_history(  # pylint: disable=unused-argument
    subscription_id: str,
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    Get payment history for a subscription

    - Requires authentication (admin or subscriber)
    - Returns all payments ordered by creation date
    """
    try:
        response = supabase_auth.service_client.table("payments").select(
            "*"
        ).eq("subscription_id", subscription_id).order("created_at", desc=True).execute()

        return {
            "subscription_id": subscription_id,
            "payments": response.data,
            "total_payments": len(response.data),
            "total_amount": sum(p["amount"] for p in response.data if p["status"] == "success")
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching payment history: {str(e)}") from e


@router.get("/status/{payment_id}", response_model=PaymentResponse)
@require_role(["admin", "subscriber"])
async def get_payment_status(  # pylint: disable=unused-argument
    payment_id: str,
    authorization: Optional[str] = Header(None),
    token: str = None,
    current_user: dict = None
):
    """
    Get payment status by ID

    - Requires authentication
    - Returns payment details
    """
    try:
        response = supabase_auth.service_client.table("payments").select(
            "*"
        ).eq("id", payment_id).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Payment not found")

        return PaymentResponse(**response.data)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Payment not found") from None
