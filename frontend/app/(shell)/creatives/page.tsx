"use client";

import { useEffect, useState } from "react";
import { listCreatives, updateCreative, approveCreative, type AdCreative } from "@/lib/api/creatives";
import { getMediaAssets, type MediaAsset } from "@/lib/api/media";
import { SplitScreenPreview } from "@/components/landing/SplitScreenPreview";
import { ChatbotPreview } from "@/components/landing/ChatbotPreview";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Palette, MessageSquare, Sparkles } from "lucide-react";

export default function CreativeStudioPage() {
  const [creatives, setCreatives] = useState<AdCreative[]>([]);
  const [assets, setAssets] = useState<MediaAsset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([listCreatives(), getMediaAssets()])
      .then(([cData, aData]) => {
        setCreatives(cData);
        setAssets(aData);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] gap-8">
      <div className="relative">
        <div className="absolute inset-0 bg-primary/20 blur-[60px] animate-pulse rounded-full" />
        <div className="h-20 w-20 rounded-[2rem] border-[3px] border-primary/30 border-t-primary animate-spin relative z-10" />
        <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-8 w-8 text-primary animate-pulse" />
      </div>
      <div className="text-center">
        <p className="text-mono-premium animate-pulse mb-2">
          Quantum Creative Engine
        </p>
        <h2 className="text-2xl font-black text-white tracking-widest uppercase italic">Initializing Node...</h2>
      </div>
    </div>
  );

  return (
    <div className="space-y-12 pb-24">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-8">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <div className="px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-[10px] font-black uppercase tracking-widest text-primary shadow-[0_0_15px_rgba(139,92,246,0.1)]">
              Protocol v2.6.4
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-black uppercase tracking-widest text-emerald-400">
               <Sparkles className="h-3.5 w-3.5" />
               Autonomous Mode
            </div>
          </div>
          <h1 className="text-6xl font-black text-white tracking-tighter uppercase italic">Creative Studio</h1>
          <p className="text-slate-400 mt-4 font-medium max-w-2xl text-lg leading-relaxed">
            Architecting conversion-optimized assets through multi-agent generative orchestration.
          </p>
        </div>
      </header>

      <Tabs defaultValue="landing-page" className="w-full">
        <div className="flex items-center justify-between mb-8 border-b border-white/[0.08] pb-4">
          <TabsList className="bg-white/[0.03] border border-white/[0.06] p-1 rounded-2xl">
            <TabsTrigger value="landing-page" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-primary data-[state=active]:text-white transition-all gap-2">
              <Palette className="h-4 w-4" />
              Landing Pages
            </TabsTrigger>
            <TabsTrigger value="chatbot" className="rounded-xl px-6 py-2.5 data-[state=active]:bg-primary data-[state=active]:text-white transition-all gap-2">
              <MessageSquare className="h-4 w-4" />
              Interactive Chatbots
            </TabsTrigger>
          </TabsList>
          
          <div className="hidden md:flex items-center gap-4 text-[11px] font-bold text-slate-500">
             <span>Live Preview Sync: <span className="text-emerald-400">Active</span></span>
             <div className="h-4 w-[1px] bg-white/[0.1]" />
             <span>Agent Availability: <span className="text-primary">100%</span></span>
          </div>
        </div>

        <TabsContent value="landing-page" className="animate-in fade-in slide-in-from-bottom-4 duration-500 outline-none">
          <SplitScreenPreview />
        </TabsContent>
        
        <TabsContent value="chatbot" className="animate-in fade-in slide-in-from-bottom-4 duration-500 outline-none">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center py-12">
            <div className="space-y-8">
              <div className="glass-panel p-8 rounded-[2rem] border-white/[0.08]">
                <h3 className="text-2xl font-bold text-white mb-4">Chatbot Architect</h3>
                <p className="text-slate-400 leading-relaxed mb-6">
                  Configure your autonomous agent's personality, knowledge base, and conversion goals. AIMOS handles the training and deployment.
                </p>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">Knowledge Source</label>
                    <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] text-sm text-slate-300">
                      Syncing from: <span className="text-primary">brand-corpus-v2.pdf</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">Primary Goal</label>
                    <div className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.08] text-sm text-slate-300">
                      Direct Conversion / Lead Capture
                    </div>
                  </div>
                </div>
              </div>
              <button className="w-full py-4 rounded-[2rem] bg-primary text-white font-black uppercase tracking-widest hover:shadow-[0_0_32px_rgba(139,92,246,0.4)] transition-all">
                Publish Changes
              </button>
            </div>
            
            <ChatbotPreview />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

