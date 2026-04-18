"use client";

import { useEffect, useState } from "react";
import { getLeads, getLeadMessages, updateLeadStatus, type Lead, type Message } from "@/lib/api/leads";

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messagesLoading, setMessagesLoading] = useState(false);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const data = await getLeads();
      setLeads(data);
    } finally {
      setLoading(false);
    }
  };

  const selectLead = async (lead: Lead) => {
    setSelectedLead(lead);
    setMessagesLoading(true);
    try {
      const data = await getLeadMessages(lead.id);
      setMessages(data);
    } finally {
      setMessagesLoading(false);
    }
  };

  const setStatus = async (status: string) => {
    if (!selectedLead) return;
    try {
      await updateLeadStatus(selectedLead.id, status);
      setSelectedLead({ ...selectedLead, status });
      setLeads(leads.map(l => l.id === selectedLead.id ? { ...l, status } : l));
    } catch (e) {
      alert("Failed to update status.");
    }
  };

  if (loading) return <div className="p-10 text-center font-medium text-slate-500">Retrieving intelligence...</div>;

  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden bg-slate-50">
      {/* Lead List */}
      <aside className="w-1/3 flex flex-col border-r border-slate-200 bg-white">
        <header className="p-8 border-b border-slate-100">
          <h1 className="text-2xl font-black text-slate-900">Lead Intelligence</h1>
          <p className="text-xs font-bold text-slate-400 mt-1 uppercase tracking-widest">High Intent Pipeline</p>
        </header>
        <div className="flex-1 overflow-y-auto">
          {leads.map((l) => (
            <button
              key={l.id}
              onClick={() => selectLead(l)}
              className={`w-full p-6 text-left border-b border-slate-50 transition-all hover:bg-slate-50 ${
                selectedLead?.id === l.id ? "bg-violet-50 border-r-4 border-r-violet-600" : ""
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest ${
                    l.score > 80 ? "bg-emerald-100 text-emerald-600" : "bg-slate-100 text-slate-500"
                }`}>
                    Score: {l.score}
                </span>
                <span className="text-[10px] font-bold text-slate-400 uppercase">{l.intent || 'unclassified'}</span>
              </div>
              <h3 className="font-bold text-slate-900">{l.full_name || l.phone}</h3>
              <p className="text-xs text-slate-400 mt-1 truncate">{l.email || l.phone}</p>
            </button>
          ))}
        </div>
      </aside>

      {/* Lead Detail / Conversation */}
      <main className="flex-1 flex flex-col relative">
        {selectedLead ? (
          <>
            <header className="p-8 bg-white border-b border-slate-200 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-slate-900">{selectedLead.full_name || selectedLead.phone}</h2>
                <div className="flex gap-2 mt-2">
                    {["new", "contacted", "qualified", "closed"].map(s => (
                        <button 
                            key={s}
                            onClick={() => setStatus(s)}
                            className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest transition-all ${
                                selectedLead.status === s ? "bg-violet-600 text-white" : "border border-slate-200 text-slate-400 hover:bg-slate-50"
                            }`}
                        >
                            {s}
                        </button>
                    ))}
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Sentiment</p>
                <p className="text-sm font-black text-emerald-500 uppercase">Positive</p>
              </div>
            </header>

            <div className="flex-1 overflow-y-auto p-10 space-y-6 bg-slate-50/50">
              {messagesLoading ? (
                <div className="text-center py-20 text-slate-400 text-sm font-medium">Loading history...</div>
              ) : messages.length === 0 ? (
                <div className="text-center py-20 text-slate-400 text-sm font-medium">No messages yet.</div>
              ) : (
                messages.map((m) => (
                  <div 
                    key={m.id} 
                    className={`flex ${m.direction === 'inbound' ? 'justify-start' : 'justify-end'}`}
                  >
                    <div className={`max-w-[70%] rounded-2xl p-4 text-sm font-medium shadow-sm ${
                      m.direction === 'inbound' 
                        ? 'bg-white text-slate-900 border border-slate-100' 
                        : 'bg-violet-600 text-white'
                    }`}>
                        {m.direction === 'outbound' && (
                            <span className="block text-[8px] font-black uppercase tracking-widest mb-1 opacity-60 italic">AI Agent</span>
                        )}
                        {m.content}
                    </div>
                  </div>
                ))
              )}
            </div>

            <footer className="p-8 bg-white border-t border-slate-200">
                <div className="flex gap-4">
                    <button className="flex-1 rounded-2xl bg-slate-900 py-4 text-xs font-bold uppercase tracking-widest text-white transition-all hover:scale-[1.02] active:scale-95">
                        ✨ Smart AI Reply Draft
                    </button>
                    <button className="rounded-2xl border border-slate-200 px-6 font-bold text-slate-400">
                        ...
                    </button>
                </div>
            </footer>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-300">
            <span className="text-6xl mb-4">💬</span>
            <p className="font-bold text-xl">Select a lead to analyze conversation</p>
          </div>
        )}
      </main>
    </div>
  );
}
