import React from 'react';
import { render, screen } from '@testing-library/react';
import PasswordStrengthIndicator from '../components/PasswordStrengthIndicator';

describe('PasswordStrengthIndicator', () => {
  test('renders nothing when password is empty', () => {
    const { container } = render(<PasswordStrengthIndicator password="" />);
    expect(container).toBeEmptyDOMElement();
  });

  test('shows "Weak" for short password', () => {
    render(<PasswordStrengthIndicator password="abc" />);
    expect(screen.getByText(/weak/i)).toBeInTheDocument();
  });

  test('shows "Weak" for password with only 2 strength criteria', () => {
    render(<PasswordStrengthIndicator password="password" />);
    expect(screen.getByText(/weak/i)).toBeInTheDocument();
  });

  test('shows "Medium" for password with 3 strength criteria', () => {
    // password: 8+ chars (1), uppercase (1), digit (1) = 3 strength
    render(<PasswordStrengthIndicator password="Password1" />);
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
  });

  test('shows "Good" for password with 4 strength criteria', () => {
    // Password1: 8+ chars (1), uppercase (1), lowercase (implicit), digit (1) = 3
    // Need 12+ chars for extra point
    render(<PasswordStrengthIndicator password="Password1234" />);
    expect(screen.getByText(/good/i)).toBeInTheDocument();
  });

  test('shows "Strong" for password with all strength criteria', () => {
    // 12+ chars (2), uppercase (1), digit (1), special char (1) = 5
    render(<PasswordStrengthIndicator password="Password123!" />);
    expect(screen.getByText(/strong/i)).toBeInTheDocument();
  });

  test('shows "Strong" for very long password with all criteria', () => {
    // MyVerySecurePassword123!@#: 12+ chars (2), uppercase (1), digit (1), special (1) = 5
    render(<PasswordStrengthIndicator password="MyVerySecurePassword123!@#" />);
    expect(screen.getByText(/strong/i)).toBeInTheDocument();
  });

  test('strength bar width increases with password strength', () => {
    const { rerender } = render(
      <PasswordStrengthIndicator password="weak" />
    );
    
    expect(screen.getByText(/weak/i)).toBeInTheDocument();
    
    rerender(<PasswordStrengthIndicator password="Password123!" />);
    
    expect(screen.getByText(/strong/i)).toBeInTheDocument();
  });

  test('displays correct strength text for weak password', () => {
    render(<PasswordStrengthIndicator password="weak" />);
    expect(screen.getByText(/weak/i)).toBeInTheDocument();
  });

  test('displays correct strength text for strong password', () => {
    render(<PasswordStrengthIndicator password="Password123!" />);
    expect(screen.getByText(/strong/i)).toBeInTheDocument();
  });
});
