import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RegisterPage from '../pages/RegisterPage';
import * as authApi from '../api/auth';

jest.mock('../api/auth');

const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('RegisterPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('renders registration form', () => {
    render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  test('shows password strength indicator when typing', () => {
    render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );

    const passwordInput = screen.getByLabelText(/password/i);
    fireEvent.change(passwordInput, { target: { value: 'Weak1!' } });

    expect(screen.getByText(/weak|medium|good|strong/i)).toBeInTheDocument();
  });

  test('displays error on registration failure', async () => {
    authApi.registerUser.mockRejectedValue(new Error('Email already exists'));

    render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Password123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(screen.getByText(/email already exists/i)).toBeInTheDocument();
    });
  });

  test('successful registration stores token and redirects', async () => {
    authApi.registerUser.mockResolvedValue({
      access_token: 'test-token-123',
      user: { id: '1', email: 'test@example.com' },
    });

    render(
      <BrowserRouter>
        <RegisterPage />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'Password123!' },
    });
    fireEvent.click(screen.getByRole('button', { name: /register/i }));

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('test-token-123');
    });
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
  });
});
