import React, { useState } from 'react';
import { AlertTriangle, Check, X, ShieldAlert, CheckCircle2, Loader2 } from 'lucide-react';
import { submitApprovalAction } from '../../services/api';

export default function ApprovalCard({ approvalToken, plan, onActionComplete }) {
  const [status, setStatus] = useState('pending'); // pending | loading | approved | rejected
  const [actionId, setActionId] = useState(null);
  const [comment, setComment] = useState('');
  const [error, setError] = useState(null);

  const handleAction = async (approved) => {
    setStatus('loading');
    setError(null);
    try {
      const res = await submitApprovalAction(approvalToken, approved, comment);
      setStatus(res.status);
      if (res.mlm_action_id) {
        setActionId(res.mlm_action_id);
      }
      if (onActionComplete) onActionComplete(res);
    } catch (err) {
      setError(err.message);
      setStatus('pending');
    }
  };

  return (
    <div className="my-4 p-4 rounded-xl border border-amber-500/40 bg-amber-950/20 text-slate-100 shadow-lg">
      <div className="flex items-center gap-2 text-amber-400 font-semibold mb-2">
        <ShieldAlert className="w-5 h-5 text-amber-400" />
        <span>Human-in-the-Loop Remediation Review</span>
      </div>

      <p className="text-xs text-slate-300 mb-3">
        The agent has prepared a state-modifying patch action. Confirm authorization to dispatch errata via SUSE MLM:
      </p>

      <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 text-xs space-y-1.5 mb-3 font-mono">
        <div><span className="text-slate-400">Target Server ID:</span> <span className="text-slate-200 font-bold">{plan?.server_id || 1001}</span></div>
        <div><span className="text-slate-400">Advisories:</span> <span className="text-amber-300">{plan?.advisories?.join(', ') || 'Security Patches'}</span></div>
        <div><span className="text-slate-400">CVEs Remediated:</span> <span className="text-emerald-400">{plan?.cves?.join(', ') || 'N/A'}</span></div>
        <div><span className="text-slate-400">Total Errata Packages:</span> <span className="text-slate-200">{plan?.errata_count || 0}</span></div>
      </div>

      {status === 'pending' && (
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Optional operator comment or change ticket reference..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className="w-full text-xs px-3 py-2 bg-slate-950/80 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/50"
          />
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleAction(true)}
              className="flex-1 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition shadow"
            >
              <Check className="w-4 h-4" />
              Approve & Deploy
            </button>
            <button
              onClick={() => handleAction(false)}
              className="px-4 py-2 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/60 text-rose-300 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition"
            >
              <X className="w-4 h-4" />
              Reject
            </button>
          </div>
        </div>
      )}

      {status === 'loading' && (
        <div className="flex items-center justify-center gap-2 py-3 text-xs text-amber-300">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span>Dispatching action to SUSE MLM FastMCP server...</span>
        </div>
      )}

      {status === 'approved' && (
        <div className="p-3 bg-emerald-950/40 border border-emerald-800/60 rounded-lg text-xs text-emerald-300 flex items-center gap-2 font-mono">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>Remediation Approved! Dispatched to SUSE MLM (Action ID: <b>{actionId || '89201'}</b>).</span>
        </div>
      )}

      {status === 'rejected' && (
        <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-lg text-xs text-rose-300 flex items-center gap-2 font-mono">
          <X className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span>Remediation proposal rejected by operator. System state unmodified.</span>
        </div>
      )}

      {error && (
        <div className="mt-2 text-xs text-rose-400 font-mono">
          Error: {error}
        </div>
      )}
    </div>
  );
}
