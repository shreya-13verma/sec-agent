import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Terminal, Loader2, Server, ShieldCheck, AlertTriangle } from 'lucide-react';
import MessageItem from './MessageItem';
import { streamChatMessage } from '../../services/api';

const QUICK_PROMPTS = [
  "Which production servers failed CIS benchmark audits?",
  "Check OpenSCAP compliance score and failed rules for hana-node1",
  "Inspect pending security errata and vulnerabilities on trento-server",
  "Prepare remediation proposal for security errata on klp-server",
  "Summarize fleet posture and non-compliant hosts"
];

export default function ChatContainer({ currentSessionId, setSessionId, initialPrompt }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'agent',
      content: '👋 **Welcome to the SUSE Multi-Linux Manager Security Agent.**\n\nConnected live to SUSE MLM / Uyuni (`https://10.0.33.56`) via FastMCP. I can audit native OpenSCAP benchmark profiles, evaluate pending security errata, and prepare operator-approved remediations across your 7 managed Linux servers (`trento-server`, `hana-node1`, `hana-node2`, `klp-server`, `monitoring-srv`, `rhel10`, `ubuntu240`).\n\nSelect a prompt below or type your inquiry to begin:',
      thoughts: [],
      toolCalls: [],
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  useEffect(() => {
    if (initialPrompt) {
      handleSend(initialPrompt);
    }
  }, [initialPrompt]);

  const handleSend = (textToSend) => {
    const query = textToSend || input;
    if (!query.trim() || isStreaming) return;

    const userMessageId = `user_${Date.now()}`;
    const botMessageId = `bot_${Date.now()}`;

    // Add user message
    const userMsg = {
      id: userMessageId,
      sender: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString()
    };

    // Placeholder bot message
    const botMsg = {
      id: botMessageId,
      sender: 'agent',
      content: '',
      thoughts: [],
      toolCalls: [],
      approvalRequired: false,
      approvalToken: null,
      remediationPlan: null,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages((prev) => [...prev, userMsg, botMsg]);
    setInput('');
    setIsStreaming(true);

    streamChatMessage(query, currentSessionId, (event, data) => {
      if (event === 'session_id') {
        if (data?.session_id && setSessionId) {
          setSessionId(data.session_id);
        }
      } else if (event === 'thought') {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessageId
              ? { ...msg, thoughts: [...(msg.thoughts || []), data.thought] }
              : msg
          )
        );
      } else if (event === 'tool_call') {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessageId
              ? { ...msg, toolCalls: [...(msg.toolCalls || []), data] }
              : msg
          )
        );
      } else if (event === 'approval_required') {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessageId
              ? {
                  ...msg,
                  approvalRequired: true,
                  approvalToken: data.approval_token,
                  remediationPlan: data.plan
                }
              : msg
          )
        );
      } else if (event === 'token') {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessageId
              ? { ...msg, content: (msg.content || '') + data.token }
              : msg
          )
        );
      } else if (event === 'done' || event === 'error') {
        setIsStreaming(false);
      }
    });
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-4rem)] bg-slate-950">
      {/* Top Banner */}
      <div className="px-6 py-2 bg-slate-900/40 border-b border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-2 font-mono">
          <Server className="w-3.5 h-3.5 text-emerald-400" />
          <span>Live MLM Fleet: <strong className="text-slate-200">7 Active Servers</strong> (10.0.33.56)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/50 font-mono text-[10px]">
            LangGraph + FastMCP
          </span>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-800/40">
        {messages.map((m) => (
          <MessageItem key={m.id} message={m} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input & Quick Chips Area */}
      <div className="border-t border-slate-800 bg-slate-900/80 p-4 backdrop-blur space-y-3">
        {/* Quick Chips */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs no-scrollbar">
          <span className="text-slate-500 font-mono text-[11px] flex items-center gap-1 flex-shrink-0">
            <Sparkles className="w-3 h-3 text-emerald-400" /> Prompts:
          </span>
          {QUICK_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              disabled={isStreaming}
              className="px-3 py-1 rounded-full bg-slate-800/90 hover:bg-emerald-950 hover:border-emerald-700 text-slate-300 border border-slate-700/60 whitespace-nowrap transition text-[11px] flex-shrink-0 hover:text-white"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Text Input Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2"
        >
          <div className="relative flex-1">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask SUSE Compliance Agent (e.g. 'Audit hana-node1' or 'Remediate klp-server')..."
              disabled={isStreaming}
              className="w-full pl-4 pr-10 py-3 bg-slate-900 border border-slate-700/80 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition shadow-inner"
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className={`px-5 py-3 rounded-xl font-medium text-sm flex items-center gap-2 transition ${
              input.trim() && !isStreaming
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-950'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
            }`}
          >
            {isStreaming ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}
