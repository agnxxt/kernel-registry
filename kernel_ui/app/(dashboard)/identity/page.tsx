"use client";

import { useEffect, useState } from 'react';
import { Users, Shield, Fingerprint, Activity, Power, PowerOff, RefreshCw } from 'lucide-react';

export default function IdentityManager() {
  const [identities, setIdentities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchIdentities();
  }, []);

  const fetchIdentities = () => {
    setLoading(true);
    fetch('/api/v1/admin/identities')
      .then(res => res.json())
      .then(data => {
        setIdentities(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch identities", err);
        setLoading(false);
      });
  };

  const handleDecommission = (id: string) => {
    if (confirm(`Are you sure you want to decommission agent ${id}? This will revoke all secrets.`)) {
        fetch(`/api/v1/lifecycle/decommission/${id}`, { method: 'POST' })
          .then(() => fetchIdentities());
    }
  };

  const handleActivate = (id: string) => {
    fetch(`/api/v1/lifecycle/activate/${id}`, { method: 'POST' })
      .then(() => fetchIdentities());
  };

  return (
    <div className="p-8">
      <header className="mb-12 border-b border-slate-800 pb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Users className="text-blue-500" size={32} />
            Lifecycle Manager
          </h1>
          <p className="text-slate-400 mt-1">Industrial ALM: Birth, Revision, and Retirement</p>
        </div>
        <button onClick={fetchIdentities} className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
          <RefreshCw size={20} className={loading ? "animate-spin text-blue-500" : "text-slate-500"} />
        </button>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/50">
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400">Canonical ID / DID</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400">Lifecycle State</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400">CAAS Blocks</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {identities.map((id) => (
                <tr key={id.artifact_id} className="hover:bg-slate-800/30 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="font-mono text-xs text-blue-400 flex items-center gap-2 mb-1">
                      <Fingerprint size={14} className="text-slate-500" />
                      {id.artifact_id}
                    </div>
                    <div className="text-[10px] text-slate-600 font-mono pl-6">{id.did || "No DID"}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-[9px] font-black uppercase tracking-tighter ${
                        id.lifecycle_state === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 
                        id.lifecycle_state === 'REVOKED' ? 'bg-rose-500/10 text-rose-500 border border-rose-500/20' :
                        'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}>
                      {id.lifecycle_state}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                        {id.version_snapshot ? Object.entries(id.version_snapshot).map(([key, val]: [string, any]) => (
                            <span key={key} className="text-[9px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700">
                                {key}:{String(val)}
                            </span>
                        )) : <span className="text-[9px] text-slate-600 italic">None</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      {id.lifecycle_state !== 'ACTIVE' && id.lifecycle_state !== 'REVOKED' && (
                        <button 
                            onClick={() => handleActivate(id.artifact_id)}
                            className="p-1.5 hover:bg-emerald-500/10 text-emerald-500 rounded transition-colors" title="Activate">
                          <Power size={14} />
                        </button>
                      )}
                      {id.lifecycle_state !== 'REVOKED' && (
                        <button 
                            onClick={() => handleDecommission(id.artifact_id)}
                            className="p-1.5 hover:bg-rose-500/10 text-rose-500 rounded transition-colors" title="Decommission">
                          <PowerOff size={14} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {identities.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-slate-500 italic">
                    No identities registered in the kernel.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
