"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getLandingPages, generateLandingPage, deleteLandingPage, type LandingPage } from "@/lib/api/leads";

export default function LandingPagesIndex() {
  const [pages, setPages] = useState<LandingPage[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    load();
  }, []);

  const load = async () => {
    setLoading(true);
    try {
      const data = await getLandingPages();
      setPages(data);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await generateLandingPage();
      await load();
      // Optionally redirect to builder
    } catch (e) {
      alert("AI Generation failed. Ensure Brand Setup is complete.");
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure?")) return;
    await deleteLandingPage(id);
    await load();
  };

  if (loading) return <div className="p-20 text-center font-medium text-slate-400">Loading your capture ecosystem...</div>;

  return (
    <div className="p-10 max-w-7xl mx-auto">
      <header className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight">Capture Pages</h1>
          <p className="text-slate-500 mt-2 font-medium">AI-generated high-fidelity landing pages for your campaigns.</p>
        </div>
        <button 
          onClick={handleGenerate}
          disabled={generating}
          className="rounded-full bg-violet-600 px-8 py-4 text-sm font-bold uppercase tracking-widest text-white shadow-xl transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
        >
          {generating ? "Generating..." : "✨ AI Generate New Page"}
        </button>
      </header>

      {pages.length === 0 ? (
        <div className="rounded-[3rem] border-2 border-dashed border-slate-200 p-20 text-center">
            <h3 className="text-xl font-bold text-slate-400">No pages yet.</h3>
            <p className="text-slate-400 mt-2">Click the button above to let AI build your first conversion engine.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {pages.map(p => (
                <div key={p.id} className="group rounded-[2.5rem] border border-slate-100 bg-white p-8 shadow-sm transition-all hover:shadow-2xl hover:border-violet-100">
                    <div className="flex justify-between items-start mb-6">
                        <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${
                            p.is_published === 'true' ? "bg-emerald-100 text-emerald-600" : "bg-slate-100 text-slate-400"
                        }`}>
                            {p.is_published === 'true' ? 'Live' : 'Draft'}
                        </span>
                        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onClick={() => handleDelete(p.id)} className="text-slate-300 hover:text-red-500 text-sm">Delete</button>
                        </div>
                    </div>
                    
                    <h2 className="text-xl font-bold text-slate-900 mb-2 truncate">{p.title}</h2>
                    <p className="text-xs font-medium text-slate-400 mb-6">/p/{p.slug}</p>
                    
                    <div className="grid grid-cols-2 gap-4 mb-8">
                        <div className="rounded-2xl bg-slate-50 p-4">
                            <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 block mb-1">Views</span>
                            <span className="text-xl font-bold text-slate-900">{p.views_count}</span>
                        </div>
                        <div className="rounded-2xl bg-slate-50 p-4">
                            <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 block mb-1">Conv.</span>
                            <span className="text-xl font-bold text-emerald-600">{p.conversions_count}</span>
                        </div>
                    </div>

                    <Link 
                        href={`/leads/pages/${p.id}`}
                        className="block w-full rounded-2xl bg-slate-900 py-4 text-center text-xs font-bold uppercase tracking-widest text-white transition-all hover:bg-slate-800"
                    >
                        Edit & Preview
                    </Link>
                </div>
            ))}
        </div>
      )}
    </div>
  );
}
