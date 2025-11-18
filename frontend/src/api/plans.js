/**
 * Plans API Client
 * Handles subscription plan operations
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Get all active plans
 * @returns {Promise} List of plans
 */
export async function getPlans() {
  const response = await fetch(`${API_BASE_URL}/api/plans`);
  
  if (!response.ok) {
    throw new Error('Failed to fetch plans');
  }

  return response.json();
}

/**
 * Get plan by ID
 * @param {string} planId - Plan UUID
 * @returns {Promise} Plan details
 */
export async function getPlanById(planId) {
  const response = await fetch(`${API_BASE_URL}/api/plans/${planId}`);
  
  if (!response.ok) {
    throw new Error('Plan not found');
  }

  return response.json();
}

/**
 * Create new plan (Admin only)
 * @param {Object} planData - Plan details
 * @returns {Promise} Created plan
 */
export async function createPlan(planData) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}/api/plans`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ plan: planData }), // Wrapped in "plan"
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to create plan');
  }

  return data;
}

/**
 * Update plan (Admin only)
 * @param {string} planId - Plan UUID
 * @param {Object} updates - Plan updates
 * @returns {Promise} Updated plan
 */
export async function updatePlan(planId, updates) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}/api/plans/${planId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ plan: updates }), // Wrapped in "plan"
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to update plan');
  }

  return data;
}

/**
 * Delete plan (Admin only)
 * @param {string} planId - Plan UUID
 * @returns {Promise} Success
 */
export async function deletePlan(planId) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}/api/plans/${planId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to delete plan');
  }

  return true;
}
