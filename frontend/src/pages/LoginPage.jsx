import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../api/auth';
import './LoginPage.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await loginUser(email, password);
      if (data.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (role) => {
    if (role === 'admin') {
      localStorage.setItem('token', 'mock-admin-jwt-token');
      localStorage.setItem('user_id', 'admin-user-001');
      localStorage.setItem('role', 'admin');
      navigate('/admin');
    } else {
      localStorage.setItem('token', 'mock-subscriber-jwt-token');
      localStorage.setItem('user_id', 'user-12345');
      localStorage.setItem('role', 'subscriber');
      navigate('/dashboard');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card glass-panel">
        <div className="brand-header">
          <div className="brand-logo">
            <span className="logo-pulse">⚡</span>
          </div>
          <h2>SubSphere</h2>
          <p className="brand-tagline">Subscription & Billing Intelligence Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@company.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary auth-submit-btn">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="demo-credentials-box">
          <span className="demo-label">Instant Demo Access:</span>
          <div className="demo-actions">
            <button type="button" onClick={() => handleQuickDemo('subscriber')} className="demo-badge subscriber">
              👤 Demo Subscriber
            </button>
            <button type="button" onClick={() => handleQuickDemo('admin')} className="demo-badge admin">
              👑 Demo Admin
            </button>
          </div>
        </div>

        <div className="register-link auth-footer">
          Don't have an account?{' '}
          <Link to="/register" className="auth-link">Register here</Link>
        </div>
      </div>
    </div>
  );
}
