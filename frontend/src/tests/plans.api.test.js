import * as plansApi from '../api/plans';

global.fetch = jest.fn();

describe('Plans API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    fetch.mockClear();
  });

  describe('getPlans', () => {
    test('fetches all plans successfully', async () => {
      const mockPlans = [
        { id: 'plan-1', name: 'Basic', price: 9.99 },
        { id: 'plan-2', name: 'Premium', price: 19.99 },
      ];

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPlans,
      });

      const result = await plansApi.getPlans();

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/plans');
      expect(result).toEqual(mockPlans);
    });

    test('throws error when fetch fails', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
      });

      await expect(plansApi.getPlans()).rejects.toThrow('Failed to fetch plans');
    });
  });

  describe('getPlanById', () => {
    test('fetches single plan by ID', async () => {
      const mockPlan = { id: 'plan-1', name: 'Basic', price: 9.99 };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPlan,
      });

      const result = await plansApi.getPlanById('plan-1');

      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/plans/plan-1');
      expect(result).toEqual(mockPlan);
    });

    test('throws error when plan not found', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
      });

      await expect(plansApi.getPlanById('invalid-id')).rejects.toThrow('Plan not found');
    });
  });

  describe('createPlan', () => {
    test('creates plan with authorization token', async () => {
      localStorage.setItem('token', 'admin-token');
      const planData = {
        name: 'New Plan',
        description: 'Test plan',
        price: 14.99,
        duration_days: 30,
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'plan-3', ...planData }),
      });

      await plansApi.createPlan(planData);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/plans',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: 'Bearer admin-token',
          },
          body: JSON.stringify({ plan: planData }),
        })
      );
    });

    test('throws error with detail message when creation fails', async () => {
      localStorage.setItem('token', 'admin-token');
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Invalid plan data' }),
      });

      await expect(plansApi.createPlan({})).rejects.toThrow('Invalid plan data');
    });

    test('throws generic error when no detail provided', async () => {
      localStorage.setItem('token', 'admin-token');
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      await expect(plansApi.createPlan({})).rejects.toThrow('Failed to create plan');
    });
  });

  describe('updatePlan', () => {
    test('updates plan with correct data', async () => {
      localStorage.setItem('token', 'admin-token');
      const updates = { name: 'Updated Plan', price: 24.99 };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'plan-1', ...updates }),
      });

      await plansApi.updatePlan('plan-1', updates);

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/plans/plan-1',
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({ plan: updates }),
        })
      );
    });

    test('throws error with detail message when update fails', async () => {
      localStorage.setItem('token', 'admin-token');
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Plan not found' }),
      });

      await expect(plansApi.updatePlan('plan-1', {})).rejects.toThrow('Plan not found');
    });

    test('throws generic error when no detail provided', async () => {
      localStorage.setItem('token', 'admin-token');
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({}),
      });

      await expect(plansApi.updatePlan('plan-1', {})).rejects.toThrow('Failed to update plan');
    });
  });

  describe('deletePlan', () => {
    test('deletes plan successfully', async () => {
      localStorage.setItem('token', 'admin-token');

      fetch.mockResolvedValueOnce({
        ok: true,
      });

      const result = await plansApi.deletePlan('plan-1');

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/plans/plan-1',
        expect.objectContaining({
          method: 'DELETE',
          headers: { Authorization: 'Bearer admin-token' },
        })
      );
      expect(result).toBe(true);
    });
  });
});
