"use client";

import { useEffect, useState } from "react";
import { getSettings } from "@/lib/settings";

interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  resource_id: string;
  metadata: any;
  timestamp: string;
}

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      const settings = getSettings();
      const res = await fetch(`${settings.apiBaseUrl}/org/audit-logs`, {
         headers: {
           "Authorization": `Bearer ${localStorage.getItem("token")}`,
         },
      });
      if (res.ok) {
        setLogs(await res.json());
      }
      setLoading(false);
    };
    fetchLogs();
  }, []);

  if (loading) return <div className="p-20 text-center font-medium text-slate-400">Loading enterprise logs...</div>;

  return (
    <div className="max-w-5xl mx-auto p-10">
      <header className="mb-12">
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Enterprise Audit Trail</h1>
        <p className="text-slate-500 mt-2 font-medium">Full transparency on organizational activities and compliance events.</p>
      </header>

      <div className="bg-white rounded-[2.5rem] border border-slate-100 shadow-xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 border-b border-slate-100">
            <tr>
              <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-slate-400">Action</th>
              <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-slate-400">User ID</th>
              <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-slate-400">Resource</th>
              <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-50/50 transition-colors">
                <td className="px-8 py-6">
                  <span className="px-3 py-1 rounded-full bg-violet-50 text-violet-600 text-[10px] font-black uppercase tracking-widest">
                    {log.action.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="px-8 py-6 text-sm font-mono text-slate-500">{log.user_id?.slice(0, 8) || "System"}</td>
                <td className="px-8 py-6 text-sm text-slate-600 font-medium">{log.resource_id || "—"}</td>
                <td className="px-8 py-6 text-sm text-slate-400 text-right font-medium">
                  {new Date(log.timestamp).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {logs.length === 0 && (
          <div className="p-20 text-center">
            <p className="text-slate-300 font-bold">No audit events recorded yet.</p>
          </div>
        )}
      </div>
      
      <footer className="mt-8 text-center">
         <p className="text-xs text-slate-400 font-medium">Compliance Requirement: Audit logs are retained for 90 days. For exports, contact support.</p>
      </footer>
    </div>
  );
}
