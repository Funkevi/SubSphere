"""
Database migrations for Trial Period Activation
"""

CREATE_SUBSCRIPTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES subscription_plans(id),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('trial', 'active', 'paused', 'cancelled', 'payment_failed')),
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    next_billing_date TIMESTAMP WITH TIME ZONE,
    paused_at TIMESTAMP WITH TIME ZONE,
    resumed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, plan_id)
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_trial_end ON subscriptions(trial_end) WHERE status = 'trial';
CREATE INDEX idx_subscriptions_billing_date ON subscriptions(next_billing_date);
"""

def run_migration():
    """Execute migration"""
    from src.auth.supabase_auth import supabase_auth
    
    try:
        # Execute raw SQL
        response = supabase_auth.service_client.query(
            f"PRAGMA foreign_keys = ON; {CREATE_SUBSCRIPTIONS_TABLE}"
        )
        print("✓ Subscriptions table created successfully")
        return True
    except Exception as e:
        print(f"✗ Migration error: {e}")
        return False

if __name__ == "__main__":
    run_migration()