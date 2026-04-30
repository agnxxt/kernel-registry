import React from 'react';
import { TelemetryEvent } from '../hooks/useTelemetry';
import { Activity, Zap, Brain } from 'lucide-react';

interface Props {
  events: TelemetryEvent[];
}

export const CognitiveTrace: React.FC<Props> = ({ events }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 h-full overflow-hidden flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold flex items-center gap-2 text-white">
          <Activity className="text-blue-400" />
          Real-time Cognitive Trace
        </h2>
        <span className="text-xs text-slate-500 uppercase tracking-widest font-semibold">Active Engine</span>
      </div>
      
      <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar">
        {events.length === 0 ? (
          <div className="h-full flex items-center justify-center text-slate-600 italic">
            Waiting for agent telemetry...
          </div>
        ) : (
          events.map((event, idx) => (
            <div 
              key={`${event.action_id}-${idx}`}
              className={`p-4 rounded-lg border flex flex-col gap-2 transition-all animate-in fade-in slide-in-from-left-2 ${
                event.pathway?.includes('Slow') 
                  ? 'bg-purple-900/20 border-purple-500/30' 
                  : 'bg-blue-900/20 border-blue-500/30'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-slate-400">{event.agent}</span>
                <span className="text-[10px] text-slate-500">{event.timestamp}</span>
              </div>
              
              <div className="flex items-center gap-3">
                {event.pathway?.includes('Slow') ? (
                  <Brain size={18} className="text-purple-400" />
                ) : (
                  <Zap size={18} className="text-blue-400" />
                )}
                <span className={`text-sm font-semibold ${
                  event.pathway?.includes('Slow') ? 'text-purple-300' : 'text-blue-300'
                }`}>
                  {event.pathway}
                </span>
              </div>

              <div className="flex flex-wrap gap-1 mt-1">
                {event.theories.map((theory) => (
                  <span 
                    key={theory}
                    className="px-2 py-0.5 rounded-full text-[10px] bg-slate-800 text-slate-400 border border-slate-700"
                  >
                    {theory.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
