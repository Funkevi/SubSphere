import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPlans, createPlan, updatePlan, deletePlan } from '../api/plans';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    billing_cycle: 'monthly',
    is_active: true,
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

  const handleOpenModal = (plan = null) => {
    if (plan) {
      setEditingPlan(plan);
      setFormData({
        name: plan.name,
        description: plan.description,
        price: plan.price,
        billing_cycle: plan.billing_cycle || 'monthly',
        is_active: plan.is_active,
      });
    } else {
      setEditingPlan(null);
      setFormData({
        name: '',
        description: '',
        price: '',
        billing_cycle: 'monthly',
        is_active: true,
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingPlan(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const planData = {
        ...formData,
        price: parseFloat(formData.price),
      };

      if (editingPlan) {
        await updatePlan(editingPlan.id, planData);
      } else {
        await createPlan(planData);
      }

      await loadPlans();
      handleCloseModal();
    } catch (err) {
      setError(err.message || 'Operation failed');
    }
  };

  const handleDelete = async (planId) => {
    if (!window.confirm('Are you sure you want to delete this plan?')) {
      return;
    }

    try {
      await deletePlan(planId);
      await loadPlans();
    } catch (err) {
      setError(err.message || 'Failed to delete plan');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user_id');
    navigate('/login');
  };

  const filteredPlans = plans.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="admin-dashboard">
      {/* Admin Nav */}
      <nav className="dashboard-nav glass-panel">
        <div className="nav-brand">
          <span className="brand-icon">⚡</span>
          <span className="brand-name">SubSphere</span>
          <span className="badge badge-active">Admin Portal</span>
        </div>
        <div className="user-profile-menu">
          <div className="avatar admin-avatar">AD</div>
          <button onClick={handleLogout} className="btn-secondary logout-btn">Sign Out</button>
        </div>
      </nav>

      <main className="admin-content">
        {/* Revenue Analytics Cards */}
        <section className="metrics-grid">
          <div className="glass-panel metric-card">
            <span className="metric-label">Monthly Recurring Revenue (MRR)</span>
            <div className="metric-value">$14,850.00</div>
            <span className="metric-subtext text-emerald">+12.4% from last month</span>
          </div>

          <div className="glass-panel metric-card">
            <span className="metric-label">Active Subscribers</span>
            <div className="metric-value">1,280</div>
            <span className="metric-subtext text-emerald">95% retention rate</span>
          </div>

          <div className="glass-panel metric-card">
            <span className="metric-label">Annual Run Rate (ARR)</span>
            <div className="metric-value">$178,200.00</div>
            <span className="metric-subtext">Projected annualized ARR</span>
          </div>

          <div className="glass-panel metric-card">
            <span className="metric-label">Platform Churn</span>
            <div className="metric-value">2.4%</div>
            <span className="metric-subtext text-emerald">-0.8% YoY Improvement</span>
          </div>
        </section>

        {/* Header Bar */}
        <header className="admin-header section-header">
          <div>
            <h1>Admin Dashboard</h1>
            <p className="section-subtitle">Manage subscription plans and view revenue metrics</p>
          </div>

          <div className="admin-header-actions">
            <input 
              type="text" 
              className="form-input search-input" 
              placeholder="Search plans..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button className="create-btn btn-primary" onClick={() => handleOpenModal()}>
              + Create Plan
            </button>
          </div>
        </header>

        {error && <div className="error-banner">{error}</div>}

        {/* Plans Table */}
        <div className="plans-table glass-panel table-container">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Price</th>
                <th>Billing Cycle</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPlans.map((plan) => (
                <tr key={plan.id}>
                  <td className="plan-name-cell">
                    <strong>{plan.name}</strong>
                  </td>
                  <td className="desc-cell">{plan.description}</td>
                  <td className="price-cell">${typeof plan.price === 'number' ? plan.price.toFixed(2) : plan.price}</td>
                  <td className="cycle-cell">{plan.billing_cycle || 'monthly'}</td>
                  <td>
                    <span className={`status ${plan.is_active ? 'active' : 'inactive'} badge ${plan.is_active ? 'badge-active' : 'badge-canceled'}`}>
                      {plan.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button className="edit-btn btn-secondary btn-sm" onClick={() => handleOpenModal(plan)}>
                        Edit
                      </button>
                      <button className="delete-btn btn-outline-danger btn-sm" onClick={() => handleDelete(plan.id)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Create/Edit Modal */}
        {showModal && (
          <div className="modal-overlay" onClick={handleCloseModal}>
            <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>{editingPlan ? 'Edit Plan' : 'Create Plan'}</h2>
                <button className="close-btn" onClick={handleCloseModal}>×</button>
              </div>

              <form onSubmit={handleSubmit} className="modal-form">
                <div className="form-group">
                  <label className="form-label">Name</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Plan Name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea
                    className="form-input"
                    rows="3"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Plan Description"
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Price</label>
                    <input
                      type="number"
                      step="0.01"
                      className="form-input"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                      placeholder="Price"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Billing Cycle</label>
                    <select
                      className="form-select"
                      value={formData.billing_cycle}
                      onChange={(e) => setFormData({ ...formData, billing_cycle: e.target.value })}
                    >
                      <option value="monthly">Monthly</option>
                      <option value="yearly">Yearly</option>
                    </select>
                  </div>
                </div>

                <div className="form-group checkbox checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    />
                    <span>Active</span>
                  </label>
                </div>

                <div className="modal-actions">
                  <button type="button" onClick={handleCloseModal} className="cancel-btn btn-secondary">
                    Cancel
                  </button>
                  <button type="submit" className="save-btn btn-primary">
                    {editingPlan ? 'Update' : 'Create'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
