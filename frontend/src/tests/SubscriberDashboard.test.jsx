import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SubscriberDashboard from '../pages/SubscriberDashboard';
import * as plansApi from '../api/plans';
import * as paymentsApi from '../api/payments';
import * as subscriptionsApi from '../api/subscriptions';

jest.mock('../api/plans');
jest.mock('../api/payments');
jest.mock('../api/subscriptions');

describe('SubscriberDashboard', () => {
  const mockPlans = [
    {
      id: 'plan-1',
      name: 'Basic Plan',
      description: 'Basic features',
      price: 9.99,
      duration_days: 30,
      is_active: true,
      features: ['Feature 1', 'Feature 2'],
    },
    {
      id: 'plan-2',
      name: 'Premium Plan',
      description: 'Premium features',
      price: 19.99,
      duration_days: 30,
      is_active: true,
      features: ['Feature 1', 'Feature 2', 'Feature 3'],
    },
    {
      id: 'plan-3',
      name: 'Inactive Plan',
      description: 'Not available',
      price: 29.99,
      duration_days: 30,
      is_active: false,
      features: [],
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('user_id', 'user-123');
  });

  afterEach(() => {
    localStorage.clear();
  });

  test('displays loading state initially', () => {
    plansApi.getPlans.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    expect(screen.getByText(/loading plans/i)).toBeInTheDocument();
  });

  test('displays plans after loading', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });
    expect(screen.getByText('Premium Plan')).toBeInTheDocument();
    expect(screen.getByText('Inactive Plan')).toBeInTheDocument();
  });

  test('displays error message when plans fail to load', async () => {
    plansApi.getPlans.mockRejectedValue(new Error('Failed to load plans'));

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/failed to load plans/i)).toBeInTheDocument();
    });
  });

  test('displays plan features correctly', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      const feature1Elements = screen.getAllByText(/✓ Feature 1/i);
      expect(feature1Elements.length).toBeGreaterThan(0);
    });
    const feature2Elements = screen.getAllByText(/✓ Feature 2/i);
    expect(feature2Elements.length).toBeGreaterThan(0);
  });

  test('subscribe button is disabled for inactive plans', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });
    const buttons = screen.getAllByRole('button');
    const inactiveButton = buttons.find((btn) =>
      btn.textContent.includes('Not Available')
    );
    expect(inactiveButton).toBeDisabled();
  });

  test('successful subscription shows success message', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    subscriptionsApi.createSubscription.mockResolvedValue({
      id: 'sub-123',
      plan_id: 'plan-1',
      user_id: 'user-123',
    });
    paymentsApi.createMockPayment.mockResolvedValue({
      id: 'payment-123',
      status: 'success',
    });

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    const subscribeButtons = screen.getAllByText(/subscribe now/i);
    fireEvent.click(subscribeButtons[0]);

    await waitFor(() => {
      expect(
        screen.getByText(/payment successful! subscription activated/i)
      ).toBeInTheDocument();
    });
  });

  test('failed subscription shows error message', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    subscriptionsApi.createSubscription.mockRejectedValue(
      new Error('Subscription failed')
    );

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    const subscribeButtons = screen.getAllByText(/subscribe now/i);
    fireEvent.click(subscribeButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/subscription failed/i)).toBeInTheDocument();
    });
  });

  test('displays processing state during subscription', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    subscriptionsApi.createSubscription.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );
    paymentsApi.createMockPayment.mockResolvedValue({ status: 'success' });

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    const subscribeButtons = screen.getAllByText(/subscribe now/i);
    fireEvent.click(subscribeButtons[0]);

    expect(screen.getByText(/processing payment/i)).toBeInTheDocument();
  });

  test('handles payment failure after successful subscription creation', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    subscriptionsApi.createSubscription.mockResolvedValue({
      id: 'sub-123',
      plan_id: 'plan-1',
      user_id: 'user-123',
    });
    paymentsApi.createMockPayment.mockRejectedValue(new Error('Payment failed'));

    render(
      <BrowserRouter>
        <SubscriberDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    const subscribeButtons = screen.getAllByText(/subscribe now/i);
    fireEvent.click(subscribeButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/payment failed/i)).toBeInTheDocument();
    });
  });
});
