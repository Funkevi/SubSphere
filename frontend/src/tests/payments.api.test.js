import * as paymentsApi from '../api/payments';

global.fetch = jest.fn();

describe('Payments API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    fetch.mockClear();
  });

  describe('createMockPayment', () => {
    test('creates successful payment', async () => {
      const mockResponse = {
        id: 'payment-123',
        subscription_id: 'sub-456',
        amount: 9.99,
        status: 'success',
        transaction_id: 'TXN-ABC123',
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await paymentsApi.createMockPayment('sub-456', 9.99, true);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/payments/mock',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            payment: {
              subscription_id: 'sub-456',
              amount: 9.99,
              should_succeed: true,
            },
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    test('creates failed payment when shouldSucceed is false', async () => {
      const mockResponse = {
        id: 'payment-124',
        subscription_id: 'sub-456',
        amount: 9.99,
        status: 'failed',
        transaction_id: null,
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await paymentsApi.createMockPayment('sub-456', 9.99, false);

      expect(result.status).toBe('failed');
    });

    test('throws error on payment failure', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Payment processing failed' }),
      });

      await expect(
        paymentsApi.createMockPayment('sub-456', 9.99, true)
      ).rejects.toThrow('Payment processing failed');
    });
  });

  describe('getPaymentHistory', () => {
    test('fetches payment history with authorization', async () => {
      localStorage.setItem('token', 'test-token');
      const mockHistory = {
        subscription_id: 'sub-456',
        payments: [
          { id: 'payment-1', amount: 9.99, status: 'success' },
          { id: 'payment-2', amount: 9.99, status: 'success' },
        ],
        total_payments: 2,
        total_amount: 19.98,
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHistory,
      });

      const result = await paymentsApi.getPaymentHistory('sub-456');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/payments/history/sub-456',
        expect.objectContaining({
          method: 'GET',
          headers: { Authorization: 'Bearer test-token' },
        })
      );
      expect(result).toEqual(mockHistory);
    });

    test('throws error when fetch fails', async () => {
      localStorage.setItem('token', 'test-token');
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Not found' }),
      });

      await expect(paymentsApi.getPaymentHistory('sub-456')).rejects.toThrow(
        'Not found'
      );
    });

    test('throws error when no token exists', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Unauthorized' }),
      });

      await expect(paymentsApi.getPaymentHistory('sub-456')).rejects.toThrow(
        'Unauthorized'
      );
    });
  });
});
