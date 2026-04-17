"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getSettings } from "@/lib/settings";

export default function PublicLandingPage() {
  const params = useParams();
  const slug = params.slug as string;

  const [page, setPage] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState<Record<string, string>>({});

  useEffect(() => {
    const settings = getSettings();
    fetch(`${settings.apiBaseUrl}/p/${slug}`)
      .then(res => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then(data => setPage(data))
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [slug]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    const settings = getSettings();
    try {
      const res = await fetch(`${settings.apiBaseUrl}/p/${slug}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      if (res.ok) setSubmitted(true);
      else alert("Submission failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="h-screen flex items-center justify-center font-medium text-slate-400">Loading experience...</div>;
  if (error) return <div className="h-screen flex items-center justify-center font-bold text-slate-900 border-t-4 border-violet-600">404 | Page not found.</div>;

  return (
    <div className="min-h-screen bg-white">
      {page.content.sections.map((s: any, i: number) => (
        <div key={i}>
          {s.type === 'hero' && (
            <section className="py-24 px-6 md:px-20 text-center" style={{ backgroundColor: s.content.background_color + '05' }}>
              <div className="max-w-4xl mx-auto">
                <h1 className="text-4xl md:text-7xl font-black text-slate-900 mb-8 leading-[1.1] tracking-tight">{s.content.headline}</h1>
                <p className="text-lg md:text-2xl text-slate-500 mb-12 max-w-2xl mx-auto leading-relaxed">{s.content.subheadline}</p>
                <button 
                  onClick={() => document.getElementById('conversion-form')?.scrollIntoView({ behavior: 'smooth' })}
                  className="rounded-full px-12 py-6 text-sm font-black uppercase tracking-[0.2em] text-white shadow-2xl transition-all hover:scale-105 active:scale-95" 
                  style={{ backgroundColor: s.content.background_color }}
                >
                  {s.content.cta_text}
                </button>
              </div>
            </section>
          )}

          {s.type === 'features' && (
            <section className="py-24 px-6 md:px-20 max-w-6xl mx-auto">
              <h2 className="text-center text-[10px] font-black uppercase tracking-[0.3em] text-slate-300 mb-16">{s.content.title}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-20 gap-y-12">
                {s.content.items.map((item: string, j: number) => (
                  <div key={j} className="flex gap-6 items-start">
                    <div className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center shrink-0 text-emerald-600 font-bold">✓</div>
                    <p className="text-xl font-bold text-slate-800 leading-snug">{item}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {s.type === 'form' && (
            <section id="conversion-form" className="py-24 px-6 bg-slate-50 border-y border-slate-100">
              <div className="max-w-xl mx-auto">
                {submitted ? (
                  <div className="rounded-[3rem] bg-emerald-500 p-16 text-center text-white shadow-2xl animate-in fade-in zoom-in duration-500">
                    <span className="text-6xl block mb-6">✨</span>
                    <h3 className="text-3xl font-black mb-4">Request Received</h3>
                    <p className="font-bold opacity-80">Our AI agent will reach out to you within minutes via WhatsApp/Email.</p>
                  </div>
                ) : (
                  <div className="rounded-[3rem] bg-white p-12 md:p-16 shadow-2xl border border-slate-100">
                    <h3 className="text-3xl font-black text-slate-900 mb-10 text-center tracking-tight">{s.content.title}</h3>
                    <form onSubmit={handleSubmit} className="space-y-6">
                      {(s.content.fields || ["Full Name", "Email", "Phone"]).map((f: string, j: number) => (
                        <div key={j}>
                          <label className="block text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 mb-2 ml-1">{f}</label>
                          <input 
                            required 
                            type={f.toLowerCase().includes('email') ? 'email' : 'text'}
                            placeholder={`Enter your ${f.toLowerCase()}...`}
                            onChange={e => setFormData({...formData, [f]: e.target.value})}
                            className="w-full rounded-2xl border border-slate-100 bg-slate-50/50 p-5 text-slate-900 outline-none transition-all focus:ring-4 focus:ring-violet-100 focus:bg-white focus:border-violet-300" 
                          />
                        </div>
                      ))}
                      <button 
                        type="submit"
                        disabled={submitting}
                        className="w-full rounded-2xl bg-slate-900 py-6 text-sm font-black uppercase tracking-[0.2em] text-white shadow-xl transition-all hover:bg-slate-800 active:scale-[0.98] disabled:opacity-50 mt-4"
                      >
                        {submitting ? "Processing..." : "Continue →"}
                      </button>
                    </form>
                    <p className="text-center text-[10px] text-slate-300 font-bold uppercase tracking-widest mt-10">Secured by AIMOS Lead Engine</p>
                  </div>
                )}
              </div>
            </section>
          )}
        </div>
      ))}
      
      <footer className="py-12 border-t border-slate-50 text-center">
        <p className="text-[10px] font-black uppercase tracking-[0.5em] text-slate-200">Built with AIMOS AI</p>
      </footer>
    </div>
  );
}
