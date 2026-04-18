"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Target, 
  Rocket, 
  Brain, 
  Zap, 
  ShieldCheck, 
  ChevronRight, 
  DollarSign, 
  Globe, 
  ArrowRight,
  Sparkles,
  BarChart4,
  Users
} from "lucide-react";
import { upsertBrand, completeOnboarding, type BrandData } from "@/lib/api/brand";
import { OnboardingShell } from "@/components/onboarding/OnboardingShell";
import { NeuralStepper } from "@/components/onboarding/NeuralStepper";
import { cn } from "@/lib/utils";

const STEPS = [
  { id: "objective", title: "Primary Objective", description: "What is your primary market directive?" },
  { id: "identity", title: "Brand DNA", description: "Identify the core essence of your business." },
  { id: "mapping", title: "Resource Allocation", description: "Define your operational budget parameters." },
  { id: "syndication", title: "Global Syndication", description: "Where should the AI synchronize your presence?" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Partial<BrandData>>({
    name: "",
    category: "",
    description: "",
    business_type: "",
    industry: "",
    marketing_goal: "",
    monthly_budget: 1000,
    platform_preference: [],
  });

  const next = async () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setLoading(true);
      try {
        await upsertBrand(formData as BrandData);
        // Trigger background synthesis
        fetch("/api/brand/generate-kit", { method: "POST" }).catch(console.error);
        await completeOnboarding();
        router.push("/");
      } catch (e) {
        alert("System Sync Failed. Please retry.");
      } finally {
        setLoading(false);
      }
    }
  };

  const back = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  const update = (key: keyof BrandData, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <OnboardingShell>
      <div className="flex flex-col h-full">
        {/* Futuristic Stepper */}
        <NeuralStepper steps={STEPS} currentStep={currentStep} />

        {/* Content Area */}
        <div className="flex-1 relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20, filter: "blur(10px)" }}
              animate={{ opacity: 1, x: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, x: -20, filter: "blur(10px)" }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="space-y-12"
            >
              <div className="text-center md:text-left">
                <motion.h2 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-5xl font-black text-white uppercase italic tracking-tighter"
                >
                  {STEPS[currentStep].title}
                </motion.h2>
                <div className="flex items-center gap-3 mt-4 justify-center md:justify-start">
                   <div className="h-[1px] w-8 bg-primary/40" />
                   <p className="text-slate-400 font-medium italic">{STEPS[currentStep].description}</p>
                </div>
              </div>

              {/* Step Renderers */}
              <div className="min-h-[400px]">
                {currentStep === 0 && <StepObjective value={formData.marketing_goal} onChange={(v) => update("marketing_goal", v)} />}
                {currentStep === 1 && <StepIdentity data={formData} update={update} />}
                {currentStep === 2 && <StepMapping value={formData.monthly_budget} onChange={(v) => update("monthly_budget", v)} />}
                {currentStep === 3 && <StepSyndication value={formData.platform_preference || []} onChange={(v) => update("platform_preference", v)} />}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Navigation Actions */}
        <div className="mt-20 flex items-center justify-between border-t border-white/5 pt-12">
           <button
             onClick={back}
             disabled={currentStep === 0}
             className={cn(
               "text-mono-premium hover:text-white transition-all disabled:opacity-0",
               currentStep === 0 ? "pointer-events-none" : "cursor-pointer"
             )}
           >
             // REVOKE_PREVIOUS_STEP
           </button>
           
           <button
             onClick={next}
             disabled={loading || (
               currentStep === 0 ? !formData.marketing_goal :
               currentStep === 1 ? !formData.name :
               currentStep === 2 ? false : // Budget always has a default
               currentStep === 3 ? (formData.platform_preference?.length === 0) :
               false
             )}
             className="group relative flex items-center gap-4 bg-white text-black px-12 py-5 rounded-2xl font-black uppercase italic tracking-tighter transition-all hover:scale-105 active:scale-95 disabled:opacity-20"
           >
             {loading ? "Synchronizing..." : currentStep === STEPS.length - 1 ? "Commence Ignite" : "Proceed to Next Node"}
             <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
           </button>
        </div>
      </div>
    </OnboardingShell>
  );
}

function StepObjective({ value, onChange }: { value: any; onChange: (v: string) => void }) {
  const objectives = [
    { id: "Sales", label: "Revenue Dominance", desc: "Aggressive conversion optimization for direct sales.", icon: Target },
    { id: "Leads", label: "Lead Synthesis", desc: "Capture and qualify high-intent growth signals.", icon: Users },
    { id: "Awareness", label: "Market Resonance", desc: "Maximize brand visibility and cultural footprint.", icon: BarChart4 },
  ];

  return (
    <div className="grid grid-cols-1 gap-6">
      {objectives.map((obj) => (
        <button
          key={obj.id}
          onClick={() => onChange(obj.id)}
          className={cn(
            "group relative flex items-center justify-between p-8 rounded-[2rem] border transition-all text-left",
            value === obj.id 
              ? "bg-primary/10 border-primary shadow-[0_0_30px_rgba(139,92,246,0.1)]" 
              : "bg-white/[0.02] border-white/5 hover:border-white/20"
          )}
        >
          <div className="flex items-center gap-6">
            <div className={cn(
                "h-14 w-14 rounded-2xl flex items-center justify-center transition-all",
                value === obj.id ? "bg-primary text-white" : "bg-white/5 text-slate-500 group-hover:text-white"
            )}>
              <obj.icon className="h-7 w-7" />
            </div>
            <div>
              <h3 className="text-xl font-black text-white uppercase italic">{obj.label}</h3>
              <p className="text-sm text-slate-500 mt-1 max-w-sm">{obj.desc}</p>
            </div>
          </div>
          {value === obj.id && (
              <motion.div layoutId="check" className="h-6 w-6 rounded-full bg-primary flex items-center justify-center">
                  <ChevronRight className="h-4 w-4 text-white" />
              </motion.div>
          )}
        </button>
      ))}
    </div>
  );
}

function StepIdentity({ data, update }: { data: any; update: any }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
      <div className="space-y-6">
        <label className="text-mono-premium block">System Identifier (Business Name)</label>
        <input
          type="text"
          value={data.name || ""}
          onChange={(e) => update("name", e.target.value)}
          className="w-full bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-white text-xl font-bold italic outline-none focus:ring-2 focus:ring-primary/50 transition-all"
          placeholder="ENTER_BRAND_NAME"
        />
      </div>
      <div className="space-y-6">
        <label className="text-mono-premium block">Category / Market Segment</label>
        <input
          type="text"
          value={data.category || ""}
          onChange={(e) => update("category", e.target.value)}
          className="w-full bg-white/[0.03] border border-white/10 rounded-2xl p-6 text-white text-xl font-bold italic outline-none focus:ring-2 focus:ring-primary/50 transition-all"
          placeholder="e.g. LUXURY_FASHION"
        />
      </div>
      <div className="md:col-span-2 space-y-6">
        <label className="text-mono-premium block">Market Intent (Short Description)</label>
        <textarea
          value={data.description || ""}
          onChange={(e) => update("description", e.target.value)}
          rows={3}
          className="w-full bg-white/[0.03] border border-white/10 rounded-3xl p-6 text-white text-lg font-medium outline-none focus:ring-2 focus:ring-primary/50 transition-all resize-none"
          placeholder="Describe your market disruption strategy..."
        />
      </div>
    </div>
  );
}

function StepMapping({ value, onChange }: { value: any; onChange: (v: number) => void }) {
  return (
    <div className="flex flex-col items-center justify-center space-y-16 py-10">
      <div className="relative">
         <motion.div
           key={value}
           initial={{ opacity: 0, scale: 0.8 }}
           animate={{ opacity: 1, scale: 1 }}
           className="text-7xl md:text-9xl font-black text-white italic tracking-tighter"
         >
           ${value?.toLocaleString()}
         </motion.div>
         <div className="absolute -top-10 -right-10">
            <Sparkles className="h-10 w-10 text-primary animate-pulse" />
         </div>
      </div>
      
      <div className="w-full max-w-2xl space-y-6">
        <input
          type="range"
          min="1000"
          max="100000"
          step="1000"
          value={value}
          onChange={(e) => onChange(parseInt(e.target.value))}
          className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-white/5 accent-primary hover:accent-primary/80 transition-all"
        />
        <div className="flex justify-between text-mono-premium opacity-40">
           <span>$1,000 // BASE</span>
           <span>$100,000+ // SUPREME</span>
        </div>
      </div>

      <div className="flex items-center gap-6 p-6 rounded-3xl bg-primary/5 border border-primary/10">
         <Zap className="h-5 w-5 text-primary" />
         <p className="text-sm text-slate-400">
           Projected <span className="text-white font-bold">2.4x - 3.8x ROAS</span> based on current node allocation.
         </p>
      </div>
    </div>
  );
}

function StepSyndication({ value, onChange }: { value: string[]; onChange: (v: string[]) => void }) {
  const platforms = [
    { id: "meta", label: "Meta Neural (FB & IG)", icon: Users },
    { id: "google", label: "Google Nexus (Search)", icon: Globe },
    { id: "tiktok", label: "ByteStream (TikTok)", icon: Sparkles },
  ];

  const toggle = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      onChange([...value, id]);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      {platforms.map((p) => (
        <button
          key={p.id}
          onClick={() => toggle(p.id)}
          className={cn(
            "group flex items-center gap-6 p-8 rounded-[2rem] border transition-all text-left",
            value.includes(p.id)
              ? "bg-primary/10 border-primary shadow-[0_0_30px_rgba(139,92,246,0.1)]"
              : "bg-white/[0.02] border-white/5 hover:border-white/20"
          )}
        >
          <div className={cn(
            "h-16 w-16 rounded-2xl flex items-center justify-center transition-all",
            value.includes(p.id) ? "bg-primary text-white" : "bg-white/5 text-slate-500 group-hover:text-white"
          )}>
            <p.icon className="h-8 w-8" />
          </div>
          <div>
            <h3 className="text-xl font-black text-white uppercase italic">{p.label}</h3>
            <p className="text-xs text-slate-500 mt-1 uppercase tracking-widest font-bold">Protocol Active</p>
          </div>
        </button>
      ))}
    </div>
  );
}
