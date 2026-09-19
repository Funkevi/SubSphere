import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPlans } from '../api/plans';
import { createMockPayment } from '../api/payments';
import { createSubscription } from '../api/subscriptions';
import './SubscriberDashboard.css';

export default function SubscriberDashboard() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');
  const [activeTab, setActiveTab] = useState('plans'); // 'plans' | 'subscriptions'
  const [billingCycle, setBillingCycle] = useState('monthly'); // 'monthly' | 'annual'
  const [activeSub, setActiveSub] = useState({
    id: 'sub-demo-001',
    planName: 'Professional',
    price: 29.99,
    status: 'active',
    renewalDate: '2026-10-19',
    billingCycle: 'monthly'
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const data = await getPlans();
      if (data && Array.isArray(data)) {
        setPlans(data);
      }
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
      setActiveSub({
        id: subscription.id,
        planName: plans.find(p => p.id === planId)?.name || 'Active Plan',
        price: price,
        status: 'active',
        renewalDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        billingCycle: 'monthly'
      });
      setTimeout(() => setPaymentStatus(''), 4000);
    } catch (err) {
      setError(err.message || 'Payment failed');
      setPaymentStatus('failed');
      setTimeout(() => setPaymentStatus(''), 4000);
    }
  };

  const handleToggleSubStatus = () => {
    if (activeSub.status === 'active') {
      setActiveSub({ ...activeSub, status: 'paused' });
    } else {
      setActiveSub({ ...activeSub, status: 'active' });
    }
  };

  const handleCancelSub = () => {
    if (window.confirm('Are you sure you want to cancel your subscription?')) {
      setActiveSub({ ...activeSub, status: 'canceled' });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    navigate('/login');
  };

  if (loading) {
    return <div className="loading">Loading plans...</div>;
  }

  return (
    <div className="subscriber-dashboard">
      {/* Top Navbar */}
      <nav className="dashboard-nav glass-panel">
        <div className="nav-brand">
          <span className="brand-icon">⚡</span>
          <span className="brand-name">SubSphere</span>
          <span className="badge badge-trialing">Subscriber Workspace</span>
        </div>
        <div className="nav-links">
          <button 
            className={`nav-tab ${activeTab === 'plans' ? 'active' : ''}`}
            onClick={() => setActiveTab('plans')}
          >
            Explore Plans
          </button>
          <button 
            className={`nav-tab ${activeTab === 'subscriptions' ? 'active' : ''}`}
            onClick={() => setActiveTab('subscriptions')}
          >
            My Subscription {activeSub.status === 'active' && <span className="indicator-dot"></span>}
          </button>
        </div>
        <div className="user-profile-menu">
          <div className="avatar">JS</div>
          <button onClick={handleLogout} className="btn-secondary logout-btn">Sign Out</button>
        </div>
      </nav>

      {/* Main Workspace */}
      <main className="dashboard-content">
        {/* Banner Messages */}
        {error && <div className="error-banner">{error}</div>}
        {paymentStatus === 'success' && (
          <div className="success-banner">Payment successful! Subscription activated.</div>
        )}
        {paymentStatus === 'processing' && (
          <div className="info-banner">Processing payment...</div>
        )}

        {/* Metric Summary Cards */}
        <section className="metrics-grid">
          <div className="glass-panel metric-card">
            <span className="metric-label">Current Plan</span>
            <div className="metric-value">{activeSub.planName}</div>
            <span className={`badge badge-${activeSub.status}`}>{activeSub.status}</span>
          </div>

          <div className="glass-panel metric-card">
            <span className="metric-label">Monthly Rate</span>
            <div className="metric-value">${activeSub.price ? activeSub.price.toFixed(2) : '0.00'}</div>
            <span className="metric-subtext">Billed {activeSub.billingCycle}</span>
          </div>

          <div className="glass-panel metric-card">
            <span className="metric-label">Next Renewal</span>
            <div className="metric-value">{activeSub.renewalDate}</div>
            <span className="metric-subtext">Auto-renew enabled</span>
          </div>

          <div className="glass-panel metric-card">
            <span className="metric-label">Account Health</span>
            <div className="metric-value text-emerald">Good Status</div>
            <span className="metric-subtext">Payment Method Verified</span>
          </div>
        </section>

        {/* Tab 1: Explore Plans */}
        {activeTab === 'plans' && (
          <section className="plans-section">
            <div className="section-header">
              <div>
                <h2>Subscription Plans</h2>
                <p className="section-subtitle">Choose the plan that's right for you</p>
              </div>

              {/* Billing Cycle Toggle */}
              <div className="cycle-toggle-container glass-panel">
                <button 
                  className={`toggle-btn ${billingCycle === 'monthly' ? 'active' : ''}`}
                  onClick={() => setBillingCycle('monthly')}
                >
                  Monthly
                </button>
                <button 
                  className={`toggle-btn ${billingCycle === 'annual' ? 'active' : ''}`}
                  onClick={() => setBillingCycle('annual')}
                >
                  Annual <span className="discount-tag">Save 20%</span>
                </button>
              </div>
            </div>

            <div className="plans-grid">
              {plans.map((plan) => {
                const adjustedPrice = billingCycle === 'annual' ? (plan.price * 0.8).toFixed(2) : plan.price;

                return (
                  <div 
                    key={plan.id} 
                    className={`glass-panel plan-card ${!plan.is_active ? 'inactive' : ''}`}
                  >
                    <div className="plan-header">
                      <h2>{plan.name}</h2>
                      <p className="plan-description">{plan.description}</p>
                    </div>

                    <div className="price-container">
                      <span className="currency">$</span>
                      <span className="amount">{adjustedPrice}</span>
                      <span className="period">/{plan.billing_cycle || 'month'}</span>
                    </div>

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
                      className="subscribe-btn btn-primary plan-action-btn"
                      onClick={() => handleSubscribe(plan.id, plan.price)}
                      disabled={!plan.is_active || paymentStatus === 'processing'}
                    >
                      {plan.is_active ? 'Subscribe Now' : 'Not Available'}
                    </button>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Tab 2: My Active Subscriptions */}
        {activeTab === 'subscriptions' && (
          <section className="subscriptions-section">
            <div className="section-header">
              <h2>My Subscription</h2>
              <p className="section-subtitle">Manage billing status and subscription features</p>
            </div>

            <div className="glass-panel sub-detail-card">
              <div className="sub-header-row">
                <div>
                  <h3 className="sub-title">{activeSub.planName}</h3>
                  <p className="sub-id">Subscription ID: {activeSub.id}</p>
                </div>
                <span className={`badge badge-${activeSub.status}`}>{activeSub.status}</span>
              </div>

              <div className="sub-meta-grid">
                <div className="meta-item">
                  <span className="meta-label">Billing Amount</span>
                  <span className="meta-value">${activeSub.price ? activeSub.price.toFixed(2) : '0.00'} / {activeSub.billingCycle}</span>
                </div>

                <div className="meta-item">
                  <span className="meta-label">Next Renewal Date</span>
                  <span className="meta-value">{activeSub.renewalDate}</span>
                </div>

                <div className="meta-item">
                  <span className="meta-label">Payment Method</span>
                  <span className="meta-value">💳 Visa ending in 4242</span>
                </div>
              </div>

              <div className="sub-actions">
                <button onClick={handleToggleSubStatus} className="btn-secondary">
                  {activeSub.status === 'active' ? 'Pause Subscription' : 'Resume Subscription'}
                </button>
                <button onClick={handleCancelSub} className="btn-outline-danger">
                  Cancel Subscription
                </button>
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
