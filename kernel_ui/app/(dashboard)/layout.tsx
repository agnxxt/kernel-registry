import { Cpu, LayoutDashboard, Users, ShieldCheck, History } from "lucide-react";
import Link from "next/link";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col p-6 sticky top-0 h-screen shrink-0">
        <div className="flex items-center gap-3 mb-12">
          <Cpu className="text-blue-500" size={28} />
          <span className="font-extrabold text-white tracking-tight">KERNEL</span>
        </div>

        <nav className="flex flex-col gap-2">
          <Link href="/" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors group">
            <LayoutDashboard size={18} className="text-slate-400 group-hover:text-blue-400" />
            <span className="text-sm font-medium">Dashboard</span>
          </Link>
          <Link href="/identity" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors group">
            <Users size={18} className="text-slate-400 group-hover:text-blue-400" />
            <span className="text-sm font-medium">Identities</span>
          </Link>
          <Link href="/policies" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors group">
            <ShieldCheck size={18} className="text-slate-400 group-hover:text-blue-400" />
            <span className="text-sm font-medium">Policies</span>
          </Link>
        
          <Link href="/audit" className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors group">
            <History size={18} className="text-slate-400 group-hover:text-blue-400" />
            <span className="text-sm font-medium">Audit Trail</span>
          </Link>
        </nav>

        <div className="mt-auto pt-6 border-t border-slate-800">
          <div className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">System Version</div>
          <div className="font-mono text-[10px] text-blue-400">v1.0.4-stable</div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
}
