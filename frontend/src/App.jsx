import React, { useState } from 'react';
import Header from './components/common/Header';
import ChatContainer from './components/chat/ChatContainer';
import ComplianceOverview from './components/dashboard/ComplianceOverview';
import ReportViewer from './components/reports/ReportViewer';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat'); // chat | fleet | reports
  const [sessionId, setSessionId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSelectServerForChat = (serverId) => {
    setActiveTab('chat');
  };

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRefresh={handleRefresh}
      />

      <main className="flex-1 flex overflow-hidden">
        {activeTab === 'chat' && (
          <ChatContainer
            currentSessionId={sessionId}
            setSessionId={setSessionId}
          />
        )}

        {activeTab === 'fleet' && (
          <ComplianceOverview
            key={refreshKey}
            onSelectServerForChat={handleSelectServerForChat}
          />
        )}

        {activeTab === 'reports' && (
          <ReportViewer key={refreshKey} />
        )}
      </main>
    </div>
  );
}
