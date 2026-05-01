"use client";

import { useEffect, useState } from 'react';
import { ShieldCheck, Save, RefreshCw, AlertCircle } from 'lucide-react';

export default function PolicyEditor() {
  const [policies, setPolicies] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = () => {
    setLoading(true);
    fetch('/api/v1/admin/policies')
      .then(res => res.json())
      .then(data => {
        setPolicies(JSON.stringify(data, null, 2));
        setLoading(false);
      })
      .catch(err => {
        setError("Failed to load policies");
        setLoading(false);
      });
  };

  const handleSave = () => {
    setSaving(true);
    setError("");
    try {
      const parsed = JSON.parse(policies);
      fetch('/api/v1/admin/policies', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed)
      })
      .then(res => res.json())
      .then(() => {
        setSaving(false);
        alert("Policies updated successfully");
      })
      .catch(() => {
        setError("Failed to save policies");
        setSaving(false);
      });
    } catch (e) {
      setError("Invalid JSON format");
      setSaving(false);
    }
  };

  return (
    <div className="p-8 h-screen flex flex-col">
      <header className="mb-8 flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <ShieldCheck className="text-blue-500" size={32} />
            Policy Editor
          </h1>
          <p className="text-slate-400 mt-1">Manage Deontic Guardrails & Global Constraints</p>
        </div>
        
        <div className="flex gap-4">
          <button 
            onClick={fetchPolicies}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors text-xs font-bold"
          >
            <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
            Reload
          </button>
          <button 
            onClick={handleSave}
            disabled={saving || loading}
            className="flex items-center gap-2 px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition-colors text-xs font-bold text-white shadow-lg shadow-blue-900/20"
          >
            <Save size={14} />
            {saving ? "Saving..." : "Save Policies"}
          </button>
        </div>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg flex items-center gap-3 text-rose-500 text-sm">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
        <div className="bg-slate-800/50 px-4 py-2 border-b border-slate-800 flex items-center justify-between">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">policies.json</span>
          <span className="text-[10px] text-slate-500 italic">JSON format required</span>
        </div>
        <textarea
          value={policies}
          onChange={(e) => setPolicies(e.target.value)}
          disabled={loading}
          className="flex-1 w-full bg-transparent p-6 font-mono text-sm text-blue-400 focus:outline-none resize-none leading-relaxed"
          spellCheck={false}
        />
      </div>
    </div>
  );
}
