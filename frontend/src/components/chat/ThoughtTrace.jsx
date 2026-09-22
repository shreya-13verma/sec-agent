import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Cpu, CheckCircle2 } from 'lucide-react';

export default function ThoughtTrace({ thoughts = [], toolCalls = [] }) {
  const [isOpen, setIsOpen] = useState(true);

  if (thoughts.length === 0 && toolCalls.length === 0) return null;

  return (
    <div className="mb-3 rounded-lg border border-slate-800 bg-slate-900/50 overflow-hidden text-xs">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 flex items-center justify-between text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 transition"
      >
        <span className="flex items-center gap-2 font-mono">
          <Cpu className="w-3.5 h-3.5 text-emerald-400" />
          <span>Agent Reasoning & FastMCP Traces ({thoughts.length + toolCalls.length})</span>
        </span>
        {isOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
      </button>

      {isOpen && (
        <div className="px-3 py-2.5 border-t border-slate-800/60 bg-slate-950/40 space-y-1.5 font-mono">
          {thoughts.map((thought, idx) => (
            <div key={`thought-${idx}`} className="flex items-start gap-2 text-slate-300">
              <span className="text-emerald-500 select-none">›</span>
              <span>{thought}</span>
            </div>
          ))}
          {toolCalls.map((tool, idx) => (
            <div key={`tool-${idx}`} className="flex items-center gap-2 text-emerald-400 font-semibold pl-2 py-0.5 bg-emerald-950/20 rounded border border-emerald-900/30">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span>Tool Call: {typeof tool === 'string' ? tool : tool.tool} [OK]</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
