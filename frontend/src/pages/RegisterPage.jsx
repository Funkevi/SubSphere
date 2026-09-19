import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import PasswordStrengthIndicator from '../components/PasswordStrengthIndicator';
import { registerUser } from '../api/auth';
import './RegisterPage.css';

export default function RegisterPage() {
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
      const data = await registerUser(email, password);
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', 'subscriber');
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
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
          <p className="brand-tagline">Create Your Subscriber Account</p>
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
            <PasswordStrengthIndicator password={password} />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="btn-primary auth-submit-btn">
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <div className="login-link auth-footer">
          Already have an account?{' '}
          <Link to="/login" className="auth-link">Login here</Link>
        </div>
      </div>
    </div>
  );
}
