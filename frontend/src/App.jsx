import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import SubscriberDashboard from './pages/SubscriberDashboard';
import AdminDashboard from './pages/AdminDashboard';
import './styles/index.css';

function App() {
  // Check if user is logged in
  const isLoggedIn = !!localStorage.getItem('token');
  const userRole = localStorage.getItem('role');

  // Protected route wrapper
  const ProtectedRoute = ({ children, requiredRole }) => {
    if (!isLoggedIn) {
      return <Navigate to="/login" replace />;
    }

    if (requiredRole && userRole !== requiredRole) {
      return <Navigate to="/dashboard" replace />;
    }

    return children;
  };

  return (
    <Router>
      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <SubscriberDashboard />
            </ProtectedRoute>
          }
        />
        
        <Route
          path="/admin"
          element={
            <ProtectedRoute requiredRole="admin">
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
