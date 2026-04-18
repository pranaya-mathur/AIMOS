"use client";

import React from "react";
import { Area, AreaChart, ResponsiveContainer, YAxis } from "recharts";
import { cn } from "@/lib/utils";

type MetricChartCardProps = {
  title: string;
  value: string | number;
  change: string;
  trend: { value: number }[];
  changeTone?: "positive" | "negative" | "neutral";
  icon?: React.ReactNode;
  className?: string;
};

export function MetricChartCard({
  title,
  value,
  change,
  trend,
  changeTone = "positive",
  icon,
  className,
}: MetricChartCardProps) {
  const isPositive = changeTone === "positive";
  const color = isPositive ? "#10b981" : changeTone === "negative" ? "#f43f5e" : "#94a3b8";

  return (
    <div className={cn("glass-panel group relative flex flex-col justify-between overflow-hidden rounded-[2.5rem] p-8", className)}>
      <div className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-primary/10 blur-[80px] group-hover:bg-primary/20 transition-all duration-700" />
      
      <div className="flex justify-between items-start mb-6">
        <div>
          <p className="text-mono-premium mb-1">
            {title}
          </p>
          <h3 className="text-4xl font-black tracking-tighter text-white group-hover:text-primary transition-colors duration-500">
            {value}
          </h3>
        </div>
        {icon && (
          <div className="h-12 w-12 rounded-2xl bg-white/[0.04] border border-white/[0.1] flex items-center justify-center text-slate-400 group-hover:text-primary group-hover:scale-110 group-hover:rotate-6 transition-all duration-500">
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-end justify-between gap-4">
        <div className="flex flex-col gap-2">
          <div className={cn(
            "flex items-center gap-1.5 px-3 py-1 rounded-full border text-[10px] font-black uppercase tracking-widest",
            isPositive ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : 
            changeTone === "negative" ? "bg-rose-500/10 text-rose-400 border-rose-500/20" : 
            "bg-slate-500/10 text-slate-400 border-slate-500/20"
          )}>
            {isPositive ? "↑" : changeTone === "negative" ? "↓" : "→"} {change}
          </div>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider opacity-60">Trailing 30D</p>
        </div>
        
        <div className="h-16 w-32 -mb-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trend}>
              <defs>
                <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.4} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <YAxis hide domain={['auto', 'auto']} />
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={3}
                fillOpacity={1}
                fill={`url(#gradient-${title})`}
                isAnimationActive={true}
                animationDuration={1500}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
