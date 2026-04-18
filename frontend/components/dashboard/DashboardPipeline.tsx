"use client";

import { useQuery } from "@tanstack/react-query";
import { Pipeline } from "@/components/pipeline/Pipeline";
import {
  getCampaign,
  listCampaigns,
  type CampaignSummary,
} from "@/lib/api/campaign";
import { mapAgentStepsFromCampaign } from "@/lib/pipeline/map-agent-steps";
import { DecisionTooltip } from "@/components/common/DecisionTooltip";
import { ShieldCheck, Info, Rocket } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

function pickFocusCampaign(
  rows: CampaignSummary[],
): CampaignSummary | null {
  if (!rows.length) return null;
  const processing = rows.find((r) => r.status === "processing");
  if (processing) return processing;
  return rows[0];
}

export function DashboardPipeline() {
  const { data: list = [] } = useQuery({
    queryKey: ["campaigns"],
    queryFn: () => listCampaigns(15),
    refetchInterval: 10000,
  });

  const focus = pickFocusCampaign(list);

  const { data: detail } = useQuery({
    queryKey: ["campaign", focus?.id],
    queryFn: () => getCampaign(focus!.id),
    enabled: !!focus,
    refetchInterval: focus?.status === "processing" ? 3000 : false,
  });

  const { steps, headline } = mapAgentStepsFromCampaign(detail ?? null);

  return (
    <section className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-10 w-10 rounded-2xl bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-2xl font-black tracking-tighter text-white uppercase italic">
              Orchestration Pipeline
            </h2>
            <p className="text-mono-premium opacity-50">Real-time Agent Synchronization</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
           <div className="flex items-center gap-3 px-4 py-2 bg-white/[0.03] border border-white/[0.08] rounded-2xl">
              <div className="h-2 w-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(139,92,246,0.5)]" />
              <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Governance Node: Encrypted</span>
           </div>
        </div>
      </div>
      
      <div className="glass-panel rounded-[3rem] p-10 relative overflow-hidden group">
        <div className="absolute -top-24 -right-24 h-64 w-64 rounded-full bg-primary/5 blur-[100px] group-hover:bg-primary/10 transition-all duration-1000" />
        
        <div className="mb-10 flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-3xl font-black text-white tracking-tighter uppercase italic">{headline}</p>
            {focus && (
              <div className="flex items-center gap-2 mt-2">
                 <div className="h-px w-6 bg-slate-700" />
                 <p className="text-mono-premium">ID: {focus.id.slice(0, 12)} // {focus.name ?? "unnamed_node"}</p>
              </div>
            )}
          </div>
          
          {focus && (
            <div className="flex items-center gap-3">
              <span className={cn(
                "inline-flex items-center gap-2 rounded-2xl border px-5 py-2 text-[10px] font-black uppercase tracking-[0.2em] transition-all duration-500 shadow-xl",
                focus.status === "processing" 
                  ? "bg-primary/20 text-white border-primary/30 shadow-primary/10" 
                  : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 shadow-emerald-500/5"
              )}>
                {focus.status === "processing" && (
                   <span className="relative flex h-2 w-2">
                     <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                     <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
                   </span>
                )}
                {focus.status}
              </span>
            </div>
          )}
        </div>
        
        <div className="relative">
          <div className="absolute inset-0 bg-primary/5 blur-3xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-1000" />
          <Pipeline steps={steps.map(s => ({
            ...s,
            title: (
              <DecisionTooltip
                agent={s.title as string}
                decision="Optimization directive issued"
                rationale="Performance metrics indicate 24% under-utilization in Meta Top-of-Funnel. Budget shifted to Content Studio variations."
                confidence={0.94}
              >
                <span className="group-hover:text-primary transition-colors cursor-help">{s.title}</span>
              </DecisionTooltip>
            )
          }))} />
        </div>
        
        {!focus && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-10 flex flex-col items-center justify-center rounded-[2.5rem] border border-dashed border-white/[0.08] bg-white/[0.01] p-16 text-center"
          >
            <div className="relative mb-6">
               <div className="absolute inset-0 bg-primary/10 blur-2xl rounded-full animate-pulse" />
               <Rocket className="h-16 w-16 text-slate-800 relative z-10" />
            </div>
            <p className="text-xs font-black text-slate-500 uppercase tracking-[0.3em]">Ignition Sequence Bypassed</p>
            <p className="mt-4 text-[10px] text-slate-600 max-w-xs font-bold leading-relaxed uppercase tracking-tighter">
              Awaiting deployment instructions for the 15-agent orchestration engine.
            </p>
          </motion.div>
        )}
      </div>
    </section>
  );
}

