import * as authApi from '../api/auth';

// Mock fetch globally
global.fetch = jest.fn();

describe('Auth API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    fetch.mockClear();
  });

  describe('registerUser', () => {
    test('sends correct request for registration', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'test-token',
          user_id: 'user-123',
          email: 'test@example.com',
          role: 'subscriber',
        }),
      });

      const result = await authApi.registerUser('test@example.com', 'Password123!');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/register',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'Password123!',
          }),
        })
      );
      expect(result.access_token).toBe('test-token');
    });

    test('throws error on registration failure', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email already exists' }),
      });

      await expect(
        authApi.registerUser('test@example.com', 'Password123!')
      ).rejects.toThrow('Email already exists');
    });

    test('throws generic error when no detail provided', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      await expect(
        authApi.registerUser('test@example.com', 'Password123!')
      ).rejects.toThrow('Registration failed');
    });
  });

  describe('loginUser', () => {
    test('stores token and user data on successful login', async () => {
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'login-token',
          user_id: 'user-456',
          email: 'login@example.com',
          role: 'subscriber',
        }),
      });

      await authApi.loginUser('login@example.com', 'Password123!');

      expect(localStorage.getItem('token')).toBe('login-token');
      expect(localStorage.getItem('user_id')).toBe('user-456');
      expect(localStorage.getItem('role')).toBe('subscriber');
      expect(localStorage.getItem('email')).toBe('login@example.com');
    });

    test('throws error on invalid credentials', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid credentials' }),
      });

      await expect(
        authApi.loginUser('wrong@example.com', 'wrongpass')
      ).rejects.toThrow('Invalid credentials');
    });

    test('throws generic error when no detail provided', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      await expect(
        authApi.loginUser('wrong@example.com', 'wrongpass')
      ).rejects.toThrow('Login failed');
    });
  });

  describe('getCurrentUser', () => {
    test('sends token in authorization header', async () => {
      localStorage.setItem('token', 'test-token');
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 'user-123',
          email: 'test@example.com',
          role: 'subscriber',
        }),
      });

      await authApi.getCurrentUser();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/me',
        expect.objectContaining({
          headers: { Authorization: 'Bearer test-token' },
        })
      );
    });

    test('throws error when no token exists', async () => {
      await expect(authApi.getCurrentUser()).rejects.toThrow('No token found');
    });

    test('throws error when request fails', async () => {
      localStorage.setItem('token', 'test-token');
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(authApi.getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('logoutUser', () => {
    test('clears all localStorage data', () => {
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user_id', 'user-123');
      localStorage.setItem('role', 'subscriber');
      localStorage.setItem('email', 'test@example.com');

      delete window.location;
      window.location = { href: '' };

      authApi.logoutUser();

      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('user_id')).toBeNull();
      expect(localStorage.getItem('role')).toBeNull();
      expect(localStorage.getItem('email')).toBeNull();
    });
  });
});
