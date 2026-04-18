"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { Plus, Layout, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

type EmptyStateProps = {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
};

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  icon,
}: EmptyStateProps) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center p-12 text-center glass-panel rounded-[3rem] border-dashed border-white/[0.1] bg-white/[0.01]"
    >
      <div className="relative mb-6">
        <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full" />
        <div className="relative h-20 w-20 rounded-[2rem] bg-black/40 border border-white/[0.08] flex items-center justify-center text-slate-600">
          {icon || <Layout className="h-10 w-10 opacity-20" />}
        </div>
        <div className="absolute -bottom-2 -right-2 h-8 w-8 rounded-xl bg-primary flex items-center justify-center text-white shadow-lg">
          <Sparkles className="h-4 w-4" />
        </div>
      </div>
      
      <h3 className="text-xl font-bold text-white tracking-tight mb-2">
        {title}
      </h3>
      <p className="text-sm text-slate-500 max-w-xs mx-auto mb-8 font-medium">
        {description}
      </p>
      
      {actionLabel && (
        <button
          onClick={onAction}
          className="flex items-center gap-2 rounded-2xl bg-white/[0.04] border border-white/[0.08] px-6 py-3 text-xs font-black uppercase tracking-widest text-white hover:bg-white/[0.08] hover:scale-105 active:scale-95 transition-all"
        >
          <Plus className="h-4 w-4 text-primary" />
          {actionLabel}
        </button>
      )}
    </motion.div>
  );
}
