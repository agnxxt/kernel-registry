"use client";

import { useEffect, useState } from 'react';
import { Users, Shield, Fingerprint, Activity } from 'lucide-react';

export default function IdentityManager() {
  const [identities, setIdentities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
  }, []);

  return (
    <div className="p-8">
      <header className="mb-12 border-b border-slate-800 pb-6">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
          <Users className="text-blue-500" size={32} />
          Identity Manager
        </h1>
        <p className="text-slate-400 mt-1">Verified Cognitive Identities & Epistemic Trust Scores</p>
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
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400">Canonical ID</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400">Type</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400">Issuer</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400">Created At</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-widest text-slate-400 text-right">Trust Level</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {identities.map((id) => (
                <tr key={id.canonical_id} className="hover:bg-slate-800/30 transition-colors group">
                  <td className="px-6 py-4 font-mono text-xs text-blue-400 flex items-center gap-2">
                    <Fingerprint size={14} className="text-slate-500 group-hover:text-blue-500" />
                    {id.canonical_id}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-slate-300">
                    <span className="bg-slate-800 px-2 py-1 rounded text-[10px] uppercase tracking-tighter">
                      {id.subject_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-400 italic">
                    {id.issuer}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-500">
                    {new Date(id.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                         <div className="bg-emerald-500 h-full w-[80%]" />
                      </div>
                      <span className="text-xs font-bold text-emerald-400">0.80</span>
                    </div>
                  </td>
                </tr>
              ))}
              {identities.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500 italic">
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
