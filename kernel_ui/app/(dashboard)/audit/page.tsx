"use client";

import { Shield, ExternalLink, Activity, Search, ListFilter } from 'lucide-react';

export default function AuditBrowser() {
  return (
    <div className="p-8 h-screen flex flex-col">
      <header className="mb-12 border-b border-slate-800 pb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Shield className="text-emerald-500" size={32} />
            Audit Trail Browser
          </h1>
          <p className="text-slate-400 mt-1">Forensic Trace of Kernel Access & Physical Executions</p>
        </div>
        
        <a 
          href="http://localhost:16686" 
          target="_blank" 
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-6 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 transition-colors text-xs font-bold text-white shadow-lg shadow-emerald-900/20"
        >
          <ExternalLink size={14} />
          Open Jaeger Inspector
        </a>
      </header>

      {/* Audit Stats */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Total Access Spans</div>
          <div className="text-3xl font-black text-white">1,248</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl border-l-emerald-500/50">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Policy Approvals</div>
          <div className="text-3xl font-black text-emerald-400">100%</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl border-l-rose-500/50">
          <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Blocked Violations</div>
          <div className="text-3xl font-black text-rose-500">0</div>
        </div>
      </div>

      {/* Mock Audit Log (In a real app, this would query the OTel / Jaeger API) */}
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
        <div className="bg-slate-800/50 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs font-bold text-slate-400 uppercase tracking-widest">
            <ListFilter size={14} />
            Live Access Feed
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-slate-950 rounded-full border border-slate-700">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-bold text-slate-400">Auditing Active</span>
          </div>
        </div>
        
        <div className="flex-1 overflow-auto p-6 space-y-4 font-mono text-xs">
          {[
            { time: "14:22:01", agent: "agent-alpha", action: "kernel.execute_plan", status: "SUCCESS" },
            { time: "14:22:02", agent: "agent-alpha", action: "opa.policy_check", status: "ALLOWED" },
            { time: "14:22:04", agent: "agent-alpha", action: "kernel.physical_execution", tool: "github", status: "SUCCESS" },
            { time: "14:23:15", agent: "agent-beta", action: "kernel.execute_plan", status: "SUCCESS" },
            { time: "14:23:16", agent: "agent-beta", action: "vault.read_secret", status: "AUTHORIZED" },
          ].map((log, i) => (
            <div key={i} className="flex items-center gap-4 p-3 bg-slate-800/30 rounded border border-slate-800/50 hover:border-emerald-500/30 transition-colors">
              <span className="text-slate-500">{log.time}</span>
              <span className="text-blue-400">[{log.agent}]</span>
              <span className="text-slate-300 font-bold">{log.action}</span>
              {log.tool && <span className="text-purple-400">→ {log.tool}</span>}
              <span className="ml-auto px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-[9px] font-bold tracking-widest">{log.status}</span>
            </div>
          ))}
          <div className="text-center py-4 text-slate-600 italic">
            See Jaeger for detailed distributed traces and timing analysis.
          </div>
        </div>
      </div>
    </div>
  );
}
