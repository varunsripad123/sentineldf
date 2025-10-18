"""
Stripe billing integration for SentinelDF.

Handles:
- Creating Stripe customers
- Monthly usage-based billing
- Subscription management
- Invoicing
"""
import os
import stripe
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from backend.database import User, UsageRecord

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_stripe_customer(user: User) -> str:
    """
    Create a Stripe customer for a user.
    
    Returns:
        Stripe customer ID
    """
    customer = stripe.Customer.create(
        email=user.email,
        name=user.name,
        metadata={
            'user_id': user.id,
            'company': user.company or 'Individual'
        }
    )
    
    return customer.id


def calculate_monthly_usage(user_id: int, db: Session, year: int = None, month: int = None) -> dict:
    """
    Calculate total usage and cost for a user in a given month.
    
    Args:
        user_id: User ID
        db: Database session
        year: Year (default: current)
        month: Month (default: current)
        
    Returns:
        Dict with usage statistics and total cost
    """
    now = datetime.utcnow()
    year = year or now.year
    month = month or now.month
    
    # Query usage for the month
    usage = db.query(
        func.count(UsageRecord.id).label('total_calls'),
        func.sum(UsageRecord.documents_scanned).label('total_documents'),
        func.sum(UsageRecord.tokens_used).label('total_tokens'),
        func.sum(UsageRecord.cost_cents).label('total_cost_cents')
    ).filter(
        UsageRecord.user_id == user_id,
        extract('year', UsageRecord.timestamp) == year,
        extract('month', UsageRecord.timestamp) == month
    ).first()
    
    total_calls = usage.total_calls or 0
    total_documents = usage.total_documents or 0
    total_tokens = usage.total_tokens or 0
    total_cost_cents = usage.total_cost_cents or 0
    
    return {
        'year': year,
        'month': month,
        'total_calls': total_calls,
        'total_documents': total_documents,
        'total_tokens': total_tokens,
        'total_cost_cents': total_cost_cents,
        'total_cost_dollars': total_cost_cents / 100.0
    }


def charge_monthly_usage(user: User, db: Session) -> dict:
    """
    Charge user for monthly usage via Stripe.
    
    Args:
        user: User object
        db: Database session
        
    Returns:
        Dict with charge information
    """
    # Calculate usage
    usage = calculate_monthly_usage(user.id, db)
    
    # Get user's subscription tier
    if user.subscription_tier == 'free':
        # Free tier: Only charge for overage
        overage_calls = max(0, usage['total_calls'] - user.monthly_quota)
        if overage_calls == 0:
            return {
                'charged': False,
                'reason': 'Within free quota',
                'usage': usage
            }
        
        # Charge for overage: $0.01 per call
        amount_cents = overage_calls * 1
        description = f"Overage: {overage_calls} API calls beyond free quota"
        
    elif user.subscription_tier == 'pro':
        # Pro tier: Fixed monthly fee + overage
        base_fee_cents = 4900  # $49/month
        pro_quota = 50000
        overage_calls = max(0, usage['total_calls'] - pro_quota)
        overage_cost_cents = overage_calls * 1
        
        amount_cents = base_fee_cents + overage_cost_cents
        description = f"Pro Plan ($49) + Overage ({overage_calls} calls)"
        
    else:  # enterprise
        # Custom pricing - calculate based on usage
        amount_cents = usage['total_cost_cents']
        description = f"Enterprise usage: {usage['total_documents']} documents"
    
    # Don't charge if amount is zero
    if amount_cents == 0:
        return {
            'charged': False,
            'reason': 'No charges',
            'usage': usage
        }
    
    # Create Stripe charge
    try:
        charge = stripe.Charge.create(
            amount=amount_cents,
            currency='usd',
            customer=user.stripe_customer_id,
            description=description,
            metadata={
                'user_id': user.id,
                'year': usage['year'],
                'month': usage['month'],
                'total_calls': usage['total_calls']
            }
        )
        
        return {
            'charged': True,
            'amount_cents': amount_cents,
            'amount_dollars': amount_cents / 100.0,
            'charge_id': charge.id,
            'usage': usage
        }
        
    except stripe.error.StripeError as e:
        return {
            'charged': False,
            'error': str(e),
            'usage': usage
        }


def create_subscription(user: User, price_id: str, db: Session) -> dict:
    """
    Create a Stripe subscription for a user.
    
    Args:
        user: User object
        price_id: Stripe price ID (e.g., for Pro plan)
        db: Database session
        
    Returns:
        Subscription details
    """
    # Create or get Stripe customer
    if not user.stripe_customer_id:
        customer_id = create_stripe_customer(user)
        user.stripe_customer_id = customer_id
        db.commit()
    
    # Create subscription
    subscription = stripe.Subscription.create(
        customer=user.stripe_customer_id,
        items=[{'price': price_id}],
        metadata={
            'user_id': user.id
        }
    )
    
    # Update user tier
    if 'pro' in price_id.lower():
        user.subscription_tier = 'pro'
        user.monthly_quota = 50000
    elif 'enterprise' in price_id.lower():
        user.subscription_tier = 'enterprise'
        user.monthly_quota = 1000000
    
    db.commit()
    
    return {
        'subscription_id': subscription.id,
        'status': subscription.status,
        'current_period_end': subscription.current_period_end
    }


def get_usage_summary(user_id: int, db: Session) -> dict:
    """
    Get user's usage summary for current month.
    
    Returns:
        Summary with quota status and projected cost
    """
    usage = calculate_monthly_usage(user_id, db)
    user = db.query(User).filter(User.id == user_id).first()
    
    quota_remaining = max(0, user.monthly_quota - usage['total_calls'])
    quota_used_percent = (usage['total_calls'] / user.monthly_quota) * 100 if user.monthly_quota > 0 else 0
    
    # Project end-of-month cost
    days_in_month = 30  # Simplified
    current_day = datetime.utcnow().day
    days_remaining = max(0, days_in_month - current_day)
    
    if current_day > 0:
        daily_rate = usage['total_calls'] / current_day
        projected_calls = usage['total_calls'] + (daily_rate * days_remaining)
        projected_cost_cents = projected_calls * 1  # $0.01 per call
    else:
        projected_cost_cents = 0
    
    return {
        'current_usage': usage,
        'quota': {
            'total': user.monthly_quota,
            'used': usage['total_calls'],
            'remaining': quota_remaining,
            'percent_used': round(quota_used_percent, 1)
        },
        'projected': {
            'calls': int(projected_calls) if current_day > 0 else 0,
            'cost_dollars': projected_cost_cents / 100.0
        },
        'subscription_tier': user.subscription_tier
    }


# Pricing tiers (configure in Stripe dashboard)
PRICING_TIERS = {
    'free': {
        'monthly_fee': 0,
        'quota': 1000,
        'overage_per_call': 0.01
    },
    'pro': {
        'monthly_fee': 49,
        'quota': 50000,
        'overage_per_call': 0.01,
        'stripe_price_id': 'price_pro_monthly'  # Set in Stripe
    },
    'enterprise': {
        'monthly_fee': 'custom',
        'quota': 'unlimited',
        'stripe_price_id': 'price_enterprise_monthly'
    }
}


def handle_stripe_webhook(event: dict) -> dict:
    """
    Handle Stripe webhook events.
    
    Common events:
    - invoice.payment_succeeded
    - invoice.payment_failed
    - customer.subscription.deleted
    """
    event_type = event['type']
    
    if event_type == 'invoice.payment_succeeded':
        # Payment successful - nothing to do
        return {'status': 'success'}
        
    elif event_type == 'invoice.payment_failed':
        # Payment failed - suspend user account
        customer_id = event['data']['object']['customer']
        # TODO: Mark user as suspended
        return {'status': 'payment_failed'}
        
    elif event_type == 'customer.subscription.deleted':
        # Subscription cancelled - downgrade to free
        customer_id = event['data']['object']['customer']
        # TODO: Downgrade user to free tier
        return {'status': 'subscription_cancelled'}
    
    return {'status': 'ignored'}
