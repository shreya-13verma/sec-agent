import React from 'react';

export const StatusBadge = ({ status }) => {
  const getBadgeStyle = (st) => {
    switch (st?.toUpperCase()) {
      case 'COMPLIANT':
      case 'SUCCESS':
      case 'PASS':
      case 'APPROVED':
      case 'STABLE':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'NON_COMPLIANT':
      case 'MEDIUM':
      case 'STAGED':
      case 'MINOR_DRIFT':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'CRITICAL':
      case 'FAIL':
      case 'CRITICAL_DRIFT':
      case 'FAILED':
      case 'REJECTED':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'RUNNING':
      case 'IN_PROGRESS':
      case 'ANALYZING':
      case 'DISPATCHED':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 animate-pulse';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getBadgeStyle(status)}`}>
      {status || 'UNKNOWN'}
    </span>
  );
};
