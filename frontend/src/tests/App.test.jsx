import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock child components
jest.mock('../pages/RegisterPage', () => {
  return function RegisterPage() {
    return <div>RegisterPage</div>;
  };
});

jest.mock('../pages/LoginPage', () => {
  return function LoginPage() {
    return <div>LoginPage</div>;
  };
});

jest.mock('../pages/SubscriberDashboard', () => {
  return function SubscriberDashboard() {
    return <div>SubscriberDashboard</div>;
  };
});

jest.mock('../pages/AdminDashboard', () => {
  return function AdminDashboard() {
    return <div>AdminDashboard</div>;
  };
});

describe('App Routing', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('redirects to login when accessing root', () => {
    render(<App />);
    expect(screen.getByText('LoginPage')).toBeInTheDocument();
  });

  test('shows login page at /login route', () => {
    window.history.pushState({}, 'Login', '/login');
    render(<App />);
    expect(screen.getByText('LoginPage')).toBeInTheDocument();
  });

  test('shows register page at /register route', () => {
    window.history.pushState({}, 'Register', '/register');
    render(<App />);
    expect(screen.getByText('RegisterPage')).toBeInTheDocument();
  });

  test('redirects to login when accessing dashboard without token', () => {
    window.history.pushState({}, 'Dashboard', '/dashboard');
    render(<App />);
    expect(screen.getByText('LoginPage')).toBeInTheDocument();
  });

  test('shows dashboard when logged in', () => {
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('role', 'subscriber');
    window.history.pushState({}, 'Dashboard', '/dashboard');
    render(<App />);
    expect(screen.getByText('SubscriberDashboard')).toBeInTheDocument();
  });

  test('redirects non-admin users from admin dashboard', () => {
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('role', 'subscriber');
    window.history.pushState({}, 'Admin', '/admin');
    render(<App />);
    expect(screen.getByText('SubscriberDashboard')).toBeInTheDocument();
  });

  test('shows admin dashboard for admin users', () => {
    localStorage.setItem('token', 'admin-token');
    localStorage.setItem('role', 'admin');
    window.history.pushState({}, 'Admin', '/admin');
    render(<App />);
    expect(screen.getByText('AdminDashboard')).toBeInTheDocument();
  });
});
