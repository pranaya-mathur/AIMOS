"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { MessageSquare, X, Send, Sparkles, ChevronRight, ChevronLeft } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function AICopilotSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hello! I'm your AIMOS Co-pilot. I can explain budget shifts, generate landing page previews, or help you optimize your ROAS. How can I assist you today?" }
  ]);
  const [input, setInput] = useState("");

  return (
    <>
      {/* Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "fixed right-0 top-1/2 -translate-y-1/2 z-[60] flex h-14 w-12 items-center justify-center rounded-l-3xl glass-panel group shadow-2xl transition-all duration-500",
          isOpen && "right-[400px]"
        )}
      >
        {isOpen ? <ChevronRight className="h-6 w-6 text-white" /> : <ChevronLeft className="h-6 w-6 text-white" />}
        <div className="absolute right-full mr-4 opacity-0 group-hover:opacity-100 transition-all bg-black/80 backdrop-blur-md text-primary text-[10px] font-black uppercase tracking-widest px-3 py-1.5 rounded-xl pointer-events-none border border-primary/20 whitespace-nowrap">
           AI Co-pilot active
        </div>
      </motion.button>

      {/* Sidebar Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.aside
            initial={{ x: 420, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 420, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 bottom-0 z-[55] w-[400px] border-l border-white/[0.08] glass-panel !bg-[rgba(15,15,30,0.85)] p-0 flex flex-col backdrop-blur-[40px]"
          >
            {/* Header */}
            <div className="p-8 border-b border-white/[0.08] flex items-center justify-between bg-white/[0.02]">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-2xl bg-primary/20 flex items-center justify-center border border-primary/30 shadow-[0_0_20px_rgba(139,92,246,0.2)]">
                  <Sparkles className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white tracking-tight uppercase tracking-[0.1em]">AI Co-pilot</h2>
                  <p className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest flex items-center gap-1.5 mt-0.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Autonomous Node Online
                  </p>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="h-8 w-8 flex items-center justify-center rounded-xl hover:bg-white/10 transition-colors">
                <X className="h-4 w-4 text-slate-400" />
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-hide">
              {messages.map((m, i) => (
                <div key={i} className={cn("flex flex-col gap-3", m.role === "user" ? "items-end" : "items-start")}>
                  <motion.div 
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    className={cn(
                      "max-w-[90%] p-5 rounded-[2rem] text-[13px] leading-relaxed shadow-xl",
                      m.role === "user" 
                        ? "bg-primary text-white font-medium" 
                        : "bg-white/[0.05] border border-white/[0.1] text-slate-200 backdrop-blur-md"
                    )}
                  >
                    {m.content}
                  </motion.div>
                  <span className="text-mono-premium px-2 opacity-50">
                    {m.role === "user" ? "Authorized User" : m.role === "assistant" ? "AIMOS Intelligence" : "System Node"}
                  </span>
                </div>
              ))}
            </div>

            {/* Input Area */}
            <div className="p-8 border-t border-white/[0.08] bg-black/20 backdrop-blur-xl">
              <div className="relative group">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Query autonomous systems..."
                  className="w-full bg-white/[0.03] border border-white/[0.1] rounded-[1.5rem] py-4 pl-5 pr-14 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-primary/50 focus:bg-white/[0.05] transition-all"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && input.trim()) {
                      setMessages([...messages, { role: "user", content: input }]);
                      setInput("");
                    }
                  }}
                />
                <button 
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 h-10 w-10 flex items-center justify-center rounded-2xl bg-primary text-white shadow-lg shadow-primary/20 hover:scale-105 active:scale-95 transition-all"
                  onClick={() => {
                   if (input.trim()) {
                      setMessages([...messages, { role: "user", content: input }]);
                      setInput("");
                    }
                  }}
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
              <div className="mt-6 flex items-center justify-center gap-4">
                 <div className="h-[1px] flex-1 bg-white/[0.04]" />
                 <p className="text-[9px] text-slate-600 font-black uppercase tracking-widest whitespace-nowrap">
                   Quantum Key Verified
                 </p>
                 <div className="h-[1px] flex-1 bg-white/[0.04]" />
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
