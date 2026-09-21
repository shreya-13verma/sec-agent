import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Hosts } from './pages/Hosts';
import { HostDetail } from './pages/HostDetail';
import { ComplianceScans } from './pages/ComplianceScans';
import { AgentConsole } from './pages/AgentConsole';
import { RemediationManager } from './pages/RemediationManager';
import { Reports } from './pages/Reports';
import { AuditLogs } from './pages/AuditLogs';
import { Settings } from './pages/Settings';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-xs text-slate-400">Loading session...</div>;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Layout>{children}</Layout>;
};

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/hosts" element={<ProtectedRoute><Hosts /></ProtectedRoute>} />
          <Route path="/hosts/:id" element={<ProtectedRoute><HostDetail /></ProtectedRoute>} />
          <Route path="/compliance" element={<ProtectedRoute><ComplianceScans /></ProtectedRoute>} />
          <Route path="/agent" element={<ProtectedRoute><AgentConsole /></ProtectedRoute>} />
          <Route path="/remediation" element={<ProtectedRoute><RemediationManager /></ProtectedRoute>} />
          <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
          <Route path="/audit-logs" element={<ProtectedRoute><AuditLogs /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
