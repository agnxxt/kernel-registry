"use client";

import { useTelemetry } from '../hooks/useTelemetry';
import { CognitiveTrace } from '../components/CognitiveTrace';
import { GraphExplorer } from '../components/GraphExplorer';
import { Shield, ShieldAlert, Cpu, Globe, Users, Database } from 'lucide-react';

export default function Dashboard() {
  const { events, isConnected } = useTelemetry('ws://localhost:8000/ws/telemetry');

  return (
    <main className="p-8">
      {/* Header */}
      <header className="flex items-center justify-between mb-8 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Cpu className="text-blue-500" size={32} />
            Agent Kernel <span className="text-slate-500 font-light">Control Plane</span>
          </h1>
          <p className="text-slate-400 mt-1">Unified Observability for Governed AI Multi-Agent Systems</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-900 px-4 py-2 rounded-full border border-slate-800">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-xs font-bold uppercase tracking-wider">
              {isConnected ? 'Kernel Connected' : 'Disconnected'}
            </span>
          </div>
          <button className="bg-rose-600 hover:bg-rose-700 text-white px-6 py-2 rounded-full text-xs font-bold transition-colors flex items-center gap-2 shadow-lg shadow-rose-900/20">
            <ShieldAlert size={16} />
            Global Kill Switch
          </button>
        </div>
      </header>

      {/* Grid Layout */}
      <div className="grid grid-cols-12 gap-6 h-[calc(100vh-200px)]">
        
        {/* Left Column: Stats & Trace */}
        <div className="col-span-4 flex flex-col gap-6">
          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="flex items-center gap-2 text-slate-500 mb-1">
                <Users size={14} />
                <span className="text-[10px] uppercase font-bold tracking-wider">Active Agents</span>
              </div>
              <div className="text-2xl font-bold text-white">
                {new Set(events.map(e => e.agent)).size}
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <div className="flex items-center gap-2 text-slate-500 mb-1">
                <Database size={14} />
                <span className="text-[10px] uppercase font-bold tracking-wider">Cloud Zones</span>
              </div>
              <div className="text-2xl font-bold text-blue-400">Multi</div>
            </div>
          </div>

          <div className="flex-1 min-h-0">
            <CognitiveTrace events={events} />
          </div>
        </div>

        {/* Right Column: Knowledge Graph */}
        <div className="col-span-8 flex flex-col gap-6">
          <div className="flex-1">
            <GraphExplorer events={events} />
          </div>
          
          {/* Guardian / Policy Footer */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-3">
                <Shield className="text-emerald-400" size={24} />
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-tight">RACF Active</h3>
                  <p className="text-[10px] text-slate-500">Deontic Constraints Enforced</p>
                </div>
              </div>
              <div className="h-10 w-[1px] bg-slate-800" />
              <div className="flex items-center gap-3">
                <Globe className="text-blue-400" size={24} />
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-tight">Geopolitical Lens</h3>
                  <p className="text-[10px] text-slate-500">Cross-Border Compliance v2.0</p>
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">System Version</p>
              <p className="font-mono text-xs text-blue-400">agnxxt-kernel-v1.0.4-stable</p>
            </div>
          </div>
        </div>

      </div>
    </main>
  );
}
