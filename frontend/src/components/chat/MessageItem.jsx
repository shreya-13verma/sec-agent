import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';
import ThoughtTrace from './ThoughtTrace';
import ApprovalCard from './ApprovalCard';

export default function MessageItem({ message }) {
  const isAgent = message.sender === 'agent';

  return (
    <div className={`py-4 px-6 flex gap-4 ${isAgent ? 'bg-slate-900/30' : 'bg-transparent'}`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
        isAgent
          ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
          : 'bg-indigo-500/10 border border-indigo-500/30 text-indigo-400'
      }`}>
        {isAgent ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
      </div>

      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-300">
            {isAgent ? 'SUSE Compliance Agent' : 'Operator'}
          </span>
          <span className="text-[10px] text-slate-500 font-mono">
            {message.timestamp || new Date().toLocaleTimeString()}
          </span>
        </div>

        {isAgent && (message.thoughts?.length > 0 || message.toolCalls?.length > 0) && (
          <ThoughtTrace thoughts={message.thoughts} toolCalls={message.toolCalls} />
        )}

        <div className="prose prose-invert prose-sm max-w-none text-slate-200 text-sm leading-relaxed">
          <ReactMarkdown
            components={{
              table: ({ node, ...props }) => (
                <div className="overflow-x-auto my-3 border border-slate-800 rounded-lg">
                  <table className="min-w-full divide-y divide-slate-800 text-xs text-left" {...props} />
                </div>
              ),
              th: ({ node, ...props }) => (
                <th className="px-3 py-2 bg-slate-900/80 font-semibold text-slate-300 border-b border-slate-800" {...props} />
              ),
              td: ({ node, ...props }) => (
                <td className="px-3 py-2 border-b border-slate-800/60 font-mono text-slate-300" {...props} />
              ),
              code: ({ node, inline, ...props }) => (
                <code className="px-1.5 py-0.5 rounded bg-slate-800/80 text-emerald-300 font-mono text-xs border border-slate-700/50" {...props} />
              ),
              blockquote: ({ node, ...props }) => (
                <blockquote className="border-l-4 border-amber-500 bg-amber-950/20 p-2.5 rounded-r text-amber-200 text-xs my-2 font-mono" {...props} />
              )
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {message.approvalRequired && message.approvalToken && (
          <ApprovalCard
            approvalToken={message.approvalToken}
            plan={message.remediationPlan}
          />
        )}
      </div>
    </div>
  );
}
