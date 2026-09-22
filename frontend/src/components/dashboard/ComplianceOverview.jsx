import React, { useState, useEffect } from 'react';
import { Server, ShieldCheck, AlertOctagon, FileCheck, CheckCircle2, ChevronRight, Search, Activity, RefreshCw, Cpu, Layers } from 'lucide-react';
import { fetchSystems, fetchServerCompliance, fetchServerErrata } from '../../services/api';

export default function ComplianceOverview({ onSelectServerForChat }) {
  const [systems, setSystems] = useState([]);
  const [filteredSystems, setFilteredSystems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all | compliant | noncompliant
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
      setFilteredSystems(data);
      if (data.length > 0) {
        handleSelectServer(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let list = systems;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(
        (s) =>
          s.hostname.toLowerCase().includes(q) ||
          s.ip_address.includes(q) ||
          s.os_release.toLowerCase().includes(q) ||
          String(s.id).includes(q)
      );
    }
    if (statusFilter === 'compliant') {
      list = list.filter((s) => s.compliance_score >= 80);
    } else if (statusFilter === 'noncompliant') {
      list = list.filter((s) => s.compliance_score < 80);
    }
    setFilteredSystems(list);
  }, [searchQuery, statusFilter, systems]);

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
  const compliantCount = systems.filter((s) => s.compliance_score >= 80).length;

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto h-[calc(100vh-4rem)] overflow-y-auto">
      {/* Metric Cards Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 rounded-xl shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">MANAGED SERVERS</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Server className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-slate-100 mt-2">{systems.length}</div>
          <div className="text-xs text-emerald-400 mt-1 font-mono">Live SUSE MLM Registered</div>
        </div>

        <div className="p-5 bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 rounded-xl shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">FLEET COMPLIANCE</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-slate-100 mt-2">{avgCompliance}%</div>
          <div className="text-xs text-slate-400 mt-1">{compliantCount} of {systems.length} servers passing (&gt;80%)</div>
        </div>

        <div className="p-5 bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 rounded-xl shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">SECURITY ERRATA</span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <AlertOctagon className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-amber-400 mt-2">{totalSecErrata}</div>
          <div className="text-xs text-slate-400 mt-1">Pending Critical/Important Advisories</div>
        </div>

        <div className="p-5 bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 border border-slate-800 rounded-xl shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400">FASTMCP PROTOCOL</span>
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-bold text-emerald-400 mt-2">Connected</div>
          <div className="text-xs text-slate-400 mt-1 font-mono">10.0.33.56 /rpc/api</div>
        </div>
      </div>

      {/* Fleet Inventory & Detail Pane */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Server List */}
        <div className="lg:col-span-5 bg-slate-900/70 border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-emerald-400" />
              Live Server Fleet ({filteredSystems.length})
            </h2>
            <button
              onClick={loadFleet}
              className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-slate-200 transition"
              title="Refresh"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Search & Filter Controls */}
          <div className="space-y-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search server, IP, or OS release..."
                className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>

            <div className="flex items-center gap-1 text-[11px]">
              <button
                onClick={() => setStatusFilter('all')}
                className={`px-2.5 py-0.5 rounded border transition ${
                  statusFilter === 'all'
                    ? 'bg-slate-800 text-white border-slate-600'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-900'
                }`}
              >
                All ({systems.length})
              </button>
              <button
                onClick={() => setStatusFilter('compliant')}
                className={`px-2.5 py-0.5 rounded border transition ${
                  statusFilter === 'compliant'
                    ? 'bg-emerald-950 text-emerald-300 border-emerald-700'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-900'
                }`}
              >
                Compliant ({compliantCount})
              </button>
              <button
                onClick={() => setStatusFilter('noncompliant')}
                className={`px-2.5 py-0.5 rounded border transition ${
                  statusFilter === 'noncompliant'
                    ? 'bg-rose-950 text-rose-300 border-rose-700'
                    : 'bg-slate-950 text-slate-400 border-slate-800 hover:bg-slate-900'
                }`}
              >
                Action Required ({systems.length - compliantCount})
              </button>
            </div>
          </div>

          {/* List items */}
          <div className="space-y-2 max-h-[480px] overflow-y-auto pr-1">
            {filteredSystems.map((s) => (
              <div
                key={s.id}
                onClick={() => handleSelectServer(s)}
                className={`p-3 rounded-lg border transition cursor-pointer flex items-center justify-between ${
                  selectedServer?.id === s.id
                    ? 'border-emerald-500/60 bg-emerald-950/20 shadow-md shadow-emerald-950/50'
                    : 'border-slate-800/80 bg-slate-950/60 hover:bg-slate-800/40'
                }`}
              >
                <div>
                  <div className="font-semibold text-xs text-slate-200 flex items-center gap-1.5">
                    <span>{s.hostname}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                    ID: <span className="text-slate-300">{s.id}</span> · IP: <span className="text-slate-300">{s.ip_address}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5 font-sans truncate max-w-[200px]">
                    {s.os_release}
                  </div>
                </div>
                <div className="text-right">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded font-mono ${
                    s.compliance_score >= 80 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-rose-950 text-rose-400 border border-rose-800/60'
                  }`}>
                    {s.compliance_score}%
                  </span>
                  <div className="text-[10px] text-amber-400 mt-1 font-mono">
                    {s.security_errata_count} Sec Errata
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Server Detail & OpenSCAP Results */}
        <div className="lg:col-span-7 bg-slate-900/70 border border-slate-800 rounded-xl p-5 space-y-4">
          {selectedServer ? (
            <>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-lg text-slate-100">{selectedServer.hostname}</h3>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                      ID: {selectedServer.id}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">
                    {selectedServer.os_release} · IP: {selectedServer.ip_address} · Kernel: {selectedServer.kernel_version}
                  </p>
                </div>
                {onSelectServerForChat && (
                  <button
                    onClick={() => onSelectServerForChat(selectedServer.hostname)}
                    className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition shadow"
                  >
                    <span>Audit in Chat</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Scan Summary Card */}
              {complianceData && (
                <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      CIS Benchmark Scan Status
                    </span>
                    <span className="text-xs font-mono">
                      Score: <b className={complianceData.score >= 80 ? 'text-emerald-400' : 'text-rose-400'}>{complianceData.score}%</b>
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
                    <div className="p-2.5 bg-emerald-950/30 border border-emerald-900/50 rounded-lg text-emerald-400">
                      <div className="text-lg font-bold">{complianceData.pass_count}</div>
                      <div className="text-[10px] text-emerald-300">Rules Passed</div>
                    </div>
                    <div className="p-2.5 bg-rose-950/30 border border-rose-900/50 rounded-lg text-rose-400">
                      <div className="text-lg font-bold">{complianceData.fail_count}</div>
                      <div className="text-[10px] text-rose-300">Rules Failed</div>
                    </div>
                    <div className="p-2.5 bg-slate-900 border border-slate-800 rounded-lg text-slate-400">
                      <div className="text-lg font-bold">{complianceData.other_count}</div>
                      <div className="text-[10px] text-slate-400">N/A Rules</div>
                    </div>
                  </div>

                  {complianceData.failed_rules?.length > 0 && (
                    <div className="space-y-1.5 pt-2">
                      <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">
                        Failed Security Benchmark Rules:
                      </span>
                      <div className="space-y-1 max-h-44 overflow-y-auto pr-1">
                        {complianceData.failed_rules.map((rule, idx) => (
                          <div key={idx} className="p-2 bg-slate-900/90 rounded border border-slate-800 text-[11px] flex items-center justify-between">
                            <div>
                              <div className="text-slate-200 font-medium">{rule.title}</div>
                              <div className="text-[10px] font-mono text-slate-500">{rule.rule_identifier}</div>
                            </div>
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

              {/* Errata Summary Card */}
              {errataData && (
                <div className="p-4 bg-slate-950/70 rounded-xl border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                      <AlertOctagon className="w-4 h-4 text-amber-400" />
                      Pending Errata Advisories ({errataData.count})
                    </span>
                  </div>
                  <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                    {errataData.errata?.map((err, idx) => (
                      <div key={idx} className="p-2 bg-slate-900/90 rounded border border-slate-800 text-xs flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-amber-300">{err.advisory_name}</div>
                          <div className="text-[10px] text-slate-400 truncate max-w-[340px]">{err.synopsis}</div>
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
