import React, { useState, useEffect } from 'react';
import { getPlans, createPlan, updatePlan, deletePlan } from '../api/plans';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    billing_cycle: 'monthly',
    is_active: true,
  });

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

  const handleOpenModal = (plan = null) => {
    if (plan) {
      setEditingPlan(plan);
      setFormData({
        name: plan.name,
        description: plan.description,
        price: plan.price,
        billing_cycle: plan.billing_cycle,
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

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>Admin Dashboard</h1>
        <button className="create-btn" onClick={() => handleOpenModal()}>
          + Create Plan
        </button>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="plans-table">
        <table>
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
            {plans.map((plan) => (
              <tr key={plan.id}>
                <td>{plan.name}</td>
                <td>{plan.description}</td>
                <td>${plan.price}</td>
                <td>{plan.billing_cycle}</td>
                <td>
                  <span className={`status ${plan.is_active ? 'active' : 'inactive'}`}>
                    {plan.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <button
                    className="edit-btn"
                    onClick={() => handleOpenModal(plan)}
                  >
                    Edit
                  </button>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(plan.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{editingPlan ? 'Edit Plan' : 'Create Plan'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Price</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Billing Cycle</label>
                <select
                  value={formData.billing_cycle}
                  onChange={(e) => setFormData({ ...formData, billing_cycle: e.target.value })}
                >
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>

              <div className="form-group checkbox">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                  Active
                </label>
              </div>

              <div className="modal-actions">
                <button type="button" onClick={handleCloseModal} className="cancel-btn">
                  Cancel
                </button>
                <button type="submit" className="save-btn">
                  {editingPlan ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
