import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { ComplianceGauge } from '../components/ComplianceGauge';
import { 
  FileCheck2, Play, CheckCircle, AlertTriangle, 
  Clock, RefreshCw, ChevronDown, ChevronRight, Shield
} from 'lucide-react';

export const ComplianceScans = () => {
  const [frameworks, setFrameworks] = useState([]);
  const [scans, setScans] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scanningFwId, setScanningFwId] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');

  const fetchScansData = async () => {
    try {
      const [fwRes, scansRes] = await Promise.all([
        api.get('/compliance/frameworks'),
        api.get('/compliance/scans?limit=20')
      ]);
      setFrameworks(fwRes.data);
      setScans(scansRes.data);
      if (scansRes.data.length > 0 && !selectedScan) {
        loadScanDetail(scansRes.data[0].id);
      }
    } catch (err) {
      console.error("Failed to load scans", err);
    } finally {
      setLoading(false);
    }
  };

  const loadScanDetail = async (scanId) => {
    try {
      const res = await api.get(`/compliance/scans/${scanId}`);
      setSelectedScan(res.data);
      setFindings(res.data.findings || []);
    } catch (err) {
      console.error("Failed to load scan detail", err);
    }
  };

  useEffect(() => {
    fetchScansData();
  }, []);

  const handleTriggerScan = async (frameworkId) => {
    setScanningFwId(frameworkId);
    try {
      const res = await api.post('/compliance/scans', { framework_id: frameworkId });
      await fetchScansData();
      await loadScanDetail(res.data.id);
    } catch (err) {
      console.error("Failed to execute scan", err);
    } finally {
      setScanningFwId(null);
    }
  };

  const filteredFindings = statusFilter
    ? findings.filter(f => f.status === statusFilter)
    : findings;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100">Compliance & Regulatory Hardening Audits</h2>
        <p className="text-xs text-slate-400 mt-1">Continuous verification against CIS Benchmarks, HIPAA, and PCI-DSS standards</p>
      </div>

      {/* Framework Trigger Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {frameworks.map((fw) => (
          <div key={fw.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-800 text-emerald-400 border border-slate-700 rounded">
                  {fw.code}
                </span>
                <span className="text-xs text-slate-400 font-medium">{fw.rule_count} Rules</span>
              </div>
              <h3 className="text-sm font-bold text-slate-100 mt-2">{fw.name}</h3>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">{fw.description}</p>
            </div>

            <button
              onClick={() => handleTriggerScan(fw.id)}
              disabled={scanningFwId === fw.id}
              className="mt-4 w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition disabled:opacity-50"
            >
              <Play className={`w-3.5 h-3.5 ${scanningFwId === fw.id ? 'animate-spin' : ''}`} />
              {scanningFwId === fw.id ? 'Running Audit...' : 'Audit Fleet Now'}
            </button>
          </div>
        ))}
      </div>

      {/* Scan Detail & Findings */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Past Scans List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Recent Audit Runs</h3>
          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {scans.map((sc) => (
              <div
                key={sc.id}
                onClick={() => loadScanDetail(sc.id)}
                className={`p-3 rounded-xl border cursor-pointer transition ${
                  selectedScan?.id === sc.id
                    ? 'bg-emerald-500/10 border-emerald-500/40 text-slate-100'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-200">
                    {sc.framework?.name || `Framework #${sc.framework_id}`}
                  </span>
                  <span className="text-xs font-black text-emerald-400">{sc.overall_score}%</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 font-mono">
                  <span>{sc.hosts_scanned_count} hosts</span>
                  <span>{new Date(sc.started_at).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Selected Scan Findings Details */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
          {selectedScan ? (
            <>
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-100">
                    {selectedScan.framework?.name} Audit Findings
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Scanned {selectedScan.hosts_scanned_count} hosts · {selectedScan.passed_rules_count} Passed · {selectedScan.failed_rules_count} Failed
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setStatusFilter('')}
                    className={`px-2.5 py-1 text-xs rounded-lg font-semibold transition ${
                      statusFilter === '' ? 'bg-slate-700 text-white' : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    All ({findings.length})
                  </button>
                  <button
                    onClick={() => setStatusFilter('FAIL')}
                    className={`px-2.5 py-1 text-xs rounded-lg font-semibold transition ${
                      statusFilter === 'FAIL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    Failures
                  </button>
                  <button
                    onClick={() => setStatusFilter('PASS')}
                    className={`px-2.5 py-1 text-xs rounded-lg font-semibold transition ${
                      statusFilter === 'PASS' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    Passed
                  </button>
                </div>
              </div>

              {/* Findings Table */}
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                {filteredFindings.map((finding) => (
                  <div
                    key={finding.id}
                    className="p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl flex items-start justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <StatusBadge status={finding.status} />
                        <span className="text-xs font-mono font-bold text-slate-200">
                          {finding.rule?.rule_identifier}
                        </span>
                        <span className="text-xs text-slate-300 font-semibold">
                          {finding.rule?.title}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400">{finding.finding_details}</p>
                      <p className="text-[11px] font-mono text-slate-500">
                        Observed: <span className="text-slate-300">{finding.observed_value}</span>
                      </p>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500 shrink-0">
                      Host #{finding.host_id}
                    </span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-center p-12 text-slate-500 text-xs">Select a scan to inspect findings.</div>
          )}
        </div>
      </div>
    </div>
  );
};
