"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { Monitor, Smartphone, Tablet, Edit3, Eye, Send, Sparkles } from "lucide-react";

export function SplitScreenPreview() {
  const [prompt, setPrompt] = useState("Create a high-converting landing page for a luxury skincare brand using minimalist aesthetics.");
  const [viewMode, setViewMode] = useState<"desktop" | "tablet" | "mobile">("desktop");
  const [isPreview, setIsPreview] = useState(true);

  const [isGenerating, setIsGenerating] = useState(false);

  const startGeneration = () => {
    setIsGenerating(true);
    setTimeout(() => setIsGenerating(false), 2500);
  };

  return (
    <div className="flex h-[800px] w-full gap-6 overflow-hidden">
      {/* Editor Side (Left) */}
      <div className="flex flex-col w-[35%] glass-panel rounded-[3rem] p-10 border-white/[0.08]">
        <div className="flex items-center gap-4 mb-10">
          <div className="h-12 w-12 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30 shadow-[0_0_20px_rgba(139,92,246,0.1)]">
            <Edit3 className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h2 className="text-xl font-black text-white tracking-tighter uppercase italic">Designer</h2>
            <p className="text-mono-premium opacity-50">Generative Canvas v2.6</p>
          </div>
        </div>

        <div className="space-y-8 flex-1">
          <div className="space-y-3">
            <label className="text-mono-premium px-1">Synthesis Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full h-40 bg-white/[0.03] border border-white/[0.1] rounded-[1.5rem] p-6 text-sm text-white placeholder:text-slate-700 focus:outline-none focus:border-primary/50 transition-all resize-none shadow-inner"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <button 
              onClick={startGeneration}
              disabled={isGenerating}
              className="flex flex-col items-center justify-center p-5 rounded-[1.5rem] bg-white/[0.03] border border-white/[0.08] hover:bg-white/[0.06] hover:border-white/[0.2] transition-all group disabled:opacity-50"
            >
              <Sparkles className={cn("h-6 w-6 text-primary mb-2 group-hover:scale-110 transition-transform", isGenerating && "animate-spin")} />
              <span className="text-mono-premium">Synthesize</span>
            </button>
            <button className="flex flex-col items-center justify-center p-5 rounded-[1.5rem] bg-primary/10 border border-primary/20 hover:bg-primary/20 transition-all group shadow-lg shadow-primary/5">
              <Send className="h-6 w-6 text-primary mb-2 group-hover:scale-110 transition-transform" />
              <span className="text-mono-premium !text-primary">Deploy</span>
            </button>
          </div>

          <div className="pt-8 border-t border-white/[0.06] space-y-6">
            <div className="flex items-center justify-between">
               <span className="text-mono-premium">Variations Library</span>
               <span className="px-3 py-1 rounded-full bg-white/[0.04] text-[9px] font-black text-slate-500 uppercase tracking-widest border border-white/[0.04]">4 Active</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
               {[1,2,3,4].map(i => (
                 <motion.div 
                   key={i} 
                   whileHover={{ scale: 1.02 }}
                   whileTap={{ scale: 0.98 }}
                   className={cn(
                    "aspect-video rounded-2xl bg-white/[0.02] border border-white/[0.08] cursor-pointer hover:border-primary/40 transition-all flex items-center justify-center text-[11px] font-black uppercase text-slate-600 tracking-tighter shadow-sm",
                    i === 1 && "border-primary/60 bg-primary/10 text-primary shadow-[0_0_20px_rgba(139,92,246,0.1)]"
                  )}
                 >
                   v.{i}
                 </motion.div>
               ))}
            </div>
          </div>
        </div>
      </div>

      {/* Preview Side (Right) */}
      <div className="flex-1 flex flex-col glass-panel rounded-[3rem] border-white/[0.08] overflow-hidden group">
        {/* Preview Toolbar */}
        <div className="px-10 py-6 border-b border-white/[0.08] flex items-center justify-between bg-black/40 backdrop-blur-xl">
          <div className="flex items-center gap-3">
            {[ 
              { id: "desktop", icon: Monitor },
              { id: "tablet", icon: Tablet },
              { id: "mobile", icon: Smartphone }
            ].map((mode) => (
              <button 
                key={mode.id}
                onClick={() => setViewMode(mode.id as any)}
                className={cn(
                  "p-3 rounded-xl transition-all border", 
                  viewMode === mode.id 
                    ? "bg-primary/20 text-primary border-primary/40 shadow-[0_0_15px_rgba(139,92,246,0.15)]" 
                    : "text-slate-600 border-transparent hover:text-slate-300 hover:bg-white/5"
                )}
              >
                <mode.icon className="h-5 w-5" />
              </button>
            ))}
          </div>

          <div className="flex items-center gap-4 bg-white/[0.04] rounded-full px-6 py-2 border border-white/[0.08] shadow-inner">
             <div className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
             </div>
             <span className="text-mono-premium !text-white !opacity-100">Live Render Pipeline</span>
          </div>
        </div>

        {/* Iframe-like Preview Container */}
        <div className="flex-1 bg-[#0a0a0f] p-10 overflow-hidden flex justify-center relative">
          {/* Animated Noise Background */}
          <div className="absolute inset-0 opacity-10 mix-blend-overlay pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')]" />
          
          <motion.div 
            animate={{ 
              width: viewMode === "desktop" ? "100%" : viewMode === "tablet" ? "768px" : "375px",
            }}
            transition={{ type: "spring", damping: 25, stiffness: 120 }}
            className="h-full bg-white rounded-t-[2.5rem] shadow-[0_40px_100px_-20px_rgba(0,0,0,1)] overflow-y-auto scrollbar-hide border-[12px] border-[#050505] relative"
          >
            {/* AI Scanning Overlay */}
            <AnimatePresence>
              {isGenerating && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute inset-0 z-50 bg-primary/10 backdrop-blur-[2px] pointer-events-none"
                >
                   <motion.div 
                     initial={{ top: "-10%" }}
                     animate={{ top: "110%" }}
                     transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                     className="absolute left-0 right-0 h-[2px] bg-primary shadow-[0_0_20px_#8b5cf6,0_0_40px_#8b5cf6]"
                   />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Mock Page Content */}
            <div className="p-0">
               <nav className="p-8 flex justify-between items-center bg-white border-b border-slate-100">
                  <div className="h-8 w-32 bg-slate-900 rounded-lg" />
                  <div className="flex gap-6">
                     <div className="h-2.5 w-16 bg-slate-200 rounded-full" />
                     <div className="h-2.5 w-16 bg-slate-200 rounded-full" />
                  </div>
               </nav>
               <div className="p-16 text-center space-y-8">
                  <motion.h1 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-5xl font-serif text-slate-900 leading-[1.1] tracking-tight"
                  >
                    Radiance & Renewal
                  </motion.h1>
                  <p className="text-slate-500 max-w-lg mx-auto text-base leading-relaxed">
                    Experience the future of clinical skincare with our ultra-potent biometric formulations.
                  </p>
                  <div className="h-16 w-64 bg-slate-900 rounded-full mx-auto" />
               </div>
               <div className="aspect-video bg-slate-50 border-y border-slate-100 flex items-center justify-center">
                  <div className="h-48 w-48 rounded-full border-8 border-slate-100 bg-white shadow-2xl animate-pulse" />
               </div>
               <div className="p-16 grid grid-cols-2 gap-12">
                  <div className="space-y-4">
                     <div className="h-6 w-6 bg-slate-200 rounded-md" />
                     <div className="h-2.5 w-full bg-slate-100 rounded-full" />
                     <div className="h-2.5 w-2/3 bg-slate-100 rounded-full" />
                  </div>
                  <div className="space-y-4">
                     <div className="h-6 w-6 bg-slate-200 rounded-md" />
                     <div className="h-2.5 w-full bg-slate-100 rounded-full" />
                     <div className="h-2.5 w-2/3 bg-slate-100 rounded-full" />
                  </div>
               </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
