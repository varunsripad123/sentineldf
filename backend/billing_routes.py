"""
Billing and usage API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db, User
from backend.auth import verify_api_key
from backend.billing import (
    get_usage_summary,
    calculate_monthly_usage,
    create_subscription,
    charge_monthly_usage,
    PRICING_TIERS
)

router = APIRouter(prefix="/v1/billing", tags=["Billing"])


class SubscriptionRequest(BaseModel):
    tier: str  # 'pro' or 'enterprise'
    payment_method_id: str  # Stripe payment method ID


# --- Endpoints ---

@router.get("/usage")
async def get_my_usage(
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Get current month's usage and quota status.
    
    Returns:
        - Current usage (calls, documents, cost)
        - Quota status (used, remaining, %)
        - Projected end-of-month cost
    """
    user, _ = auth
    
    summary = get_usage_summary(user.id, db)
    
    return summary


@router.get("/usage/history")
async def get_usage_history(
    months: int = 6,
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Get usage history for past N months.
    """
    user, _ = auth
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    history = []
    now = datetime.utcnow()
    
    for i in range(months):
        date = now - relativedelta(months=i)
        usage = calculate_monthly_usage(user.id, db, date.year, date.month)
        history.append(usage)
    
    return {
        'history': history,
        'subscription_tier': user.subscription_tier
    }


@router.get("/pricing")
async def get_pricing():
    """
    Get pricing tiers and plans.
    
    Public endpoint - no authentication required.
    """
    return {
        'tiers': PRICING_TIERS,
        'currency': 'USD'
    }


@router.post("/subscribe")
async def subscribe_to_plan(
    request: SubscriptionRequest,
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Subscribe to a paid plan (Pro or Enterprise).
    
    Requires:
    - tier: 'pro' or 'enterprise'
    - payment_method_id: Stripe payment method
    """
    user, _ = auth
    
    if request.tier not in ['pro', 'enterprise']:
        raise HTTPException(400, "Invalid tier. Must be 'pro' or 'enterprise'")
    
    # Get Stripe price ID for tier
    price_id = PRICING_TIERS[request.tier].get('stripe_price_id')
    if not price_id:
        raise HTTPException(400, "Price not configured for this tier")
    
    try:
        result = create_subscription(user, price_id, db)
        return {
            'success': True,
            'subscription': result,
            'new_tier': user.subscription_tier,
            'new_quota': user.monthly_quota
        }
    except Exception as e:
        raise HTTPException(500, f"Subscription failed: {str(e)}")


@router.post("/charge")
async def charge_user_monthly(
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Charge user for current month's usage.
    
    Note: This is typically called automatically at end of month.
    """
    user, _ = auth
    
    result = charge_monthly_usage(user, db)
    
    return result


@router.get("/invoice/{year}/{month}")
async def get_monthly_invoice(
    year: int,
    month: int,
    auth: tuple = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Get detailed invoice for a specific month.
    """
    user, _ = auth
    
    if month < 1 or month > 12:
        raise HTTPException(400, "Invalid month")
    
    usage = calculate_monthly_usage(user.id, db, year, month)
    
    # Calculate charges
    base_fee = 0
    overage_fee = 0
    
    if user.subscription_tier == 'pro':
        base_fee = 49.00
        overage_calls = max(0, usage['total_calls'] - 50000)
        overage_fee = overage_calls * 0.01
    elif user.subscription_tier == 'free':
        overage_calls = max(0, usage['total_calls'] - user.monthly_quota)
        overage_fee = overage_calls * 0.01
    
    total = base_fee + overage_fee
    
    return {
        'invoice': {
            'year': year,
            'month': month,
            'user': {
                'email': user.email,
                'company': user.company,
                'tier': user.subscription_tier
            },
            'usage': usage,
            'charges': {
                'base_fee': base_fee,
                'overage_fee': overage_fee,
                'total': total
            }
        }
    }
