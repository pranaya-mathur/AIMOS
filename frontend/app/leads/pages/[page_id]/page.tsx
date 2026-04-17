"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { getLandingPages, updateLandingPage, type LandingPage } from "@/lib/api/leads";

export default function LandingPageBuilder() {
  const router = useRouter();
  const params = useParams();
  const pageId = params.page_id as string;

  const [page, setPage] = useState<LandingPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getLandingPages().then((pages) => {
      const p = pages.find((x) => x.id === pageId);
      if (p) setPage(p);
      setLoading(false);
    });
  }, [pageId]);

  const save = async (publish = false) => {
    if (!page) return;
    setSaving(true);
    try {
      const data: Partial<LandingPage> = {
        title: page.title,
        slug: page.slug,
        content_json: page.content_json,
      };
      if (publish) data.is_published = "true";
      
      await updateLandingPage(page.id, data);
      if (publish) setPage({ ...page, is_published: "true" });
      alert(publish ? "Published successfully!" : "Saved draft.");
    } finally {
      setSaving(false);
    }
  };

  const updateSection = (index: number, content: any) => {
    if (!page) return;
    const newSections = [...page.content_json.sections];
    newSections[index].content = { ...newSections[index].content, ...content };
    setPage({ ...page, content_json: { ...page.content_json, sections: newSections } });
  };

  if (loading) return <div className="p-20 text-center font-medium text-slate-400">Loading builder...</div>;
  if (!page) return <div className="p-20 text-center font-bold text-red-500">Page not found.</div>;

  return (
    <div className="flex h-[calc(100vh-64px)] bg-slate-50">
      {/* Editor Sidebar */}
      <aside className="w-1/3 border-r border-slate-200 bg-white flex flex-col">
        <header className="p-8 border-b border-slate-100 flex items-center justify-between">
          <button onClick={() => router.back()} className="text-slate-400 hover:text-slate-900 font-bold text-xs uppercase tracking-widest">← Back</button>
          <div className="flex gap-2">
            <button 
                onClick={() => save(false)} 
                disabled={saving}
                className="px-4 py-2 rounded-xl border border-slate-200 text-[10px] font-black uppercase tracking-widest text-slate-500 hover:bg-slate-50 disabled:opacity-50"
            >
                {saving ? "..." : "Save Draft"}
            </button>
            <button 
                onClick={() => save(true)} 
                disabled={saving}
                className="px-4 py-2 rounded-xl bg-violet-600 text-[10px] font-black uppercase tracking-widest text-white shadow-lg hover:bg-violet-700 disabled:opacity-50"
            >
                {saving ? "..." : "Publish"}
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-8 space-y-10">
          <div>
            <label className="block text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2">Internal Title</label>
            <input 
                type="text" 
                value={page.title} 
                onChange={e => setPage({...page, title: e.target.value})}
                className="w-full rounded-2xl border border-slate-100 bg-slate-50 p-4 text-sm font-bold outline-none focus:ring-2 focus:ring-violet-600"
            />
          </div>

          <div>
            <label className="block text-[10px] font-black uppercase tracking-widest text-slate-400 mb-2">URL Slug</label>
            <div className="flex items-center gap-2">
                <span className="text-xs text-slate-300">/p/</span>
                <input 
                    type="text" 
                    value={page.slug} 
                    onChange={e => setPage({...page, slug: e.target.value})}
                    className="flex-1 rounded-xl border border-slate-50 bg-slate-50 p-2 text-xs font-medium outline-none"
                />
            </div>
          </div>

          <div className="pt-8 border-t border-slate-100">
            <h3 className="text-xs font-black uppercase tracking-widest text-slate-900 mb-6">Page Sections</h3>
            {page.content_json.sections.map((s: any, i: number) => (
                <div key={i} className="mb-8 p-6 rounded-3xl bg-slate-50 border border-slate-100">
                    <span className="text-[10px] font-black uppercase tracking-widest text-violet-600 block mb-4">{s.type} Section</span>
                    {s.type === 'hero' && (
                        <div className="space-y-4">
                            <input 
                                className="w-full bg-transparent font-bold text-slate-900 outline-none" 
                                value={s.content.headline} 
                                onChange={e => updateSection(i, {headline: e.target.value})} 
                            />
                            <textarea 
                                className="w-full bg-transparent text-xs text-slate-500 outline-none" 
                                rows={3}
                                value={s.content.subheadline} 
                                onChange={e => updateSection(i, {subheadline: e.target.value})} 
                            />
                        </div>
                    )}
                    {s.type === 'features' && (
                        <div className="space-y-2">
                            {s.content.items.map((item: string, j: number) => (
                                <input 
                                    key={j}
                                    className="w-full bg-transparent text-xs font-medium text-slate-600 outline-none" 
                                    value={item} 
                                    onChange={e => {
                                        const newItems = [...s.content.items];
                                        newItems[j] = e.target.value;
                                        updateSection(i, {items: newItems});
                                    }}
                                />
                            ))}
                        </div>
                    )}
                </div>
            ))}
          </div>
        </div>
      </aside>

      {/* Preview Area */}
      <main className="flex-1 bg-slate-100 p-12 overflow-hidden flex flex-col">
        <div className="flex-1 bg-white rounded-[3rem] shadow-2xl overflow-y-auto overflow-x-hidden border-[12px] border-slate-900 scrollbar-hide">
            {/* Mock Landing Page Render */}
            {page.content_json.sections.map((s: any, i: number) => (
                <div key={i}>
                    {s.type === 'hero' && (
                        <div className="p-20 text-center" style={{ backgroundColor: s.content.background_color + '10' }}>
                            <h1 className="text-5xl font-black text-slate-900 mb-6 leading-tight">{s.content.headline}</h1>
                            <p className="text-xl text-slate-500 mb-10 max-w-2xl mx-auto">{s.content.subheadline}</p>
                            <button className="rounded-full px-10 py-5 text-sm font-bold uppercase tracking-widest text-white shadow-xl" style={{ backgroundColor: s.content.background_color }}>
                                {s.content.cta_text}
                            </button>
                        </div>
                    )}
                    {s.type === 'features' && (
                        <div className="p-20 bg-white">
                            <h2 className="text-center text-xs font-black uppercase tracking-widest text-slate-400 mb-12">{s.content.title}</h2>
                            <div className="grid grid-cols-2 gap-10">
                                {s.content.items.map((item: string, j: number) => (
                                    <div key={j} className="flex gap-4 items-start">
                                        <div className="h-6 w-6 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">✅</div>
                                        <p className="font-bold text-slate-800">{item}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                    {s.type === 'form' && (
                        <div className="p-20 bg-slate-50">
                             <div className="max-w-md mx-auto rounded-[2rem] bg-white p-10 shadow-lg border border-slate-100">
                                <h3 className="text-xl font-bold text-center mb-8">{s.content.title}</h3>
                                <div className="space-y-4">
                                    {(s.content.fields || ["Name", "Email"]).map((f: string, j: number) => (
                                        <div key={j}>
                                            <label className="block text-[10px] font-black uppercase tracking-widest text-slate-300 mb-1">{f}</label>
                                            <div className="h-12 w-full rounded-xl bg-slate-50 border border-slate-100" />
                                        </div>
                                    ))}
                                    <button className="w-full rounded-xl bg-slate-900 py-4 text-xs font-bold uppercase tracking-widest text-white mt-4">Submit</button>
                                </div>
                             </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
      </main>
    </div>
  );
}
