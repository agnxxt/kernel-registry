"use client";

import { useState } from 'react';
import { Cpu, Shield, Key, Rocket, ArrowRight, CheckCircle2, Globe, Server } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function SetupWizard() {
  const [step, setStep] = useState(1);
  const [masterKey, setMasterKey] = useState("");
  const [provider, setProvider] = useState("openai");
  const [openaiKey, setOpenaiKey] = useState("");
  const [localUrl, setLocalUrl] = useState("http://localhost:11434");
  const [localModel, setLocalModel] = useState("llama3");
  const [githubToken, setGithubToken] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleFinish = async () => {
    setLoading(true);
    try {
      const secrets: any = {
        'github-token': githubToken
      };

      if (provider === 'openai') {
        secrets['openai-key'] = openaiKey;
      } else {
        secrets['local-intelligence-url'] = localUrl;
        secrets['local-intelligence-model'] = localModel;
      }

      const res = await fetch('/api/v1/setup/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          master_key: masterKey,
          secrets: secrets
        })
      });
      if (res.ok) {
        setStep(4);
        setTimeout(() => {
           window.location.href = '/';
        }, 3000);
      } else {
        const txt = await res.text();
        alert("Setup failed: " + txt);
      }
    } catch (e) {
      alert("Error connecting to kernel");
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl">
        <div className="flex items-center gap-3 mb-8">
          <Cpu className="text-blue-500" size={32} />
          <h1 className="text-2xl font-black text-white tracking-tight">Kernel Setup</h1>
        </div>

        {/* Progress Bar */}
        <div className="flex gap-2 mb-12">
          {[1, 2, 3].map((s) => (
            <div key={s} className={`h-1 flex-1 rounded-full ${step >= s ? 'bg-blue-500' : 'bg-slate-800'}`} />
          ))}
        </div>

        {step === 1 && (
          <div className="animate-in fade-in slide-in-from-bottom-4">
            <Shield className="text-blue-400 mb-4" size={48} />
            <h2 className="text-xl font-bold text-white mb-2">Establish Master Key</h2>
            <p className="text-slate-400 text-sm mb-6">Secures your kernel and administrative actions.</p>
            <input 
              type="password"
              placeholder="Min 8 characters..."
              value={masterKey}
              onChange={(e) => setMasterKey(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 mb-6"
            />
            <button 
              onClick={() => setStep(2)}
              disabled={masterKey.length < 8}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2"
            >
              Continue <ArrowRight size={18} />
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="animate-in fade-in slide-in-from-bottom-4">
            <Globe className="text-emerald-400 mb-4" size={48} />
            <h2 className="text-xl font-bold text-white mb-2">Intelligence Source</h2>
            <p className="text-slate-400 text-sm mb-6">Choose between cloud vendors or open-source local models.</p>
            
            <div className="flex gap-4 mb-6">
              <button 
                onClick={() => setProvider('openai')}
                className={`flex-1 p-4 rounded-xl border transition-all flex flex-col items-center gap-2 ${provider === 'openai' ? 'border-blue-500 bg-blue-500/10' : 'border-slate-800 bg-slate-800/50'}`}
              >
                <Cloud className={provider === 'openai' ? 'text-blue-400' : 'text-slate-500'} />
                <span className="text-xs font-bold uppercase">Cloud (OpenAI)</span>
              </button>
              <button 
                onClick={() => setProvider('local')}
                className={`flex-1 p-4 rounded-xl border transition-all flex flex-col items-center gap-2 ${provider === 'local' ? 'border-emerald-500 bg-emerald-500/10' : 'border-slate-800 bg-slate-800/50'}`}
              >
                <Server className={provider === 'local' ? 'text-emerald-400' : 'text-slate-500'} />
                <span className="text-xs font-bold uppercase">Open Source (Local)</span>
              </button>
            </div>

            {provider === 'openai' ? (
              <input 
                type="password"
                placeholder="sk-..."
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 mb-6"
              />
            ) : (
              <div className="space-y-4 mb-6">
                <input 
                  type="text"
                  placeholder="Base URL (e.g. http://localhost:11434)"
                  value={localUrl}
                  onChange={(e) => setLocalUrl(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-emerald-500"
                />
                <input 
                  type="text"
                  placeholder="Model Name (e.g. llama3, mistral)"
                  value={localModel}
                  onChange={(e) => setLocalModel(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
            )}

            <button 
              onClick={() => setStep(3)}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2"
            >
              Continue <ArrowRight size={18} />
            </button>
          </div>
        )}

        {step === 3 && (
          <div className="animate-in fade-in slide-in-from-bottom-4">
            <Rocket className="text-purple-400 mb-4" size={48} />
            <h2 className="text-xl font-bold text-white mb-2">Physical Execution</h2>
            <p className="text-slate-400 text-sm mb-6">Optional: Add a GitHub token to allow governed code updates.</p>
            <input 
              type="password"
              placeholder="ghp_..."
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500 mb-6"
            />
            <button 
              onClick={handleFinish}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2"
            >
              {loading ? "Initializing..." : "Complete Setup"}
            </button>
          </div>
        )}

        {step === 4 && (
          <div className="text-center py-8 animate-in zoom-in">
            <CheckCircle2 className="text-emerald-500 mx-auto mb-4" size={64} />
            <h2 className="text-2xl font-black text-white mb-2">Kernel Online</h2>
            <p className="text-slate-400">Your Agent Kernel is initialized and ready for production.</p>
            <p className="text-slate-500 text-xs mt-4">Redirecting to Dashboard...</p>
          </div>
        )}
      </div>
    </main>
  );
}

function Cloud(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M17.5 19c.5 0 1-.1 1.4-.3a2.5 2.5 0 0 0 1.5-3.3 5 5 0 1 0-8.6-3 4 4 0 1 0-3.3 6.6h9Z" />
    </svg>
  )
}
