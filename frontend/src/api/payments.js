/**
 * Payments API Client
 * Handles mock payment operations
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Create mock payment
 * @param {string} subscriptionId - Subscription UUID
 * @param {number} amount - Payment amount
 * @param {boolean} shouldSucceed - Mock success/failure
 * @returns {Promise} Payment result
 */
export async function createMockPayment(subscriptionId, amount, shouldSucceed = true) {
  const response = await fetch(`${API_BASE_URL}/api/payments/mock`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      payment: {
        subscription_id: subscriptionId,
        amount: amount,
        should_succeed: shouldSucceed,
      },
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Payment failed');
  }

  return data;
}

/**
 * Get payment history for subscription
 * @param {string} subscriptionId - Subscription UUID
 * @returns {Promise} Payment history
 */
export async function getPaymentHistory(subscriptionId) {
  const token = localStorage.getItem('token');

  const response = await fetch(`${API_BASE_URL}/api/payments/history/${subscriptionId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch payment history');
  }

  return data;
}
