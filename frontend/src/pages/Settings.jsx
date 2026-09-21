import React, { useState } from 'react';
import { Settings as SettingsIcon, Server, Shield, Database, Save, Check } from 'lucide-react';

export const Settings = () => {
  const [mlmUrl, setMlmUrl] = useState('https://10.0.33.56/rhn/apidoc/index.jsp');
  const [apiBase, setApiBase] = useState('https://10.0.33.56/rpc/api');
  const [scanInterval, setScanInterval] = useState('6');
  const [criticalThreshold, setCriticalThreshold] = useState('70');
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2.5">
          <SettingsIcon className="w-6 h-6 text-emerald-400" />
          System Settings & Operational Parameters
        </h2>
        <p className="text-xs text-slate-400 mt-1">Configure SUSE Multi-Linux Manager endpoints, automated audit cycles, and risk scoring policies</p>
      </div>

      <form onSubmit={handleSave} className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
        {/* SUSE MLM Connection */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Server className="w-4 h-4 text-emerald-400" />
            SUSE Multi-Linux Manager Integration
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">MLM Web / Doc URL</label>
              <input
                type="text"
                value={mlmUrl}
                onChange={(e) => setMlmUrl(e.target.value)}
                className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">MLM XML-RPC API Base</label>
              <input
                type="text"
                value={apiBase}
                onChange={(e) => setApiBase(e.target.value)}
                className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
        </div>

        {/* Operational Parameters */}
        <div className="space-y-4 pt-4 border-t border-slate-800">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            Compliance & Scoring Thresholds
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Automated Scan Horizon (Hours)</label>
              <input
                type="number"
                value={scanInterval}
                onChange={(e) => setScanInterval(e.target.value)}
                className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">Default background fleet scan frequency</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Critical Drift Score Threshold (%)</label>
              <input
                type="number"
                value={criticalThreshold}
                onChange={(e) => setCriticalThreshold(e.target.value)}
                className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500"
              />
              <p className="text-[11px] text-slate-500 mt-1">Scores below this threshold flag hosts as CRITICAL</p>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
          {saved && (
            <span className="text-xs text-emerald-400 flex items-center gap-1 font-semibold animate-fadeIn">
              <Check className="w-4 h-4" /> Settings updated successfully
            </span>
          )}
          <button
            type="submit"
            className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition"
          >
            <Save className="w-4 h-4" /> Save Parameters
          </button>
        </div>
      </form>
    </div>
  );
};
