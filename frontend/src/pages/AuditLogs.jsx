import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { History, Shield, Search, Filter, Clock } from 'lucide-react';

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');

  const fetchAuditLogs = async () => {
    try {
      let query = '/audit-logs?limit=100';
      if (actionFilter) query += `&action=${encodeURIComponent(actionFilter)}`;
      const res = await api.get(query);
      setLogs(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error("Failed to load audit logs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, [actionFilter]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2.5">
            <History className="w-6 h-6 text-emerald-400" />
            Immutable Security & Operational Audit Log
          </h2>
          <p className="text-xs text-slate-400 mt-1">Tamper-evident trail of logins, scans, agent reasoning sessions, approvals, and MLM actions</p>
        </div>

        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All Action Types</option>
          <option value="USER_LOGIN_SUCCESS">Login Success</option>
          <option value="COMPLIANCE_SCAN_COMPLETED">Scan Completed</option>
          <option value="AGENT_ANALYSIS_COMPLETED">Agent Analysis</option>
          <option value="REMEDIATION_PLAN_APPROVED">Plan Approved</option>
          <option value="REMEDIATION_PLAN_EXECUTED">Plan Executed</option>
          <option value="MLM_INVENTORY_SYNC">MLM Sync</option>
        </select>
      </div>

      {/* Logs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading audit trail...</div>
        ) : logs.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">No audit records found.</div>
        ) : (
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/40 text-slate-400 font-semibold uppercase text-[10px]">
                <th className="py-3 px-4">Timestamp (UTC)</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Action Event</th>
                <th className="py-3 px-4">Resource</th>
                <th className="py-3 px-4">Details</th>
                <th className="py-3 px-4">Client IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30 font-mono">
                  <td className="py-3 px-4 text-slate-400 text-[11px]">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 font-bold text-slate-200">{log.user_username}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-emerald-400 text-[10px] font-bold border border-slate-700">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400 text-[11px]">
                    {log.resource_type} #{log.resource_id}
                  </td>
                  <td className="py-3 px-4 font-sans text-xs text-slate-300 max-w-md truncate">
                    {log.details}
                  </td>
                  <td className="py-3 px-4 text-slate-500 text-[11px]">{log.ip_address}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
