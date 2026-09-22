import React from 'react';
import { Shield, Server, Terminal, RefreshCw } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onRefresh }) {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
          <Shield className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-slate-100 flex items-center gap-2">
            SUSE MLM Security Agent
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-medium border border-emerald-500/30">
              FastMCP v1.0
            </span>
          </h1>
          <p className="text-xs text-slate-400">Autonomous OpenSCAP Auditing & Errata Remediation</p>
        </div>
      </div>

      <nav className="flex items-center gap-1 bg-slate-950/60 p-1 rounded-lg border border-slate-800">
        <button
          onClick={() => setActiveTab('chat')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition flex items-center gap-2 ${
            activeTab === 'chat'
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <Terminal className="w-4 h-4" />
          Agent Chat
        </button>
        <button
          onClick={() => setActiveTab('fleet')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition flex items-center gap-2 ${
            activeTab === 'fleet'
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <Server className="w-4 h-4" />
          Fleet Posture
        </button>
        <button
          onClick={() => setActiveTab('reports')}
          className={`px-4 py-1.5 rounded-md text-sm font-medium transition flex items-center gap-2 ${
            activeTab === 'reports'
              ? 'bg-emerald-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
          }`}
        >
          <Shield className="w-4 h-4" />
          Report Center
        </button>
      </nav>

      <div className="flex items-center gap-3">
        <button
          onClick={onRefresh}
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-lg transition border border-slate-800"
          title="Refresh Fleet Data"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
        <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-slate-300 font-medium">MLM Connected</span>
        </div>
      </div>
    </header>
  );
}
