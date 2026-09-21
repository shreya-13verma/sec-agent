import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Bot, Play, CheckCircle2, AlertOctagon, 
  ArrowRight, Shield, Zap, Sparkles, Terminal
} from 'lucide-react';

export const AgentConsole = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [hosts, setHosts] = useState([]);
  const [selectedHostId, setSelectedHostId] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [drift, setDrift] = useState(null);

  useEffect(() => {
    const init = async () => {
      try {
        const [hostsRes, driftRes] = await Promise.all([
          api.get('/hosts?limit=100'),
          api.get('/agent/drift-detection')
        ]);
        setHosts(hostsRes.data.items);
        setDrift(driftRes.data);

        if (location.state?.analysisId) {
          const anRes = await api.get(`/agent/analyses/${location.state.analysisId}`);
          setAnalysis(anRes.data);
          setSelectedHostId(anRes.data.host_id.toString());
        } else if (hostsRes.data.items.length > 0) {
          setSelectedHostId(hostsRes.data.items[0].id.toString());
        }
      } catch (err) {
        console.error("Failed to load agent console data", err);
      }
    };
    init();
  }, [location.state]);

  const handleRunAnalysis = async () => {
    if (!selectedHostId) return;
    setLoading(true);
    try {
      const res = await api.post('/agent/analyze', { host_id: parseInt(selectedHostId) });
      setAnalysis(res.data);
    } catch (err) {
      console.error("Analysis failed", err);
    } finally {
      setLoading(false);
    }
  };

  const getThoughtBadge = (type) => {
    switch (type) {
      case 'OBSERVATION':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      case 'CORRELATION':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      case 'RISK_EVALUATION':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'DECISION':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      default:
        return 'bg-slate-800 text-slate-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2.5">
            <Bot className="w-6 h-6 text-emerald-400" />
            Autonomous Agent Reasoning & Posture Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">Multi-step autonomous drift detection, root-cause correlation, and remediation planning</p>
        </div>
      </div>

      {/* Target Host Selector */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between gap-4">
        <div className="flex items-center gap-3 flex-1">
          <label className="text-xs font-semibold text-slate-300 shrink-0">Target Host:</label>
          <select
            value={selectedHostId}
            onChange={(e) => setSelectedHostId(e.target.value)}
            className="w-full max-w-md bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-emerald-500"
          >
            {hosts.map((h) => (
              <option key={h.id} value={h.id}>
                {h.hostname} ({h.os_family} {h.os_version}) — {h.compliance_status} ({h.compliance_score}%)
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={loading || !selectedHostId}
          className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          {loading ? 'Agent Reasoning...' : 'Run Autonomous Analysis'}
        </button>
      </div>

      {/* Agent Thought Stream & Staged Plan */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Thought Stream Column */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Terminal className="w-4 h-4 text-emerald-400" />
              Agent Step-by-Step Reasoning Trace
            </h3>
            {analysis && <StatusBadge status={analysis.analysis_status} />}
          </div>

          {loading ? (
            <div className="py-12 flex flex-col items-center justify-center space-y-3">
              <Bot className="w-8 h-8 text-emerald-400 animate-bounce" />
              <p className="text-xs text-slate-400 animate-pulse font-mono">Agent analyzing host errata, dependencies, and configuration drift...</p>
            </div>
          ) : analysis?.thought_steps?.length > 0 ? (
            <div className="space-y-4">
              {analysis.thought_steps.map((step) => (
                <div key={step.id} className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getThoughtBadge(step.thought_type)}`}>
                      Step {step.step_order}: {step.thought_type}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">
                      {new Date(step.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">
                    {step.thought_content}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-slate-500 text-xs">
              Select a host and click "Run Autonomous Analysis" to watch the agent reasoning loop.
            </div>
          )}
        </div>

        {/* Action / Plan Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between space-y-4">
          <div>
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Agent Synthesis</h3>
            <p className="text-xs text-slate-400 mt-1">Autonomous conclusion & staged remediation plan</p>

            {analysis ? (
              <div className="mt-4 space-y-3">
                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-xl">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Drift Anomaly Summary</span>
                  <p className="text-xs font-semibold text-slate-200 mt-1">{analysis.root_cause_summary || 'Baseline intact'}</p>
                </div>

                {analysis.proposed_plan_id && (
                  <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-emerald-400">Remediation Plan #{analysis.proposed_plan_id}</span>
                      <span className="text-[10px] px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded font-bold">STAGED</span>
                    </div>
                    <p className="text-xs text-slate-300">
                      Autonomous remediation actions compiled and staged for human review.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500 mt-4">Run analysis to generate remediation proposal.</p>
            )}
          </div>

          {analysis?.proposed_plan_id && (
            <button
              onClick={() => navigate('/remediation')}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl flex items-center justify-center gap-2 transition shadow-lg shadow-emerald-500/20"
            >
              Review Staged Plan in Remediation Manager
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
