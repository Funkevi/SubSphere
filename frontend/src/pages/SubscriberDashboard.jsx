import React, { useState, useEffect } from 'react';
import { getPlans } from '../api/plans';
import { createMockPayment } from '../api/payments';
import { createSubscription } from '../api/subscriptions';
import './SubscriberDashboard.css';

export default function SubscriberDashboard() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const data = await getPlans();
      setPlans(data);
    } catch (err) {
      setError(err.message || 'Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId, price) => {
    setPaymentStatus('processing');
    setError('');

    try {
      // Step 1: Create subscription
      const subscription = await createSubscription(planId);
      
      // Step 2: Process payment using the subscription ID
      await createMockPayment(subscription.id, price, true);
      
      setPaymentStatus('success');
      setTimeout(() => setPaymentStatus(''), 3000);
    } catch (err) {
      setError(err.message || 'Payment failed');
      setPaymentStatus('failed');
      setTimeout(() => setPaymentStatus(''), 3000);
    }
  };

  if (loading) {
    return <div className="loading">Loading plans...</div>;
  }

  return (
    <div className="subscriber-dashboard">
      <header className="dashboard-header">
        <h1>Subscription Plans</h1>
        <p>Choose the plan that's right for you</p>
      </header>

      {error && <div className="error-banner">{error}</div>}
      {paymentStatus === 'success' && (
        <div className="success-banner">Payment successful! Subscription activated.</div>
      )}
      {paymentStatus === 'processing' && (
        <div className="info-banner">Processing payment...</div>
      )}

      <div className="plans-grid">
        {plans.map((plan) => (
          <div key={plan.id} className={`plan-card ${!plan.is_active ? 'inactive' : ''}`}>
            <h2>{plan.name}</h2>
            <div className="price">
              <span className="currency">$</span>
              <span className="amount">{plan.price}</span>
              <span className="period">/{plan.billing_cycle}</span>
            </div>
            <p className="description">{plan.description}</p>
            <ul className="features">
              {plan.features && Array.isArray(plan.features) && plan.features.length > 0 ? (
                plan.features.map((feature, idx) => (
                  <li key={idx}>
                    ✓ {typeof feature === 'string' ? feature : feature.name || feature.description || 'Feature included'}
                  </li>
                ))
              ) : (
                <li>✓ Standard features included</li>
              )}
            </ul>
            <button
              className="subscribe-btn"
              onClick={() => handleSubscribe(plan.id, plan.price)}
              disabled={!plan.is_active || paymentStatus === 'processing'}
            >
              {plan.is_active ? 'Subscribe Now' : 'Not Available'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
