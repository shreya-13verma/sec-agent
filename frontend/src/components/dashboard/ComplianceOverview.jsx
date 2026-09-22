import React, { useState, useEffect } from 'react';
import { Server, ShieldCheck, AlertOctagon, FileCheck, CheckCircle2, ChevronRight } from 'lucide-react';
import { fetchSystems, fetchServerCompliance, fetchServerErrata } from '../../services/api';

export default function ComplianceOverview({ onSelectServerForChat }) {
  const [systems, setSystems] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [complianceData, setComplianceData] = useState(null);
  const [errataData, setErrataData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFleet();
  }, []);

  const loadFleet = async () => {
    setLoading(true);
    try {
      const data = await fetchSystems();
      setSystems(data);
      if (data.length > 0) {
        handleSelectServer(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectServer = async (server) => {
    setSelectedServer(server);
    try {
      const [comp, err] = await Promise.all([
        fetchServerCompliance(server.id),
        fetchServerErrata(server.id)
      ]);
      setComplianceData(comp);
      setErrataData(err);
    } catch (e) {
      console.error(e);
    }
  };

  const avgCompliance = systems.length
    ? (systems.reduce((acc, s) => acc + s.compliance_score, 0) / systems.length).toFixed(1)
    : 0;
  const totalSecErrata = systems.reduce((acc, s) => acc + s.security_errata_count, 0);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto h-[calc(100vh-4rem)] overflow-y-auto">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">MANAGED SERVERS</span>
            <Server className="w-5 h-5 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{systems.length}</div>
          <div className="text-xs text-emerald-400 mt-1">SUSE MLM Registered</div>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">FLEET COMPLIANCE</span>
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">{avgCompliance}%</div>
          <div className="text-xs text-slate-400 mt-1">CIS Benchmark Target &gt; 80%</div>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">SECURITY ERRATA</span>
            <AlertOctagon className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 mt-2">{totalSecErrata}</div>
          <div className="text-xs text-slate-400 mt-1">Pending Remediations</div>
        </div>

        <div className="p-5 bg-slate-900/60 border border-slate-800 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">FASTMCP PROTOCOL</span>
            <FileCheck className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2">Active</div>
          <div className="text-xs text-emerald-400 mt-1">12 Tools Connected</div>
        </div>
      </div>

      {/* Fleet Inventory & Detail Pane */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Server List */}
        <div className="lg:col-span-5 bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-3">
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wide">Registered Server Fleet</h2>
          <div className="space-y-2">
            {systems.map((s) => (
              <div
                key={s.id}
                onClick={() => handleSelectServer(s)}
                className={`p-3 rounded-lg border transition cursor-pointer flex items-center justify-between ${
                  selectedServer?.id === s.id
                    ? 'border-emerald-500/50 bg-emerald-950/20'
                    : 'border-slate-800/80 bg-slate-950/50 hover:bg-slate-800/40'
                }`}
              >
                <div>
                  <div className="font-semibold text-xs text-slate-200">{s.hostname}</div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">ID: {s.id} | {s.ip_address}</div>
                </div>
                <div className="text-right">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                    s.compliance_score >= 80 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-rose-950 text-rose-400 border border-rose-800/60'
                  }`}>
                    {s.compliance_score}%
                  </span>
                  <div className="text-[10px] text-amber-400 mt-1">{s.security_errata_count} Sec Errata</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Server Detail & OpenSCAP Results */}
        <div className="lg:col-span-7 bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
          {selectedServer ? (
            <>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h3 className="font-bold text-base text-slate-100">{selectedServer.hostname}</h3>
                  <p className="text-xs text-slate-400 font-mono">{selectedServer.os_release} | {selectedServer.kernel_version}</p>
                </div>
                {onSelectServerForChat && (
                  <button
                    onClick={() => onSelectServerForChat(selectedServer.id)}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1 transition"
                  >
                    <span>Audit in Chat</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Scan Summary */}
              {complianceData && (
                <div className="p-4 bg-slate-950/60 rounded-lg border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-300">CIS Benchmark Scan Details</span>
                    <span className="text-xs text-slate-400 font-mono">Score: <b>{complianceData.score}%</b></span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
                    <div className="p-2 bg-emerald-950/20 border border-emerald-900/40 rounded text-emerald-400">
                      ✅ {complianceData.pass_count} Passed
                    </div>
                    <div className="p-2 bg-rose-950/20 border border-rose-900/40 rounded text-rose-400">
                      ❌ {complianceData.fail_count} Failed
                    </div>
                    <div className="p-2 bg-slate-900 rounded text-slate-400">
                      ℹ️ {complianceData.other_count} Other
                    </div>
                  </div>

                  {complianceData.failed_rules?.length > 0 && (
                    <div className="space-y-1.5 pt-2">
                      <span className="text-[11px] font-semibold text-rose-400">Non-Compliant Rule Failures:</span>
                      <div className="space-y-1 max-h-40 overflow-y-auto pr-1">
                        {complianceData.failed_rules.map((rule, idx) => (
                          <div key={idx} className="p-2 bg-slate-900/80 rounded border border-slate-800 text-[11px] flex items-center justify-between">
                            <span className="text-slate-200">{rule.title}</span>
                            <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                              {rule.severity}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Errata Summary */}
              {errataData && (
                <div className="p-4 bg-slate-950/60 rounded-lg border border-slate-800 space-y-2">
                  <span className="text-xs font-bold text-slate-300">Pending Errata Advisories ({errataData.count})</span>
                  <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                    {errataData.errata?.map((err, idx) => (
                      <div key={idx} className="p-2 bg-slate-900/80 rounded border border-slate-800 text-xs flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-amber-300">{err.advisory_name}</div>
                          <div className="text-[10px] text-slate-400">{err.synopsis}</div>
                        </div>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                          {err.cve_id || 'N/A'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="p-12 text-center text-slate-500 text-xs">
              Select a server on the left to inspect OpenSCAP benchmark metrics and pending errata.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
