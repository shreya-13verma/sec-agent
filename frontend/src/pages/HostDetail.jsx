import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { ComplianceGauge } from '../components/ComplianceGauge';
import { 
  Server, ArrowLeft, Bot, ShieldCheck, 
  Layers, Package, AlertOctagon, CheckCircle2, Play
} from 'lucide-react';

export const HostDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [host, setHost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState('packages');

  const fetchHostDetail = async () => {
    try {
      const res = await api.get(`/hosts/${id}`);
      setHost(res.data);
    } catch (err) {
      console.error("Failed to load host detail", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHostDetail();
  }, [id]);

  const handleAgentAnalyze = async () => {
    setAnalyzing(true);
    try {
      const res = await api.post('/agent/analyze', { host_id: parseInt(id) });
      navigate('/agent', { state: { analysisId: res.data.id } });
    } catch (err) {
      console.error("Agent analysis failed", err);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading host specifications...</div>;
  }

  if (!host) {
    return <div className="p-8 text-center text-xs text-rose-400">Host not found.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Back button & Title */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/hosts" className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 transition">
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-bold font-mono text-slate-100">{host.hostname}</h2>
              <StatusBadge status={host.compliance_status} />
            </div>
            <p className="text-xs text-slate-400 mt-0.5">SUSE MLM System ID: #{host.mlm_system_id} · IP: {host.ip_address}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleAgentAnalyze}
            disabled={analyzing}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition disabled:opacity-50"
          >
            <Bot className="w-4 h-4" />
            {analyzing ? 'Reasoning...' : 'Autonomous Agent Audit'}
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400">Operating System</span>
            <p className="text-sm font-bold text-slate-200">{host.os_family} {host.os_version}</p>
            <p className="text-xs font-mono text-slate-400">{host.kernel_release}</p>
          </div>
          <div className="p-3 bg-slate-800 rounded-xl border border-slate-700">
            <Server className="w-5 h-5 text-emerald-400" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400">Security Errata / CVEs</span>
            <p className="text-sm font-bold text-slate-200">{host.missing_errata?.length || 0} Missing Advisories</p>
            <p className="text-xs text-rose-400 font-semibold">{host.critical_errata_count} Critical CVEs</p>
          </div>
          <div className="p-3 bg-slate-800 rounded-xl border border-slate-700">
            <AlertOctagon className="w-5 h-5 text-rose-400" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center justify-center">
          <ComplianceGauge score={host.compliance_score} size={90} label="System Compliance" />
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800 flex items-center gap-6">
        <button
          onClick={() => setActiveTab('packages')}
          className={`pb-3 text-xs font-bold transition border-b-2 ${
            activeTab === 'packages'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Installed Packages ({host.packages?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('errata')}
          className={`pb-3 text-xs font-bold transition border-b-2 ${
            activeTab === 'errata'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Missing Security Errata ({host.missing_errata?.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('channels')}
          className={`pb-3 text-xs font-bold transition border-b-2 ${
            activeTab === 'channels'
              ? 'border-emerald-500 text-emerald-400'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Subscribed MLM Channels ({host.channels?.length || 0})
        </button>
      </div>

      {/* Tab Content */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
        {activeTab === 'packages' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px]">
                  <th className="pb-3">Package Name</th>
                  <th className="pb-3">Version</th>
                  <th className="pb-3">Release</th>
                  <th className="pb-3">Architecture</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {host.packages?.map((pkg) => (
                  <tr key={pkg.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-mono font-medium text-slate-200">{pkg.package_name}</td>
                    <td className="py-2.5 font-mono text-slate-400">{pkg.package_version}</td>
                    <td className="py-2.5 font-mono text-slate-400">{pkg.package_release}</td>
                    <td className="py-2.5 font-mono text-slate-500">{pkg.package_arch}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'errata' && (
          <div className="space-y-3">
            {host.missing_errata?.length === 0 ? (
              <p className="text-xs text-emerald-400 p-4">No missing security advisories. System is fully patched.</p>
            ) : (
              host.missing_errata?.map((item) => (
                <div key={item.id} className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-200">{item.errata?.advisory_name}</span>
                      <StatusBadge status={item.errata?.severity} />
                      {item.errata?.cve_identifier && (
                        <span className="text-[10px] font-mono px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded">
                          {item.errata.cve_identifier}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">{item.errata?.synopsis}</p>
                  </div>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {new Date(item.detected_at).toLocaleDateString()}
                  </span>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'channels' && (
          <div className="space-y-2">
            {host.channels?.map((ch) => (
              <div key={ch.id} className="p-3 bg-slate-950/60 border border-slate-800 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-200">{ch.channel_name}</p>
                  <p className="text-[11px] font-mono text-slate-400">{ch.channel_label}</p>
                </div>
                <span className="text-[10px] px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded">
                  Subscribed
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
