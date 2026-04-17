"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { upsertBrand, completeOnboarding, type BrandData } from "@/lib/api/brand";

const STEPS = [
  { id: "business_type", title: "Business Type", description: "How would you categorize your business?" },
  { id: "industry", title: "Industry", description: "Which sector do you operate in?" },
  { id: "primary_goal", title: "Primary Goal", description: "What do you want to achieve first?" },
  { id: "monthly_budget", title: "Monthly Budget", description: "What is your estimated marketing budget?" },
  { id: "platform_preference", title: "Platforms", description: "Where should we run your campaigns?" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<Partial<BrandData>>({
    business_type: "",
    industry: "",
    primary_goal: "",
    monthly_budget: 1000,
    platform_preference: [],
    name: "My Brand", // Default placeholder for onboarding
  });

  const next = async () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      setLoading(true);
      try {
        await upsertBrand(formData as BrandData);
        // Trigger Market Intelligence / Spy Agent immediately (M1 Intelligence)
        // We use the 'generate-kit' endpoint as it triggers the strategy chain
        fetch("/api/brand/generate-kit", { method: "POST" }).catch(console.error);
        
        await completeOnboarding();
        router.push("/");
      } catch (e) {
        alert("Failed to save. Please try again.");
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

  const step = STEPS[currentStep];

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-violet-100 via-slate-50 to-fuchsia-100 p-6">
      <div className="w-full max-w-2xl overflow-hidden rounded-[2.5rem] border border-white/40 bg-white/60 shadow-2xl backdrop-blur-xl">
        <div className="p-10">
          {/* Progress Bar */}
          <div className="mb-12 flex gap-2">
            {STEPS.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${
                  i <= currentStep ? "bg-violet-600" : "bg-slate-200"
                }`}
              />
            ))}
          </div>

          <div className="mb-10 text-center">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              {step.title}
            </h1>
            <p className="mt-2 text-slate-500">{step.description}</p>
          </div>

          <div className="min-h-[300px]">
            {currentStep === 0 && (
              <div className="grid grid-cols-2 gap-4">
                {["D2C", "Service", "Creator", "Local Business"].map((t) => (
                  <button
                    key={t}
                    onClick={() => update("business_type", t)}
                    className={`group relative overflow-hidden rounded-2xl border-2 p-6 transition-all hover:scale-[1.02] active:scale-[0.98] ${
                      formData.business_type === t
                        ? "border-violet-600 bg-violet-50"
                        : "border-slate-100 bg-white"
                    }`}
                  >
                    <span className="relative z-10 text-lg font-medium text-slate-800">
                      {t}
                    </span>
                    {formData.business_type === t && (
                        <div className="absolute inset-0 bg-violet-600/5 transition-opacity" />
                    )}
                  </button>
                ))}
              </div>
            )}

            {currentStep === 1 && (
              <div className="grid grid-cols-2 gap-4">
                {["Fashion", "Food", "Beauty", "SaaS", "Real Estate", "Other"].map((i) => (
                  <button
                    key={i}
                    onClick={() => update("industry", i)}
                    className={`rounded-2xl border-2 p-4 text-left transition-all hover:border-violet-300 ${
                      formData.industry === i
                        ? "border-violet-600 bg-violet-50"
                        : "border-slate-100 bg-white"
                    }`}
                  >
                    <span className="font-medium text-slate-800">{i}</span>
                  </button>
                ))}
              </div>
            )}

            {currentStep === 2 && (
              <div className="grid grid-cols-1 gap-4">
                {[
                  { id: "Sales", desc: "Drive purchases and direct revenue" },
                  { id: "Leads", desc: "Generate potential customer inquiries" },
                  { id: "Awareness", desc: "Build brand presence and reach" },
                ].map((g) => (
                  <button
                    key={g.id}
                    onClick={() => update("primary_goal", g.id)}
                    className={`flex items-center justify-between rounded-2xl border-2 p-6 text-left transition-all ${
                      formData.primary_goal === g.id
                        ? "border-violet-600 bg-violet-50"
                        : "border-slate-100 bg-white"
                    }`}
                  >
                    <div>
                      <h3 className="text-lg font-bold text-slate-800">{g.id}</h3>
                      <p className="text-sm text-slate-500">{g.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {currentStep === 3 && (
              <div className="space-y-8 py-10">
                <div className="flex flex-col items-center">
                  <span className="text-5xl font-black text-violet-600">
                    ${formData.monthly_budget?.toLocaleString()}
                  </span>
                  <span className="mt-2 text-sm font-medium uppercase tracking-widest text-slate-400">
                    Monthly Ad Spend
                  </span>
                </div>
                <input
                  type="range"
                  min="500"
                  max="50000"
                  step="500"
                  value={formData.monthly_budget}
                  onChange={(e) => update("monthly_budget", parseInt(e.target.value))}
                  className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-slate-200 accent-violet-600"
                />
                <div className="flex justify-between text-xs font-bold text-slate-400">
                  <span>$500</span>
                  <span>$50,000+</span>
                </div>
              </div>
            )}

            {currentStep === 4 && (
              <div className="grid grid-cols-1 gap-6">
                 {["Meta (FB & IG)", "Google Search", "Both"].map((p) => (
                  <button
                    key={p}
                    onClick={() => {
                        const val = p === "Both" ? ["meta", "google"] : [p.split(" ")[0].toLowerCase()];
                        update("platform_preference", val);
                    }}
                    className={`flex items-center gap-4 rounded-2xl border-2 p-6 text-left transition-all ${
                      formData.platform_preference?.join(", ") === (p === "Both" ? "meta, google" : p.split(" ")[0].toLowerCase())
                        ? "border-violet-600 bg-violet-50"
                        : "border-slate-100 bg-white shadow-sm"
                    }`}
                  >
                    <div className={`h-6 w-6 rounded-full border-2 ${
                        formData.platform_preference?.join(", ") === (p === "Both" ? "meta, google" : p.split(" ")[0].toLowerCase())
                        ? "border-violet-600 bg-violet-600 ring-4 ring-violet-100"
                        : "border-slate-200"
                    }`} />
                    <span className="text-lg font-semibold text-slate-800">{p}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="mt-12 flex justify-between">
            <button
              onClick={back}
              disabled={currentStep === 0}
              className={`text-sm font-bold uppercase tracking-widest transition-opacity ${
                currentStep === 0 ? "opacity-0" : "text-slate-400 hover:text-slate-600"
              }`}
            >
              Back
            </button>
            <button
              onClick={next}
              disabled={loading || !formData[STEPS[currentStep].id as keyof BrandData] && currentStep !== 3}
              className="flex items-center gap-2 rounded-full bg-violet-600 px-10 py-4 text-sm font-bold uppercase tracking-widest text-white shadow-[0_10px_30px_-10px_rgba(124,58,237,0.5)] transition-all hover:scale-105 hover:bg-violet-700 active:scale-95 disabled:opacity-50"
            >
              {loading ? "Saving..." : currentStep === STEPS.length - 1 ? "Finish" : "Next"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
