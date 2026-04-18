"use client";

import { useQuery } from "@tanstack/react-query";
import { getGlobalAnalytics } from "@/lib/api/analytics";
import { MetricChartCard } from "@/components/dashboard/MetricChartCard";
import { BrandBrainWidget } from "@/components/dashboard/BrandBrainWidget";
import { DashboardPipeline } from "@/components/dashboard/DashboardPipeline";
import { Rocket, CreditCard, TrendingUp, Target, Activity, Share2, Brain, Zap, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["global-analytics"],
    queryFn: getGlobalAnalytics,
    refetchInterval: 30000,
  });

  if (isLoading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <div className="relative">
        <div className="absolute inset-0 bg-primary/20 blur-[60px] animate-pulse rounded-full" />
        <div className="h-20 w-20 rounded-[2rem] border-[3px] border-primary/30 border-t-primary animate-spin relative z-10" />
      </div>
      <p className="text-mono-premium animate-pulse mt-4">Initializing Control Tower...</p>
    </div>
  );

  const stats = data?.summary;
  const mockTrend = [{ value: 400 }, { value: 300 }, { value: 500 }, { value: 450 }, { value: 600 }, { value: 550 }, { value: 700 }];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] as const } }
  };

  return (
    <motion.div 
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="space-y-12 pb-24"
    >
      <motion.header variants={itemVariants} className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-5xl font-black text-white tracking-tighter uppercase italic">Command Tower</h1>
          <p className="text-slate-400 mt-2 font-medium italic">Synchronizing autonomous marketing agents across your ecosystem.</p>
        </div>
        <div className="flex items-center gap-3 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full shadow-[0_0_15px_rgba(16,185,129,0.1)]">
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
            <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Live Optimization Active</span>
        </div>
      </motion.header>
      
      <motion.div variants={itemVariants}>
        <BrandBrainWidget />
      </motion.div>

      {/* Main Stats Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <MetricChartCard
          title="Est. ROI"
          value={stats ? `${(stats.roi || 0).toLocaleString(undefined, {style: 'percent'})}` : "—"}
          change="+12%"
          trend={mockTrend}
          icon={<Rocket className="h-5 w-5" />}
        />
        <MetricChartCard
          title="Total Spend"
          value={stats ? `$${(stats.total_spend || 0).toLocaleString()}` : "—"}
          change="+8.4%"
          trend={[...mockTrend].reverse()}
          icon={<CreditCard className="h-5 w-5" />}
        />
        <MetricChartCard
          title="Est. Revenue"
          value={stats ? `$${(stats.estimated_revenue || 0).toLocaleString()}` : "—"}
          change="+0.5"
          trend={[...mockTrend].sort(() => Math.random() - 0.5)}
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <MetricChartCard
          title="Active Leads"
          value={stats ? stats.total_leads.toLocaleString() : "—"}
          change="+4.2%"
          trend={mockTrend.map(v => ({ value: v.value * 0.8 }))}
          icon={<Target className="h-5 w-5" />}
        />
      </motion.div>

      <div className="grid grid-cols-1 gap-12 lg:grid-cols-3">
        {/* Performance Trends Chart Placeholder */}
        <motion.section variants={itemVariants} className="lg:col-span-2 glass-panel rounded-[3rem] p-10 relative overflow-hidden group">
            <div className="absolute -top-24 -right-24 h-64 w-64 rounded-full bg-primary/5 blur-[100px] group-hover:bg-primary/10 transition-all duration-1000" />
            
            <div className="relative z-10">
                <h2 className="text-2xl font-black text-white uppercase italic tracking-tighter">Conversion Trends</h2>
                <p className="text-mono-premium mb-10">Daily Performance Synchrony</p>
                
                <div className="flex h-64 items-end justify-between gap-3 px-4">
                    {[40, 60, 45, 80, 55, 90, 70, 85, 95, 65, 50, 75, 80, 85].map((h, i) => (
                        <div key={i} className="flex-1 group/bar relative">
                            <motion.div 
                                initial={{ height: 0 }}
                                animate={{ height: `${h}%` }}
                                transition={{ duration: 1, delay: i * 0.05 }}
                                className="w-full bg-primary/20 rounded-t-xl group-hover/bar:bg-primary group-hover/bar:shadow-[0_0_20px_rgba(139,92,246,0.6)] transition-all" 
                            />
                            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover/bar:opacity-100 transition-opacity pointer-events-none">
                                <span className="text-[10px] font-black bg-white text-black px-2 py-1 rounded-sm shadow-2xl -mt-24 uppercase transform -rotate-90">+{h}%</span>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="mt-6 flex justify-between text-mono-premium">
                    <span>T-30 Days</span>
                    <span>Real-time</span>
                </div>
            </div>
            <div className="absolute bottom-0 right-10 opacity-5 pointer-events-none">
                <span className="text-[15rem] font-black leading-none uppercase italic italic-serif">AI</span>
            </div>
        </motion.section>

        {/* AI Recommendations */}
        <motion.section variants={itemVariants} className="glass-panel border-white/[0.12] rounded-[3rem] p-10 bg-primary/5 shadow-2xl">
            <h2 className="text-2xl font-black text-white uppercase italic tracking-tighter">AI Directives</h2>
            <p className="text-mono-premium mb-10">Optimization Engine Node</p>
            
            <div className="space-y-6">
                {[
                    { title: "Boost Google Spend", desc: "Meta CPL is 15% higher than Google this week; reallocating budget is advised.", type: "Budget" },
                    { title: "A/B Test Creative #4", desc: "Static image banners are outperforming video by 2.3x for 'Awareness' goal.", type: "Creative" },
                    { title: "High-Intent Hotspots", desc: "leads from 'Tier 1 Cities' shows 3x conversion score; target specifically.", type: "Audience" }
                ].map((r) => (
                    <div key={r.title} className="group relative rounded-[1.5rem] border border-white/[0.08] bg-white/[0.02] p-6 transition-all hover:bg-white/[0.05] hover:border-primary/40">
                        <span className="text-mono-premium !text-primary/70">{r.type} // Authorized</span>
                        <h3 className="mt-2 text-sm font-bold text-white uppercase tracking-tight">{r.title}</h3>
                        <p className="mt-2 text-[11px] text-slate-500 group-hover:text-slate-300 leading-relaxed">{r.desc}</p>
                    </div>
                ))}
            </div>
            
            <button className="mt-10 w-full rounded-2xl bg-primary text-white py-4 text-[11px] font-black uppercase tracking-widest shadow-[0_0_30px_rgba(139,92,246,0.3)] hover:scale-105 active:scale-95 transition-all">
                Execute All Nodes
            </button>
        </motion.section>
      </div>

      <motion.div variants={itemVariants}>
         <DashboardPipeline />
      </motion.div>
    </motion.div>
  );
}
