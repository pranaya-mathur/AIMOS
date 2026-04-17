"use client";

import { useState } from "react";
import { ChatbotWidget } from "./ChatbotWidget";

type Section = {
  type: string;
  content: {
    headline?: string;
    subheadline?: string;
    cta_text?: string;
    bullet_points?: string[];
    form_title?: string;
    background_color?: string;
  };
};

type Props = {
  sections: Section[];
  slug: string;
};

export function LandingPageRenderer({ sections, slug }: Props) {
  const [formData, setFormData] = useState({ full_name: "", email: "", phone: "" });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`/api/landing-pages/${slug}/convert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (res.ok) setSubmitted(true);
    } catch (err) {
      console.error("Conversion failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white font-sans text-slate-900 overflow-x-hidden">
      {sections.map((section, idx) => {
        switch (section.type) {
          case "hero":
            return (
              <header key={idx} className="relative py-24 px-6 text-center border-b border-slate-100 overflow-hidden">
                 <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-violet-400 via-transparent to-transparent" />
                <div className="relative z-10 max-w-4xl mx-auto">
                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter mb-6 bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">
                    {section.content.headline}
                    </h1>
                    <p className="text-xl text-slate-500 mb-10 max-w-2xl mx-auto leading-relaxed font-medium">
                    {section.content.subheadline}
                    </p>
                    <a href="#form" className="inline-block px-10 py-5 bg-violet-600 text-white rounded-full font-bold uppercase tracking-widest text-sm shadow-2xl hover:bg-violet-700 transition-all hover:scale-105 active:scale-95">
                    {section.content.cta_text || "Get Started →"}
                    </a>
                </div>
              </header>
            );
          case "features":
            return (
              <section key={idx} className="py-20 px-6 bg-slate-50">
                <div className="max-w-5xl mx-auto">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {(section.content.bullet_points || []).map((point, i) => (
                        <div key={i} className="p-8 bg-white border border-slate-200 rounded-3xl shadow-sm hover:shadow-xl transition-all">
                            <div className="w-12 h-12 bg-violet-100 text-violet-600 rounded-2xl flex items-center justify-center mb-6">
                                <span className="font-black">0{i+1}</span>
                            </div>
                            <p className="font-bold text-lg text-slate-800 leading-tight">{point}</p>
                        </div>
                    ))}
                    </div>
                </div>
              </section>
            );
          case "form":
            return (
              <section key={idx} id="form" className="py-24 px-6 text-center max-w-2xl mx-auto">
                <div className="p-12 bg-white rounded-[3rem] border border-slate-200 shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-2 bg-violet-600" />
                    <h2 className="text-3xl font-black mb-4">{section.content.form_title || "Claim Your Offer"}</h2>
                    
                    {submitted ? (
                        <div className="py-10 text-emerald-600 animate-bounce">
                            <svg className="w-16 h-16 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg>
                            <p className="text-xl font-bold">Thank You! We'll be in touch.</p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-4 text-left">
                        <div>
                            <label className="block text-[10px] font-black uppercase text-slate-400 mb-1 ml-4">Full Name</label>
                            <input 
                                required
                                value={formData.full_name}
                                onChange={e => setFormData({...formData, full_name: e.target.value})}
                                className="w-full px-6 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-violet-500 outline-none transition-all font-medium" 
                                placeholder="Jane Doe" 
                            />
                        </div>
                        <div>
                            <label className="block text-[10px] font-black uppercase text-slate-400 mb-1 ml-4">Phone Number</label>
                            <input 
                                required
                                type="tel"
                                value={formData.phone}
                                onChange={e => setFormData({...formData, phone: e.target.value})}
                                className="w-full px-6 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-violet-500 outline-none transition-all font-medium" 
                                placeholder="+1 (555) 000-0000" 
                            />
                        </div>
                        <button 
                            disabled={loading}
                            className="w-full py-5 bg-slate-900 text-white rounded-2xl font-black uppercase tracking-widest text-sm hover:bg-slate-800 transition-all shadow-lg active:scale-95 disabled:bg-slate-300"
                        >
                            {loading ? "Processing..." : section.content.cta_text || "Submit →"}
                        </button>
                    </form>
                    )}
                </div>
              </section>
            );
          default:
            return null;
        }
      })}
      
      <footer className="py-10 border-t border-slate-100 text-center text-[10px] font-bold uppercase tracking-widest text-slate-400">
          Powered by AIMOS Autonomous Growth Engine
      </footer>

      {/* Conversion Engine: AI Chatbot */}
      <ChatbotWidget slug={slug} />
    </div>
  );
}
