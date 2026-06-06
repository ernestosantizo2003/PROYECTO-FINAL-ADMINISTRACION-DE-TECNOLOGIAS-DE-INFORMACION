import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AuthLayout } from './layouts/AuthLayout';
import { MainLayout } from './layouts/MainLayout';
import { ProtectedRoute } from './components/ProtectedRoute';

import { LoginPage } from './pages/auth/LoginPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { UsersPage } from './pages/users/UsersPage';
import { RolesPage } from './pages/roles/RolesPage';
import { KnowledgePage } from './pages/knowledge/KnowledgePage';
import { WhatIfPage } from './pages/whatif/WhatIfPage';
import { DecisionsPage } from './pages/decisions/DecisionsPage';
import { FeedbackPage } from './pages/feedback/FeedbackPage';
import { KPIsPage } from './pages/kpis/KPIsPage';
import { AuditPage } from './pages/audit/AuditPage';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Auth Routes */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
          </Route>

          {/* Protected Routes — wrap the layout with ProtectedRoute */}
          <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route
              path="/users"
              element={
                <ProtectedRoute allowedRoles={['admin_sistema']}>
                  <UsersPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/roles"
              element={
                <ProtectedRoute allowedRoles={['admin_sistema']}>
                  <RolesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge"
              element={
                <ProtectedRoute
                  allowedRoles={['admin_conocimiento', 'admin_sistema', 'decisor']}
                >
                  <KnowledgePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/whatif"
              element={
                <ProtectedRoute allowedRoles={['decisor', 'admin_sistema']}>
                  <WhatIfPage />
                </ProtectedRoute>
              }
            />
            <Route path="/decisions" element={<DecisionsPage />} />
            <Route path="/feedback" element={<FeedbackPage />} />
            <Route
              path="/kpis"
              element={
                <ProtectedRoute
                  allowedRoles={['analista', 'admin_sistema', 'decisor']}
                >
                  <KPIsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/audit"
              element={
                <ProtectedRoute allowedRoles={['admin_sistema']}>
                  <AuditPage />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
