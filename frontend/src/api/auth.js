/**
 * Authentication API Client
 * Handles registration, login, and user info
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Register a new user
 * @param {string} email - User email
 * @param {string} password - User password (must have uppercase, digit, special char)
 * @returns {Promise} Registration response
 */
export async function registerUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Registration failed');
  }

  return data;
}

/**
 * Login user
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} Login response with access_token
 */
export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Login failed');
  }

  // Store token in localStorage
  if (data.access_token) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user_id', data.user_id);
    localStorage.setItem('role', data.role);
    localStorage.setItem('email', data.email);
  }

  return data;
}

/**
 * Get current user info
 * @returns {Promise} User data
 */
export async function getCurrentUser() {
  const token = localStorage.getItem('token');

  if (!token) {
    throw new Error('No token found');
  }

  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || 'Failed to fetch user');
  }

  return data;
}

/**
 * Logout user
 */
export function logoutUser() {
  localStorage.removeItem('token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('role');
  localStorage.removeItem('email');
  window.location.href = '/login';
}
