import React, { useState, useEffect } from 'react';
import { FileText, Download, Plus, Loader2, CheckCircle2, Shield } from 'lucide-react';
import { fetchReports, generateReport, fetchSystems } from '../../services/api';

export default function ReportViewer() {
  const [reports, setReports] = useState([]);
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [scope, setScope] = useState('all');
  const [targetId, setTargetId] = useState('all');
  const [formats, setFormats] = useState(['pdf', 'csv', 'json']);
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [reps, sys] = await Promise.all([fetchReports(), fetchSystems()]);
      setReports(reps);
      setSystems(sys);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setSuccessMsg('');
    try {
      const newReport = await generateReport({
        title: `SUSE MLM ${scope.toUpperCase()} Compliance Audit`,
        scope,
        target_id: targetId,
        formats
      });
      setReports((prev) => [newReport, ...prev]);
      setSuccessMsg(`Report generated successfully! (ID: ${newReport.id})`);
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const toggleFormat = (fmt) => {
    if (formats.includes(fmt)) {
      if (formats.length > 1) setFormats(formats.filter((f) => f !== fmt));
    } else {
      setFormats([...formats, fmt]);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto h-[calc(100vh-4rem)] overflow-y-auto">
      {/* Header & Generator Box */}
      <div className="p-6 bg-slate-900/60 border border-slate-800 rounded-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              <FileText className="w-5 h-5 text-emerald-400" />
              Compliance & Vulnerability Report Generator
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Generate certified OpenSCAP and Errata audit reports in PDF, CSV, and JSON formats.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 border-t border-slate-800/80">
          {/* Scope */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Audit Scope</label>
            <select
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              className="w-full text-xs px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-emerald-500"
            >
              <option value="all">Full Fleet (All Registered Hosts)</option>
              <option value="system">Single Host Audit</option>
            </select>
          </div>

          {/* Target Host (if single host) */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Target Host</label>
            <select
              value={targetId}
              onChange={(e) => setTargetId(e.target.value)}
              disabled={scope === 'all'}
              className="w-full text-xs px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 disabled:opacity-40 focus:outline-none focus:border-emerald-500"
            >
              <option value="all">All Servers</option>
              {systems.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.hostname} (ID: {s.id})
                </option>
              ))}
            </select>
          </div>

          {/* Export Formats */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Export Formats</label>
            <div className="flex items-center gap-2 pt-1">
              {['pdf', 'csv', 'json'].map((fmt) => (
                <button
                  key={fmt}
                  onClick={() => toggleFormat(fmt)}
                  className={`px-3 py-1 rounded text-xs font-mono uppercase font-semibold border transition ${
                    formats.includes(fmt)
                      ? 'bg-emerald-600 text-white border-emerald-500'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-800'
                  }`}
                >
                  {fmt}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between pt-2">
          {successMsg ? (
            <div className="text-xs text-emerald-400 flex items-center gap-1.5 font-mono">
              <CheckCircle2 className="w-4 h-4" />
              <span>{successMsg}</span>
            </div>
          ) : <div />}

          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition shadow-lg disabled:opacity-50"
          >
            {generating ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            <span>Generate Compliance Report</span>
          </button>
        </div>
      </div>

      {/* Generated Reports Archive */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wide">
          Generated Compliance Reports Archive ({reports.length})
        </h3>

        {reports.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs font-mono">
            No compliance reports generated yet. Click "Generate Compliance Report" above.
          </div>
        ) : (
          <div className="space-y-3">
            {reports.map((r) => (
              <div
                key={r.id}
                className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg flex items-center justify-between"
              >
                <div>
                  <div className="font-semibold text-sm text-slate-200">{r.title}</div>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    Scope: <span className="uppercase text-slate-300">{r.report_scope}</span> | Target: <span className="text-slate-300">{r.target_id}</span> | Generated: <span className="text-slate-300">{new Date(r.created_at).toLocaleString()}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {r.pdf_path && (
                    <a
                      href={`/api/v1/reports/${r.id}/download/pdf`}
                      download
                      className="px-3 py-1.5 bg-slate-900 hover:bg-emerald-950 text-emerald-400 border border-emerald-900/60 rounded text-xs font-mono font-semibold flex items-center gap-1.5 transition"
                    >
                      <Download className="w-3.5 h-3.5" />
                      PDF
                    </a>
                  )}
                  {r.csv_path && (
                    <a
                      href={`/api/v1/reports/${r.id}/download/csv`}
                      download
                      className="px-3 py-1.5 bg-slate-900 hover:bg-emerald-950 text-emerald-400 border border-emerald-900/60 rounded text-xs font-mono font-semibold flex items-center gap-1.5 transition"
                    >
                      <Download className="w-3.5 h-3.5" />
                      CSV
                    </a>
                  )}
                  {r.json_path && (
                    <a
                      href={`/api/v1/reports/${r.id}/download/json`}
                      download
                      className="px-3 py-1.5 bg-slate-900 hover:bg-emerald-950 text-emerald-400 border border-emerald-900/60 rounded text-xs font-mono font-semibold flex items-center gap-1.5 transition"
                    >
                      <Download className="w-3.5 h-3.5" />
                      JSON
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
