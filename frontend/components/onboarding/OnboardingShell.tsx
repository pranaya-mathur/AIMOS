"use client";

import React from "react";
import { motion } from "framer-motion";
import { AmbientOrbs } from "../common/AmbientOrbs";
import { Sparkles } from "lucide-react";

export function OnboardingShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#020205] px-6 py-12">
      {/* Immersive Background */}
      <AmbientOrbs />
      
      {/* Top Status Header */}
      <div className="absolute top-8 left-0 right-0 z-50 px-12 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-2 w-2 rounded-full bg-primary animate-pulse shadow-[0_0_10px_rgba(139,92,246,0.6)]" />
          <span className="text-mono-premium text-primary opacity-80">Neural Link Established</span>
        </div>
        <div className="flex items-center gap-2 text-white/40">
           <Sparkles className="h-4 w-4" />
           <span className="text-[10px] font-black uppercase tracking-[0.3em]">Quantum Protocol V2.6</span>
        </div>
      </div>

      {/* Main Canvas */}
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 w-full max-w-4xl glass-panel rounded-[4rem] p-1 pb-1 shadow-[0_64px_256px_-64px_rgba(139,92,246,0.2)] overflow-hidden"
      >
        <div className="relative h-full w-full bg-[#05050a]/80 backdrop-blur-3xl rounded-[3.9rem] p-12 md:p-20">
             {/* Subtle internal glow */}
             <div className="absolute -top-40 -left-40 h-[400px] w-[400px] bg-primary/5 rounded-full blur-[100px] pointer-events-none" />
             <div className="absolute -bottom-40 -right-40 h-[400px] w-[400px] bg-fuchsia-500/5 rounded-full blur-[100px] pointer-events-none" />
             
             {children}
        </div>
      </motion.div>

      {/* Bottom Footer Info */}
      <div className="absolute bottom-8 left-0 right-0 z-50 text-center">
         <p className="text-mono-premium opacity-30">Confidential Node Synthesis // Authorized Personnel Only</p>
      </div>
    </div>
  );
}
