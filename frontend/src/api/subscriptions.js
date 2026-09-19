/**
 * Subscription API Client
 * Handles subscription operations
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Create a new subscription
 * @param {string} planId - Plan UUID
 * @returns {Promise} Created subscription
 */
export async function createSubscription(planId) {
  const token = localStorage.getItem('token');
  const userId = localStorage.getItem('user_id');

  const response = await fetch(`${API_BASE_URL}/api/subscriptions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      subscription: {
        user_id: userId,
        plan_id: planId,
        status: 'active'
      }
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to create subscription');
  }

  return data;
}

/**
 * Get user subscriptions
 * @returns {Promise} List of subscriptions
 */
export async function getUserSubscriptions() {
  const token = localStorage.getItem('token');
  const userId = localStorage.getItem('user_id');

  const response = await fetch(`${API_BASE_URL}/api/subscriptions/user/${userId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch subscriptions');
  }

  return data;
}
