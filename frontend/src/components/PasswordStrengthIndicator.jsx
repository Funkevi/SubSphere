import React from 'react';
import './PasswordStrengthIndicator.css';

/**
 * Password strength indicator component
 * Shows strength level based on password complexity
 */
export default function PasswordStrengthIndicator({ password }) {
  const getStrength = (pwd) => {
    if (!pwd) return { level: 0, text: '', color: 'gray' };

    let strength = 0;
    
    // Check length
    if (pwd.length >= 8) strength++;
    if (pwd.length >= 12) strength++;
    
    // Check for uppercase
    if (/[A-Z]/.test(pwd)) strength++;
    
    // Check for digit
    if (/\d/.test(pwd)) strength++;
    
    // Check for special char
    if (/[!@#$%^&*(),.?":{}|<>]/.test(pwd)) strength++;

    // Determine level
    if (strength <= 2) return { level: 1, text: 'Weak', color: '#ff4444' };
    if (strength === 3) return { level: 2, text: 'Medium', color: '#ffaa00' };
    if (strength === 4) return { level: 3, text: 'Good', color: '#44ff44' };
    return { level: 4, text: 'Strong', color: '#00ff00' };
  };

  const strength = getStrength(password);

  if (!password) return null;

  return (
    <div className="password-strength">
      <div className="strength-bar">
        <div
          className="strength-fill"
          style={{
            width: `${(strength.level / 4) * 100}%`,
            backgroundColor: strength.color,
          }}
        />
      </div>
      <span className="strength-text" style={{ color: strength.color }}>
        {strength.text}
      </span>
    </div>
  );
}
