"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getBrand } from "@/lib/api/brand";

const STEPS = [
  { id: "info", title: "General Info", description: "Name and core focus of the campaign." },
  { id: "target", title: "Targeting", description: "Where and why should we show your ads?" },
  { id: "budget", title: "Economics", description: "Define your investment and timeline." },
  { id: "preview", title: "Review & Launch", description: "Verify everything looks perfect." },
];

export default function NewCampaignPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "", // Will be set on load
    objective: "leads",
    platform: "both",
    total_budget: 1000,
    schedule_start: new Date().toISOString().split("T")[0],
    schedule_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
    input: {
      brief: "",
    }
  });

  useEffect(() => {
    getBrand().then((brand) => {
        if (brand.name) {
            setFormData(prev => ({
                ...prev,
                name: `${brand.name} Launch - ${new Date().toLocaleDateString()}`,
                objective: brand.marketing_goal?.toLowerCase() || "leads",
                platform: (brand.platform_preference?.length || 0) > 1 ? "both" : (brand.platform_preference?.[0] || "both"),
                total_budget: brand.monthly_budget || 2500,
                input: {
                    brief: `Driving ${brand.marketing_goal || "growth"} for our ${brand.industry || "business"} in the ${brand.category || "market"} sector. Focus on ${brand.target_audience?.interests || "target keywords"}.`
                }
            }));
        }
    });
  }, []);

  const update = (key: string, value: any) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
  };

  const next = async () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setLoading(true);
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/campaign/create`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify(formData),
        });
        if (!res.ok) throw new Error("Launch failed");
        router.push("/dashboard");
      } catch (e) {
        alert("Failed to launch campaign.");
      } finally {
        setLoading(false);
      }
    }
  };

  const back = () => {
    if (currentStep > 0) setCurrentStep(currentStep - 1);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-4xl overflow-hidden rounded-[3rem] border border-slate-200 bg-white shadow-2xl">
        <div className="flex h-[600px] flex-col md:flex-row">
          {/* Stepper Sidebar */}
          <aside className="w-full border-r border-slate-100 bg-slate-50/50 p-10 md:w-80">
            <h2 className="text-xl font-black text-slate-900 mb-10">Campaign Builder</h2>
            <div className="space-y-8">
              {STEPS.map((s, i) => (
                <div key={s.id} className="flex gap-4">
                  <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-all ${
                    i <= currentStep ? "bg-violet-600 text-white shadow-lg" : "bg-slate-200 text-slate-500"
                  }`}>
                    {i + 1}
                  </div>
                  <div className={i <= currentStep ? "text-slate-900" : "text-slate-400"}>
                    <p className="text-sm font-bold uppercase tracking-widest leading-none mb-1">{s.title}</p>
                    <p className="text-xs">{i === currentStep ? s.description : ""}</p>
                  </div>
                </div>
              ))}
            </div>
          </aside>

          {/* Form Content */}
          <main className="flex flex-1 flex-col p-12">
            <div className="flex-1">
              {currentStep === 0 && (
                <div className="space-y-6">
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Campaign Name</label>
                    <input
                      type="text"
                      className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-900 outline-none focus:ring-2 focus:ring-violet-600"
                      value={formData.name}
                      onChange={(e) => update("name", e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Primary Brief</label>
                    <textarea
                      rows={5}
                      className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-900 outline-none focus:ring-2 focus:ring-violet-600"
                      value={formData.input.brief}
                      onChange={(e) => update("input", { ...formData.input, brief: e.target.value })}
                    />
                  </div>
                </div>
              )}

              {currentStep === 1 && (
                <div className="space-y-10">
                  <div className="grid grid-cols-2 gap-4">
                     {["Sales", "Leads", "Awareness"].map(o => (
                        <button 
                            key={o}
                            onClick={() => update("objective", o.toLowerCase())}
                            className={`rounded-2xl border-2 p-6 text-left transition-all ${
                                formData.objective === o.toLowerCase() ? "border-violet-600 bg-violet-50" : "border-slate-100 hover:border-violet-200"
                            }`}
                        >
                            <span className="block text-sm font-bold">{o}</span>
                        </button>
                     ))}
                  </div>
                  <div className="flex gap-4">
                     {["Meta", "Google", "Both"].map(p => (
                        <button 
                            key={p}
                            onClick={() => update("platform", p.toLowerCase())}
                            className={`flex-1 rounded-2xl border-2 p-4 text-center transition-all ${
                                formData.platform === p.toLowerCase() ? "border-violet-600 bg-violet-50 text-violet-600" : "border-slate-100 text-slate-400"
                            }`}
                        >
                            <span className="text-xs font-black uppercase tracking-widest">{p}</span>
                        </button>
                     ))}
                  </div>
                </div>
              )}

              {currentStep === 2 && (
                <div className="space-y-8">
                  <div className="rounded-3xl bg-violet-600 p-8 text-white shadow-xl">
                    <span className="text-xs font-bold uppercase tracking-widest opacity-60">Total Ad Budget</span>
                    <div className="mt-2 text-5xl font-black">${formData.total_budget.toLocaleString()}</div>
                    <input
                        type="range"
                        min="500"
                        max="50000"
                        step="500"
                        value={formData.total_budget}
                        onChange={(e) => update("total_budget", parseInt(e.target.value))}
                        className="mt-6 w-full accent-white"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">Start Date</label>
                        <input type="date" value={formData.schedule_start} onChange={(e) => update("schedule_start", e.target.value)} className="w-full rounded-xl border border-slate-100 p-3 text-sm" />
                    </div>
                    <div>
                        <label className="block text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">End Date</label>
                        <input type="date" value={formData.schedule_end} onChange={(e) => update("schedule_end", e.target.value)} className="w-full rounded-xl border border-slate-100 p-3 text-sm" />
                    </div>
                  </div>
                </div>
              )}

              {currentStep === 3 && (
                <div className="space-y-6">
                    <div className="rounded-[2rem] border-2 border-dashed border-slate-200 p-10 text-center">
                        <h3 className="text-lg font-bold text-slate-800">Ready to Deploy</h3>
                        <p className="text-slate-400 mt-2">AI agents will now start building creatives and strategy based on these parameters.</p>
                        <div className="mt-6 grid grid-cols-2 gap-4 text-left">
                            <div className="rounded-2xl bg-slate-50 p-4">
                                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Target</span>
                                <p className="font-bold capitalize">{formData.platform}</p>
                            </div>
                            <div className="rounded-2xl bg-slate-50 p-4">
                                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Objective</span>
                                <p className="font-bold capitalize">{formData.objective}</p>
                            </div>
                        </div>
                    </div>
                </div>
              )}
            </div>

            <div className="mt-10 flex justify-between">
              <button
                onClick={back}
                disabled={currentStep === 0}
                className={`text-sm font-bold uppercase tracking-widest transition-opacity ${
                  currentStep === 0 ? "opacity-0" : "text-slate-400 hover:text-slate-900"
                }`}
              >
                Back
              </button>
              <button
                onClick={next}
                disabled={loading}
                className="rounded-full bg-violet-600 px-10 py-4 text-sm font-bold uppercase tracking-widest text-white shadow-xl transition-all hover:scale-105 hover:bg-violet-700 active:scale-95 disabled:opacity-50"
              >
                {loading ? "Launching..." : currentStep === STEPS.length - 1 ? "Start Campaign" : "Next Step"}
              </button>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
