import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import AdminDashboard from '../pages/AdminDashboard';
import * as plansApi from '../api/plans';

jest.mock('../api/plans');

describe('AdminDashboard', () => {
  const mockPlans = [
    {
      id: 'plan-1',
      name: 'Basic Plan',
      description: 'Basic features',
      price: 9.99,
      duration_days: 30,
      is_active: true,
    },
    {
      id: 'plan-2',
      name: 'Premium Plan',
      description: 'Premium features',
      price: 19.99,
      duration_days: 365,
      is_active: true,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem('token', 'admin-token');
    localStorage.setItem('role', 'admin');
  });

  afterEach(() => {
    localStorage.clear();
  });

  test('displays loading state initially', () => {
    plansApi.getPlans.mockImplementation(() => new Promise(() => {}));

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('displays error message when plans fail to load', async () => {
    plansApi.getPlans.mockRejectedValue(new Error('Network error'));

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });

  test('displays plans in table after loading', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });
    expect(screen.getByText('Premium Plan')).toBeInTheDocument();
    expect(screen.getByText('$9.99')).toBeInTheDocument();
    expect(screen.getByText('$19.99')).toBeInTheDocument();
  });

  test('displays create plan button', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/\+ create plan/i)).toBeInTheDocument();
    });
  });

  test('opens modal when create plan button is clicked', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/\+ create plan/i)).toBeInTheDocument();
    });

    const createButton = screen.getByRole('button', { name: /\+ create plan/i });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByText('Create Plan')).toBeInTheDocument();
    });
    const inputs = screen.getAllByRole('textbox');
    expect(inputs.length).toBeGreaterThan(0);
  });

  test('creates new plan successfully', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    plansApi.createPlan.mockResolvedValue({
      id: 'plan-3',
      name: 'New Plan',
      description: 'New description',
      price: 15.99,
      duration_days: 30,
      is_active: true,
    });

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/\+ create plan/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/\+ create plan/i));

    await waitFor(() => {
      expect(screen.getByText('Create Plan')).toBeInTheDocument();
    });

    const textInputs = screen.getAllByRole('textbox');
    const nameInput = textInputs[0]; // First textbox is Name
    const descInput = textInputs[1]; // Second is Description
    
    fireEvent.change(nameInput, {
      target: { value: 'New Plan' },
    });
    fireEvent.change(descInput, {
      target: { value: 'New description' },
    });
    
    const priceInput = screen.getByRole('spinbutton');
    fireEvent.change(priceInput, {
      target: { value: '15.99' },
    });

    plansApi.getPlans.mockResolvedValue([...mockPlans, {
      id: 'plan-3',
      name: 'New Plan',
      description: 'New description',
      price: 15.99,
      duration_days: 30,
      is_active: true,
    }]);

    fireEvent.click(screen.getByText(/^create$/i));

    await waitFor(() => {
      expect(plansApi.createPlan).toHaveBeenCalled();
    });
  });

  test('opens edit modal with pre-filled data', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByText(/edit/i);
    fireEvent.click(editButtons[0]);

    await waitFor(() => {
      expect(screen.getByDisplayValue('Basic Plan')).toBeInTheDocument();
    });
    expect(screen.getByDisplayValue('Basic features')).toBeInTheDocument();
    expect(screen.getByDisplayValue('9.99')).toBeInTheDocument();
  });

  test('updates plan successfully', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    plansApi.updatePlan.mockResolvedValue({
      ...mockPlans[0],
      name: 'Updated Plan',
    });

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByText(/edit/i);
    fireEvent.click(editButtons[0]);

    fireEvent.change(screen.getByDisplayValue('Basic Plan'), {
      target: { value: 'Updated Plan' },
    });

    fireEvent.click(screen.getByText(/update/i));

    await waitFor(() => {
      expect(plansApi.updatePlan).toHaveBeenCalledWith(
        'plan-1',
        expect.objectContaining({ name: 'Updated Plan' })
      );
    });
  });

  test('shows confirmation dialog when deleting plan', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    window.confirm = jest.fn(() => false);

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText(/delete/i);
    fireEvent.click(deleteButtons[0]);

    expect(window.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete this plan?'
    );
  });

  test('deletes plan when confirmed', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    plansApi.deletePlan.mockResolvedValue(true);
    window.confirm = jest.fn(() => true);

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByText(/delete/i);
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(plansApi.deletePlan).toHaveBeenCalledWith('plan-1');
    });
  });

  test('displays active/inactive status badges', async () => {
    plansApi.getPlans.mockResolvedValue([
      ...mockPlans,
      {
        id: 'plan-3',
        name: 'Inactive Plan',
        description: 'Inactive',
        price: 29.99,
        duration_days: 30,
        is_active: false,
      },
    ]);

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Inactive Plan')).toBeInTheDocument();
    });
    const activeElements = screen.getAllByText(/active/i);
    expect(activeElements.length).toBeGreaterThan(0);
  });

  test('handles create plan error', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);
    plansApi.createPlan.mockRejectedValue(new Error('Creation failed'));

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/\+ create plan/i));

    await waitFor(() => {
      expect(screen.getByText('Create Plan')).toBeInTheDocument();
    });

    const textInputs = screen.getAllByRole('textbox');
    fireEvent.change(textInputs[0], { target: { value: 'Test Plan' } });

    fireEvent.click(screen.getByText(/^create$/i));

    await waitFor(() => {
      expect(plansApi.createPlan).toHaveBeenCalled();
    });
  });

  test('closes modal when cancel is clicked', async () => {
    plansApi.getPlans.mockResolvedValue(mockPlans);

    render(
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Basic Plan')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/\+ create plan/i));

    await waitFor(() => {
      expect(screen.getByText('Create Plan')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/cancel/i));

    await waitFor(() => {
      expect(screen.queryByText('Create Plan')).not.toBeInTheDocument();
    });
  });
});
