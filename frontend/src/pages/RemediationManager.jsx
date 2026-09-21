import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { 
  Wrench, CheckCircle, XCircle, Play, 
  AlertTriangle, Shield, Clock, FileText, CheckCircle2
} from 'lucide-react';

export const RemediationManager = () => {
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  // Approval Modal State
  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [targetPlanForApproval, setTargetPlanForApproval] = useState(null);
  const [approvalNotes, setApprovalNotes] = useState('Approved by Security Officer for off-peak execution');

  // Rejection Modal State
  const [rejectionModalOpen, setRejectionModalOpen] = useState(false);
  const [targetPlanForRejection, setTargetPlanForRejection] = useState(null);
  const [rejectionReason, setRejectionReason] = useState('Requires additional maintenance window coordination');

  const fetchPlans = async () => {
    try {
      let query = '/remediations/plans?limit=50';
      if (statusFilter) query += `&status=${statusFilter}`;
      const res = await api.get(query);
      setPlans(res.data);
      if (res.data.length > 0 && !selectedPlan) {
        loadPlanDetail(res.data[0].id);
      }
    } catch (err) {
      console.error("Failed to load plans", err);
    } finally {
      setLoading(false);
    }
  };

  const loadPlanDetail = async (planId) => {
    try {
      const res = await api.get(`/remediations/plans/${planId}`);
      setSelectedPlan(res.data);
    } catch (err) {
      console.error("Failed to load plan detail", err);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, [statusFilter]);

  const handleApprove = async () => {
    if (!targetPlanForApproval) return;
    setActionLoading(true);
    try {
      await api.post(`/remediations/plans/${targetPlanForApproval.id}/approve`, {
        approval_notes: approvalNotes
      });
      setApprovalModalOpen(false);
      await fetchPlans();
      await loadPlanDetail(targetPlanForApproval.id);
    } catch (err) {
      alert(err.response?.data?.detail || "Approval failed");
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!targetPlanForRejection) return;
    setActionLoading(true);
    try {
      await api.post(`/remediations/plans/${targetPlanForRejection.id}/reject`, {
        rejection_reason: rejectionReason
      });
      setRejectionModalOpen(false);
      await fetchPlans();
      await loadPlanDetail(targetPlanForRejection.id);
    } catch (err) {
      alert(err.response?.data?.detail || "Rejection failed");
    } finally {
      setActionLoading(false);
    }
  };

  const handleExecute = async (planId) => {
    setActionLoading(true);
    try {
      await api.post(`/remediations/plans/${planId}/execute`);
      await fetchPlans();
      await loadPlanDetail(planId);
    } catch (err) {
      alert(err.response?.data?.detail || "Execution failed");
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2.5">
            <Wrench className="w-6 h-6 text-emerald-400" />
            Controlled Remediation Engine & Human Approval Gate
          </h2>
          <p className="text-xs text-slate-400 mt-1">Role-gated orchestration of package upgrades, errata patching, and configuration enforcement</p>
        </div>

        {/* Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All Plan States</option>
          <option value="STAGED">Pending Approval (STAGED)</option>
          <option value="APPROVED">Approved for Execution</option>
          <option value="COMPLETED">Completed</option>
          <option value="REJECTED">Rejected</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Plans List Column */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Remediation Proposals</h3>
          
          <div className="space-y-2 max-h-[550px] overflow-y-auto pr-1">
            {plans.map((p) => (
              <div
                key={p.id}
                onClick={() => loadPlanDetail(p.id)}
                className={`p-3.5 rounded-xl border cursor-pointer transition ${
                  selectedPlan?.id === p.id
                    ? 'bg-emerald-500/10 border-emerald-500/40 text-slate-100'
                    : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-bold text-slate-200 truncate max-w-[180px]">
                    Plan #{p.id} — Host #{p.host_id}
                  </span>
                  <StatusBadge status={p.status} />
                </div>
                <p className="text-xs text-slate-400 line-clamp-1">{p.title}</p>
                <div className="flex items-center justify-between text-[11px] text-slate-500 mt-2 font-mono">
                  <span>{p.total_steps_count} actions</span>
                  <span className="text-rose-400 font-bold">{p.risk_level} Risk</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Selected Plan Details & Execution Controls */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
          {selectedPlan ? (
            <>
              {/* Header Info */}
              <div className="flex items-start justify-between border-b border-slate-800 pb-4">
                <div>
                  <div className="flex items-center gap-2.5">
                    <h3 className="text-base font-bold text-slate-100">{selectedPlan.title}</h3>
                    <StatusBadge status={selectedPlan.status} />
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Risk Assessment: <span className="text-rose-400 font-bold">{selectedPlan.risk_level}</span> · Created: {new Date(selectedPlan.created_at).toLocaleString()}
                  </p>
                  {selectedPlan.approval_notes && (
                    <p className="text-xs text-emerald-400 mt-1">Approval Notes: {selectedPlan.approval_notes}</p>
                  )}
                  {selectedPlan.rejection_reason && (
                    <p className="text-xs text-rose-400 mt-1">Rejection Reason: {selectedPlan.rejection_reason}</p>
                  )}
                </div>

                {/* Human-in-the-Loop Action Buttons */}
                <div className="flex items-center gap-2 shrink-0">
                  {selectedPlan.status === 'STAGED' && (
                    <>
                      <button
                        onClick={() => {
                          setTargetPlanForApproval(selectedPlan);
                          setApprovalModalOpen(true);
                        }}
                        className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold transition flex items-center gap-1.5 shadow-md shadow-emerald-500/20"
                      >
                        <CheckCircle className="w-3.5 h-3.5" /> Approve
                      </button>
                      <button
                        onClick={() => {
                          setTargetPlanForRejection(selectedPlan);
                          setRejectionModalOpen(true);
                        }}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-rose-600/80 text-slate-300 hover:text-white rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
                      >
                        <XCircle className="w-3.5 h-3.5" /> Reject
                      </button>
                    </>
                  )}

                  {selectedPlan.status === 'APPROVED' && (
                    <button
                      onClick={() => handleExecute(selectedPlan.id)}
                      disabled={actionLoading}
                      className="px-4 py-2 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 text-white rounded-xl text-xs font-bold transition flex items-center gap-2 shadow-lg shadow-emerald-500/20 disabled:opacity-50"
                    >
                      <Play className="w-3.5 h-3.5" />
                      {actionLoading ? 'Dispatching to MLM...' : 'Execute Remediation Actions'}
                    </button>
                  )}

                  {selectedPlan.status === 'COMPLETED' && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-lg text-xs font-bold">
                      <CheckCircle2 className="w-4 h-4" /> Fully Executed & Verified
                    </span>
                  )}
                </div>
              </div>

              {/* Steps List */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                  Remediation Action Steps ({selectedPlan.steps?.length || 0})
                </h4>
                
                <div className="space-y-2.5 max-h-[400px] overflow-y-auto pr-1">
                  {selectedPlan.steps?.map((step) => (
                    <div
                      key={step.id}
                      className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl flex items-center justify-between"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[10px] font-bold font-mono">
                            {step.step_number}
                          </span>
                          <span className="text-xs font-bold text-slate-200 font-mono">
                            {step.action_type}
                          </span>
                          <span className="text-xs font-semibold text-emerald-400 font-mono">
                            {step.target_package_or_errata}
                          </span>
                        </div>
                        <p className="text-xs text-slate-400 pl-7">{step.execution_log}</p>
                      </div>

                      <div className="text-right">
                        <StatusBadge status={step.status} />
                        {step.mlm_action_id && (
                          <p className="text-[10px] text-slate-500 font-mono mt-1">MLM Action #{step.mlm_action_id}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center p-12 text-slate-500 text-xs">Select a plan to review and approve.</div>
          )}
        </div>
      </div>

      {/* Approval Modal */}
      <Modal
        isOpen={approvalModalOpen}
        onClose={() => setApprovalModalOpen(false)}
        title="Approve Staged Remediation Plan"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-300">
            You are authorizing autonomous remediation actions for <strong className="text-slate-100">{targetPlanForApproval?.title}</strong>.
            Actions will be queued for dispatch through SUSE Multi-Linux Manager.
          </p>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Approval Authorization Notes:</label>
            <textarea
              rows="3"
              value={approvalNotes}
              onChange={(e) => setApprovalNotes(e.target.value)}
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              onClick={() => setApprovalModalOpen(false)}
              className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-xs font-semibold hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              onClick={handleApprove}
              disabled={actionLoading}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold"
            >
              Confirm Approval
            </button>
          </div>
        </div>
      </Modal>

      {/* Rejection Modal */}
      <Modal
        isOpen={rejectionModalOpen}
        onClose={() => setRejectionModalOpen(false)}
        title="Reject Staged Remediation Plan"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-300">
            Specify the rationale for rejecting remediation plan <strong className="text-slate-100">{targetPlanForRejection?.title}</strong>:
          </p>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Rejection Reason:</label>
            <textarea
              rows="3"
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-rose-500"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              onClick={() => setRejectionModalOpen(false)}
              className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg text-xs font-semibold hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              onClick={handleReject}
              disabled={actionLoading}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-bold"
            >
              Confirm Rejection
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
