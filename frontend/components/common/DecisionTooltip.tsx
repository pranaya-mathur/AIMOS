"use client";

import React from "react";
import * as Tooltip from "@radix-ui/react-tooltip";
import { Info, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

type DecisionTooltipProps = {
  decision: string;
  rationale: string;
  confidence: number;
  agent: string;
  children: React.ReactNode;
};

export function DecisionTooltip({
  decision,
  rationale,
  confidence,
  agent,
  children,
}: DecisionTooltipProps) {
  return (
    <Tooltip.Provider delayDuration={200}>
      <Tooltip.Root>
        <Tooltip.Trigger asChild>
          <span className="cursor-help border-b border-dashed border-primary/40 hover:border-primary/80 transition-colors">
            {children}
          </span>
        </Tooltip.Trigger>
        <Tooltip.Portal>
          <Tooltip.Content
            className="z-[100] w-80 rounded-2xl glass-panel p-5 animate-in fade-in zoom-in duration-200"
            sideOffset={8}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className="h-6 w-6 rounded-md bg-primary/20 flex items-center justify-center border border-primary/30">
                <ShieldCheck className="h-3.5 w-3.5 text-primary" />
              </div>
              <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                AI Governance Report
              </span>
            </div>
            
            <div className="space-y-4">
              <div>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tight mb-1">Decision</p>
                <p className="text-sm font-bold text-white leading-tight">{decision}</p>
              </div>
              
              <div>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tight mb-1">Rationale</p>
                <p className="text-xs text-slate-300 leading-relaxed font-medium">
                  {rationale}
                </p>
              </div>
              
              <div className="flex items-center justify-between pt-2 border-t border-white/[0.04]">
                <div className="flex flex-col">
                   <p className="text-[9px] font-bold text-slate-500 uppercase">Agent</p>
                   <p className="text-[10px] font-bold text-primary">{agent}</p>
                </div>
                <div className="flex flex-col items-end">
                   <p className="text-[9px] font-bold text-slate-500 uppercase">Confidence</p>
                   <p className="text-[10px] font-bold text-emerald-400">{(confidence * 100).toFixed(0)}%</p>
                </div>
              </div>
            </div>
            
            <Tooltip.Arrow className="fill-white/[0.08]" />
          </Tooltip.Content>
        </Tooltip.Portal>
      </Tooltip.Root>
    </Tooltip.Provider>
  );
}
