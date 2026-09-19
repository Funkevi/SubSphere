import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import LoginPage from '../pages/LoginPage';
import * as authApi from '../api/auth';

jest.mock('../api/auth');

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('renders login form with email and password fields', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('displays error message on login failure', async () => {
    authApi.loginUser.mockRejectedValue(new Error('Invalid credentials'));

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'wrong@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  test('successful login as subscriber redirects to dashboard', async () => {
    authApi.loginUser.mockResolvedValue({
      access_token: 'test-token-123',
      user_id: 'user-123',
      email: 'test@example.com',
      role: 'subscriber',
    });

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Password123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('successful login as admin redirects to admin dashboard', async () => {
    authApi.loginUser.mockResolvedValue({
      access_token: 'admin-token-456',
      user_id: 'admin-123',
      email: 'admin@example.com',
      role: 'admin',
    });

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'admin@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'AdminPass123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/admin');
    });
  });

  test('shows loading state during login', async () => {
    authApi.loginUser.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Password123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    expect(screen.getByText(/logging in/i)).toBeInTheDocument();
  });

  test('displays link to registration page', () => {
    render(
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    );

    const registerLink = screen.getByRole('link', { name: /register here/i });
    expect(registerLink).toBeInTheDocument();
    expect(registerLink).toHaveAttribute('href', '/register');
  });
});
