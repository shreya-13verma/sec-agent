import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { Server, Search, Filter, RefreshCw, AlertTriangle, ArrowUpRight } from 'lucide-react';

export const Hosts = () => {
  const [hosts, setHosts] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [osFilter, setOsFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const fetchHosts = async () => {
    try {
      let query = `/hosts?limit=100`;
      if (search) query += `&search=${encodeURIComponent(search)}`;
      if (statusFilter) query += `&compliance_status=${encodeURIComponent(statusFilter)}`;
      if (osFilter) query += `&os_family=${encodeURIComponent(osFilter)}`;
      
      const res = await api.get(query);
      setHosts(res.data.items);
    } catch (err) {
      console.error("Failed to fetch hosts", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHosts();
  }, [search, statusFilter, osFilter]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await api.post('/hosts/sync', { force_full_sync: true });
      await fetchHosts();
    } catch (err) {
      console.error("Sync failed", err);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Host Inventory & MLM Registered Systems</h2>
          <p className="text-xs text-slate-400 mt-1">Managed Linux hosts discovered through SUSE Multi-Linux Manager</p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-semibold rounded-xl flex items-center gap-2 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
          {syncing ? 'Syncing...' : 'Sync from MLM'}
        </button>
      </div>

      {/* Filters & Search */}
      <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl flex flex-wrap items-center justify-between gap-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by hostname or IP address..."
            className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500"
            >
              <option value="">All Compliance Statuses</option>
              <option value="COMPLIANT">Compliant</option>
              <option value="NON_COMPLIANT">Non-Compliant</option>
              <option value="CRITICAL">Critical Drift</option>
              <option value="UNKNOWN">Unknown</option>
            </select>
          </div>

          <select
            value={osFilter}
            onChange={(e) => setOsFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500"
          >
            <option value="">All Operating Systems</option>
            <option value="SLES">SUSE Linux Enterprise (SLES)</option>
            <option value="RHEL">Red Hat Enterprise Linux (RHEL)</option>
            <option value="openSUSE">openSUSE Leap</option>
          </select>
        </div>
      </div>

      {/* Hosts Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-xs">Loading hosts...</div>
        ) : hosts.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            No registered hosts found matching criteria.
          </div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
                <th className="py-3.5 pl-4">System Name</th>
                <th className="py-3.5">IP Address</th>
                <th className="py-3.5">OS Distribution</th>
                <th className="py-3.5">Architecture</th>
                <th className="py-3.5">Compliance Posture</th>
                <th className="py-3.5 text-center">Score</th>
                <th className="py-3.5 text-center">Critical Advisories</th>
                <th className="py-3.5 text-right pr-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {hosts.map((host) => (
                <tr key={host.id} className="hover:bg-slate-800/40 transition">
                  <td className="py-3.5 pl-4 font-mono font-medium text-slate-200">{host.hostname}</td>
                  <td className="py-3.5 font-mono text-slate-400">{host.ip_address}</td>
                  <td className="py-3.5">{host.os_family} {host.os_version}</td>
                  <td className="py-3.5 font-mono text-slate-400">{host.architecture}</td>
                  <td className="py-3.5">
                    <StatusBadge status={host.compliance_status} />
                  </td>
                  <td className="py-3.5 text-center font-bold text-slate-100">{host.compliance_score}%</td>
                  <td className="py-3.5 text-center">
                    {host.critical_errata_count > 0 ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                        <AlertTriangle className="w-3 h-3" /> {host.critical_errata_count}
                      </span>
                    ) : (
                      <span className="text-slate-500 font-medium">—</span>
                    )}
                  </td>
                  <td className="py-3.5 text-right pr-4">
                    <Link
                      to={`/hosts/${host.id}`}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition inline-block"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
