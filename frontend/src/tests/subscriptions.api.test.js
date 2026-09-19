import * as subscriptionsApi from '../api/subscriptions';

global.fetch = jest.fn();

describe('Subscriptions API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    fetch.mockClear();
  });

  describe('createSubscription', () => {
    test('creates subscription with user and plan IDs', async () => {
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user_id', 'user-123');

      const mockSubscription = {
        id: 'sub-789',
        user_id: 'user-123',
        plan_id: 'plan-456',
        status: 'active',
        started_at: '2025-11-17T00:00:00Z',
        expires_at: '2025-12-17T00:00:00Z',
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSubscription,
      });

      const result = await subscriptionsApi.createSubscription('plan-456');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/subscriptions',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          },
          body: JSON.stringify({
            subscription: {
              user_id: 'user-123',
              plan_id: 'plan-456',
              status: 'active',
            },
          }),
        })
      );
      expect(result).toEqual(mockSubscription);
    });

    test('throws error when creation fails', async () => {
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user_id', 'user-123');

      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid plan ID' }),
      });

      await expect(
        subscriptionsApi.createSubscription('invalid-plan')
      ).rejects.toThrow('Invalid plan ID');
    });
  });

  describe('getUserSubscriptions', () => {
    test('fetches user subscriptions with token', async () => {
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user_id', 'user-123');

      const mockSubscriptions = [
        {
          id: 'sub-1',
          user_id: 'user-123',
          plan_id: 'plan-1',
          status: 'active',
        },
        {
          id: 'sub-2',
          user_id: 'user-123',
          plan_id: 'plan-2',
          status: 'expired',
        },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSubscriptions,
      });

      const result = await subscriptionsApi.getUserSubscriptions();

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/subscriptions/user/user-123',
        expect.objectContaining({
          method: 'GET',
          headers: { Authorization: 'Bearer test-token' },
        })
      );
      expect(result).toEqual(mockSubscriptions);
    });

    test('throws error when fetch fails', async () => {
      localStorage.setItem('token', 'test-token');
      localStorage.setItem('user_id', 'user-123');

      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(subscriptionsApi.getUserSubscriptions()).rejects.toThrow(
        'Unauthorized'
      );
    });

    test('throws error when no token exists', async () => {
      localStorage.setItem('user_id', 'user-123');

      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'No token' }),
      });

      await expect(subscriptionsApi.getUserSubscriptions()).rejects.toThrow(
        'No token'
      );
    });
  });
});
