import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { StatCard } from '../components/StatCard';
import { ComplianceGauge } from '../components/ComplianceGauge';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Server, ShieldAlert, FileCheck2, Bot, 
  ArrowUpRight, RefreshCw, AlertTriangle, CheckCircle2, Play
} from 'lucide-react';

export const Dashboard = () => {
  const [hosts, setHosts] = useState([]);
  const [report, setReport] = useState(null);
  const [drift, setDrift] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [scanning, setScanning] = useState(false);

  const fetchData = async () => {
    try {
      const [hostsRes, reportRes, driftRes] = await Promise.all([
        api.get('/hosts?limit=10'),
        api.get('/reports/compliance'),
        api.get('/agent/drift-detection')
      ]);
      setHosts(hostsRes.data.items);
      setReport(reportRes.data);
      setDrift(driftRes.data);
    } catch (err) {
      console.error("Failed to load dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await api.post('/hosts/sync', { force_full_sync: true });
      await fetchData();
    } catch (err) {
      console.error("Sync failed", err);
    } finally {
      setSyncing(false);
    }
  };

  const handleRunCisScan = async () => {
    setScanning(true);
    try {
      const fwRes = await api.get('/compliance/frameworks');
      const cisFw = fwRes.data.find(f => f.code === 'CIS_SLES_15') || fwRes.data[0];
      if (cisFw) {
        await api.post('/compliance/scans', { framework_id: cisFw.id });
        await fetchData();
      }
    } catch (err) {
      console.error("Scan failed", err);
    } finally {
      setScanning(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-6 h-6 text-emerald-400 animate-spin" />
      </div>
    );
  }

  const avgScore = report?.fleet_average_score || 0;
  const totalHosts = report?.fleet_total_hosts || hosts.length;
  const criticalHosts = report?.fleet_critical_hosts_count || 0;

  return (
    <div className="space-y-8">
      {/* Top Header & Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Fleet Posture & Agent Executive Summary</h2>
          <p className="text-xs text-slate-400 mt-1">Autonomous monitoring for SUSE Multi-Linux Manager registered hosts</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleSync}
            disabled={syncing}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-semibold rounded-xl flex items-center gap-2 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing MLM...' : 'Sync Inventory'}
          </button>
          <button
            onClick={handleRunCisScan}
            disabled={scanning}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            {scanning ? 'Running Scan...' : 'Run Fleet CIS Audit'}
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <StatCard
          title="Registered Hosts"
          value={totalHosts}
          icon={Server}
          description="Managed via SUSE MLM 10.0.33.56"
          color="cyan"
        />
        <StatCard
          title="Fleet Compliance"
          value={`${avgScore}%`}
          icon={FileCheck2}
          description="Average score across frameworks"
          color="emerald"
        />
        <StatCard
          title="Critical Errata Hosts"
          value={criticalHosts}
          icon={ShieldAlert}
          description="Unpatched CVEs or failing baselines"
          color="rose"
        />
        <StatCard
          title="Drifting Systems"
          value={drift?.drifting_hosts_count || 0}
          icon={Bot}
          description="Systems requiring agent remediation"
          color="amber"
        />
      </div>

      {/* Main Dashboard Visuals */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Gauge Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Overall Fleet Compliance Health</h3>
            <p className="text-xs text-slate-400 mt-0.5">Calculated across CIS, HIPAA & PCI benchmarks</p>
          </div>
          <div className="py-6">
            <ComplianceGauge score={avgScore} size={150} label="Current Fleet Benchmark" />
          </div>
          <div className="pt-4 border-t border-slate-800/80 flex items-center justify-around text-center text-xs">
            <div>
              <p className="text-[10px] text-slate-400 uppercase font-semibold">Target</p>
              <p className="text-sm font-bold text-emerald-400">≥ 85%</p>
            </div>
            <div className="w-px h-6 bg-slate-800"></div>
            <div>
              <p className="text-[10px] text-slate-400 uppercase font-semibold">Critical Threshold</p>
              <p className="text-sm font-bold text-rose-400">&lt; 70%</p>
            </div>
          </div>
        </div>

        {/* Framework Breakdown */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Regulatory Framework Posture</h3>
              <p className="text-xs text-slate-400 mt-0.5">Benchmark audit status across active standards</p>
            </div>
            <Link to="/compliance" className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1">
              Audit Center <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-4">
            {report?.framework_summaries?.map((fw) => (
              <div key={fw.framework_code} className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-200">{fw.framework_name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-800 text-slate-400 rounded-md">{fw.framework_code}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {fw.hosts_compliant_count} compliant / {fw.hosts_non_compliant_count} non-compliant hosts
                  </p>
                </div>
                <div className="text-right">
                  <span className={`text-base font-black ${fw.latest_score >= 85 ? 'text-emerald-400' : fw.latest_score < 70 ? 'text-rose-400' : 'text-amber-400'}`}>
                    {fw.latest_score}%
                  </span>
                  <p className="text-[10px] text-slate-500 uppercase font-semibold">Audit Score</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Host Posture Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Registered Infrastructure Status</h3>
            <p className="text-xs text-slate-400 mt-0.5">Live hosts connected through SUSE Multi-Linux Manager</p>
          </div>
          <Link to="/hosts" className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1">
            View All Hosts <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <th className="pb-3 pl-2">Hostname</th>
                <th className="pb-3">IP Address</th>
                <th className="pb-3">OS & Kernel</th>
                <th className="pb-3">Compliance Status</th>
                <th className="pb-3 text-center">Score</th>
                <th className="pb-3 text-center">Critical Errata</th>
                <th className="pb-3 text-right pr-2">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {hosts.map((host) => (
                <tr key={host.id} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 pl-2 font-mono font-medium text-slate-200">{host.hostname}</td>
                  <td className="py-3 font-mono text-slate-400">{host.ip_address}</td>
                  <td className="py-3">{host.os_family} {host.os_version}</td>
                  <td className="py-3">
                    <StatusBadge status={host.compliance_status} />
                  </td>
                  <td className="py-3 text-center font-bold">{host.compliance_score}%</td>
                  <td className="py-3 text-center">
                    {host.critical_errata_count > 0 ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                        <AlertTriangle className="w-3 h-3" /> {host.critical_errata_count} Errata
                      </span>
                    ) : (
                      <span className="text-slate-500 font-medium">—</span>
                    )}
                  </td>
                  <td className="py-3 text-right pr-2">
                    <Link
                      to={`/hosts/${host.id}`}
                      className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition inline-block"
                    >
                      Inspect
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
