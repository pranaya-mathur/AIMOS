"use client";

import React, { useState } from "react";
import { cn } from "@/lib/utils";
import { MessageCircle, X, Send, User, Bot, HelpCircle, ArrowRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function ChatbotPreview() {
  const [messages, setMessages] = useState([
    { role: "bot", content: "Hi there! I'm the AIMOS Assistant. How can I help you discover the perfect skincare routine today?" }
  ]);
  const [input, setInput] = useState("");

  const suggestions = [
    "What's your best seller?",
    "Do you have a loyalty program?",
    "How do I track my order?"
  ];

  return (
    <div className="w-full max-w-md mx-auto aspect-[3/4] glass-panel rounded-[2.5rem] border-white/[0.08] overflow-hidden flex flex-col shadow-2xl">
      {/* Header */}
      <div className="p-6 bg-primary flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-white/20 flex items-center justify-center border border-white/20 backdrop-blur-sm">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight">Store Assistant</h3>
            <p className="text-[10px] text-white/60 font-black uppercase tracking-widest">Powered by AIMOS</p>
          </div>
        </div>
        <button className="text-white/80 hover:text-white">
          <HelpCircle className="h-5 w-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50/10">
        {messages.map((m, i) => (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            key={i}
            className={cn("flex flex-col gap-1.5", m.role === "user" ? "items-end" : "items-start")}
          >
            <div className={cn(
              "px-4 py-3 rounded-2xl text-[13px] leading-relaxed",
              m.role === "user" 
                ? "bg-primary text-white" 
                : "bg-white text-slate-900 shadow-sm border border-slate-100"
            )}>
              {m.content}
            </div>
            <span className="text-[9px] font-black uppercase tracking-widest text-slate-500 px-1">
              {m.role === "user" ? "You" : "Assistant"}
            </span>
          </motion.div>
        ))}
      </div>

      {/* Suggested Actions */}
      <div className="px-6 py-4 flex gap-2 overflow-x-auto scrollbar-hide bg-white/5">
        {suggestions.map((s, i) => (
          <button 
            key={i}
            onClick={() => {
              setMessages([...messages, { role: "user", content: s }]);
            }}
            className="shrink-0 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 text-[10px] font-bold text-slate-300 hover:bg-primary/20 hover:border-primary/40 transition-all"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-6 border-t border-white/[0.08] bg-white/[0.02]">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
             className="w-full bg-slate-900/40 border border-white/[0.1] rounded-2xl py-3.5 pl-4 pr-12 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-primary/50 transition-all"
             onKeyDown={(e) => {
               if (e.key === "Enter" && input.trim()) {
                 setMessages([...messages, { role: "user", content: input }]);
                 setInput("");
               }
             }}
          />
          <button 
            className="absolute right-2 top-1/2 -translate-y-1/2 h-9 w-9 flex items-center justify-center rounded-xl bg-primary text-white hover:scale-105 transition-all"
            onClick={() => {
              if (input.trim()) {
                 setMessages([...messages, { role: "user", content: input }]);
                 setInput("");
               }
            }}
          >
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
