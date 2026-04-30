import type { Metadata } from "next";
import "./globals.css";
import { Cpu, LayoutDashboard, Users, ShieldCheck } from "lucide-react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Agent Kernel Control Plane",
  description: "Unified Observability for Governed AI Multi-Agent Systems",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-200 antialiased flex min-h-screen">
        {/* Sidebar */}
        <aside className="w-64 border-r border-slate-800 bg-slate-900/50 flex flex-col p-6 sticky top-0 h-screen">
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
      </body>
    </html>
  );
}
