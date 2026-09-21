import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { 
  FileText, Download, FileSpreadsheet, 
  ShieldCheck, RefreshCw, Calendar, ArrowUpRight
} from 'lucide-react';

export const Reports = () => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchReport = async () => {
    try {
      const res = await api.get('/reports/compliance');
      setReportData(res.data);
    } catch (err) {
      console.error("Failed to load report", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const handleDownloadCsv = () => {
    window.open('/api/v1/reports/export/csv', '_blank');
  };

  const handleDownloadPdf = () => {
    window.open('/api/v1/reports/export/pdf', '_blank');
  };

  if (loading) {
    return <div className="p-12 text-center text-xs text-slate-400">Compiling executive dossier...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2.5">
            <FileText className="w-6 h-6 text-emerald-400" />
            Audit-Ready Compliance Reporting & Dossier Export
          </h2>
          <p className="text-xs text-slate-400 mt-1">Export executive summaries, drift metrics, and host CVE logs in PDF and CSV</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDownloadCsv}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-semibold rounded-xl flex items-center gap-2 transition"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            Export CSV
          </button>
          <button
            onClick={handleDownloadPdf}
            className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-500/20 flex items-center gap-2 transition"
          >
            <Download className="w-4 h-4" />
            Download PDF Report
          </button>
        </div>
      </div>

      {/* Executive Report Preview Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
        <div className="border-b border-slate-800 pb-4 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-100">
              Executive Security Posture Overview
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Generated: {new Date(reportData?.generated_at).toUTCString()} · Target: SUSE Multi-Linux Manager
            </p>
          </div>
          <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full font-bold">
            Average Score: {reportData?.fleet_average_score}%
          </span>
        </div>

        {/* Framework Breakdown */}
        <div>
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
            Framework Summary Breakdown
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {reportData?.framework_summaries?.map((fw) => (
              <div key={fw.framework_code} className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-slate-200">{fw.framework_name}</span>
                  <span className="text-xs font-black text-emerald-400">{fw.latest_score}%</span>
                </div>
                <div className="text-[11px] text-slate-400 space-y-1">
                  <p>Total Audit Runs: {fw.total_scans}</p>
                  <p>Compliant Hosts: {fw.hosts_compliant_count} / {fw.hosts_compliant_count + fw.hosts_non_compliant_count}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Host Breakdown Table */}
        <div>
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
            Host Compliance Posture & Errata Details
          </h4>
          <div className="overflow-x-auto border border-slate-800 rounded-xl">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-950 text-slate-400 font-semibold uppercase text-[10px] border-b border-slate-800">
                  <th className="py-3 px-4">Hostname</th>
                  <th className="py-3 px-4">IP Address</th>
                  <th className="py-3 px-4">OS Distribution</th>
                  <th className="py-3 px-4">Compliance Status</th>
                  <th className="py-3 px-4 text-center">Score</th>
                  <th className="py-3 px-4">Missing CVE Advisories</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 text-slate-300">
                {reportData?.host_details?.map((h, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="py-3 px-4 font-mono font-medium text-slate-200">{h.hostname}</td>
                    <td className="py-3 px-4 font-mono text-slate-400">{h.ip_address}</td>
                    <td className="py-3 px-4">{h.os_info}</td>
                    <td className="py-3 px-4">{h.compliance_status}</td>
                    <td className="py-3 px-4 text-center font-bold">{h.compliance_score}%</td>
                    <td className="py-3 px-4 font-mono text-slate-400">
                      {h.missing_cves?.length > 0 ? (
                        <span className="text-rose-400 font-semibold">{h.missing_cves.join(', ')}</span>
                      ) : (
                        <span className="text-slate-500">None</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
