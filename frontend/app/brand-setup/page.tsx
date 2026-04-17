"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getBrand, upsertBrand, generateLogo, generateBrandKit, type BrandData } from "@/lib/api/brand";

export default function BrandSetupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generatingLogo, setGeneratingLogo] = useState(false);
  const [generatingKit, setGeneratingKit] = useState(false);
  const [brandKit, setBrandKit] = useState<any>(null);

  const [formData, setFormData] = useState<BrandData>({
    name: "",
    category: "",
    description: "",
    website_url: "",
    social_links: { instagram: "", facebook: "", youtube: "" },
    target_audience: { age: "", gender: "", location: "", interests: "" },
    product_details: [],
    pricing_range: "mid",
  });

  useEffect(() => {
    getBrand()
      .then((data) => {
        if (data.name) {
            setFormData((prev) => ({ ...prev, ...data }));
            if (data.ai_generated_kit) setBrandKit(data.ai_generated_kit);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await upsertBrand(formData);
      router.push("/");
    } catch (e) {
      alert("Failed to save brand details.");
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateLogo = async () => {
    setGeneratingLogo(true);
    try {
      const res = await generateLogo();
      setFormData(prev => ({ ...prev, logo_url: res.logo_url }));
    } catch (e) {
      alert("AI logo generation failed.");
    } finally {
      setGeneratingLogo(false);
    }
  };

  const handleGenerateKit = async () => {
    setGeneratingKit(true);
    try {
      const res = await generateBrandKit();
      setBrandKit(res.brand_kit);
      // Auto-populate description if empty
      if (!formData.description && res.brand_kit.brand_narrative) {
        setFormData(prev => ({ ...prev, description: res.brand_kit.brand_narrative }));
      }
    } catch (e) {
      alert("AI brand kit generation failed.");
    } finally {
      setGeneratingKit(false);
    }
  };

  if (loading) return <div className="p-10 text-center text-slate-500 font-medium">Loading brand profile...</div>;

  return (
    <div className="mx-auto max-w-5xl p-8 space-y-12 pb-32">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900">Brand Identity</h1>
          <p className="text-slate-500 mt-2 text-lg">Define how AI represents your business across all campaigns.</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleGenerateKit}
            disabled={generatingKit || !formData.name}
            className={`rounded-full px-6 py-3 font-bold text-white shadow-lg transition-all ${
              generatingKit ? "bg-slate-400" : "bg-gradient-to-r from-fuchsia-600 to-violet-600 hover:scale-105 active:scale-95"
            }`}
          >
            {generatingKit ? "Developing..." : "✨ AI Brand Kit"}
          </button>
          <button
            onClick={save}
            disabled={saving}
            className="rounded-full bg-slate-900 px-8 py-3 font-bold text-white shadow-md transition-transform hover:scale-105 active:scale-95 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Profile"}
          </button>
        </div>
      </header>

      {brandKit && (
        <section className="rounded-[2.5rem] bg-gradient-to-br from-violet-600 to-fuchsia-700 p-8 text-white shadow-2xl">
          <h2 className="mb-6 flex items-center gap-2 text-2xl font-black">
            <span className="text-3xl">✨</span> AI Brand Strategy Handoff
          </h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="space-y-4 rounded-3xl bg-white/10 p-6 backdrop-blur-md">
              <h3 className="text-xs font-black uppercase tracking-widest text-white/60">Brand Narrative</h3>
              <p className="text-lg font-medium leading-relaxed">{brandKit.brand_narrative}</p>
            </div>
            <div className="space-y-4 rounded-3xl bg-white/10 p-6 backdrop-blur-md">
              <h3 className="text-xs font-black uppercase tracking-widest text-white/60">Voice & Tone</h3>
              <p className="text-lg font-medium">{brandKit.brand_voice}</p>
              <div className="flex flex-wrap gap-2 pt-2">
                {brandKit.tone_guidelines?.slice(0, 3).map((t: string) => (
                  <span key={t} className="rounded-full bg-white/20 px-3 py-1 text-xs font-bold">{t}</span>
                ))}
              </div>
            </div>
            <div className="space-y-4 rounded-3xl bg-white/10 p-6 backdrop-blur-md">
              <h3 className="text-xs font-black uppercase tracking-widest text-white/60">Color Palette</h3>
              <div className="flex gap-3">
                {brandKit.color_palette?.map((c: string) => (
                  <div key={c} className="flex flex-col items-center gap-2">
                    <div className="h-12 w-12 rounded-2xl shadow-inner" style={{ backgroundColor: c.includes("#") ? c : "#fff" }} />
                    <span className="text-[10px] font-mono font-bold opacity-60">{c}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-4 rounded-3xl bg-white/10 p-6 backdrop-blur-md">
              <h3 className="text-xs font-black uppercase tracking-widest text-white/60">Primary Value Prop</h3>
              <p className="text-xl font-bold italic">"{brandKit.value_proposition_primary}"</p>
            </div>
          </div>
        </section>
      )}

      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        {/* Logo Section */}
        <section className="space-y-6 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-800">1. Visual Identity</h2>
            <button 
                onClick={handleGenerateLogo}
                disabled={generatingLogo || !formData.name}
                className="text-xs font-bold uppercase tracking-widest text-violet-600 hover:text-violet-700 disabled:opacity-50"
            >
                {generatingLogo ? "Generating..." : "✨ AI Logo"}
            </button>
          </div>
          <div className="flex flex-col items-center gap-6 py-4">
             <div className="relative h-48 w-48 overflow-hidden rounded-[2.5rem] border-4 border-slate-50 bg-slate-100 shadow-inner group">
                {formData.logo_url ? (
                    <img src={formData.logo_url} alt="Brand Logo" className="h-full w-full object-cover" />
                ) : (
                    <div className="flex h-full w-full items-center justify-center text-slate-300">
                        <span className="text-3xl font-black">?</span>
                    </div>
                )}
                {generatingLogo && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/10 backdrop-blur-sm">
                        <div className="h-8 w-8 animate-spin rounded-full border-4 border-violet-600 border-t-transparent" />
                    </div>
                )}
             </div>
             <div className="w-full">
                <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1 leading-none">Logo URL / Base64</label>
                <input
                    type="text"
                    value={formData.logo_url || ""}
                    onChange={(e) => setFormData({ ...formData, logo_url: e.target.value })}
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 text-xs font-mono outline-none focus:ring-2 focus:ring-violet-500"
                    placeholder="URL or generated data..."
                />
             </div>
          </div>
        </section>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Business Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                placeholder="e.g. Acme Fashion"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Category</label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                placeholder="e.g. Luxury Apparel"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                placeholder="Describe your brand values, tone, and mission..."
              />
            </div>
          </div>
        </section>

        {/* Links */}
        <section className="space-y-6 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-xl font-bold text-slate-800">2. Website & Socials</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Website / Shopify Link</label>
              <input
                type="url"
                value={formData.website_url}
                onChange={(e) => setFormData({ ...formData, website_url: e.target.value })}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                placeholder="https://yourstore.com"
              />
            </div>
            {["instagram", "facebook", "youtube"].map((platform) => (
              <div key={platform}>
                <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1 capitalize">{platform} Handle</label>
                <input
                  type="text"
                  value={formData.social_links?.[platform] || ""}
                  onChange={(e) => setFormData({
                    ...formData,
                    social_links: { ...formData.social_links, [platform]: e.target.value }
                  })}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                  placeholder={`@yourbrand`}
                />
              </div>
            ))}
          </div>
        </section>

        {/* Target Audience */}
        <section className="space-y-6 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm md:col-span-2">
          <h2 className="text-xl font-bold text-slate-800">3. Target Audience (AI Targeting)</h2>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Age Range</label>
              <input
                type="text"
                value={formData.target_audience?.age || ""}
                onChange={(e) => setFormData({
                  ...formData,
                  target_audience: { ...formData.target_audience, age: e.target.value }
                })}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                placeholder="e.g. 25-45"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Gender</label>
              <input
                type="text"
                value={formData.target_audience?.gender || ""}
                onChange={(e) => setFormData({
                  ...formData,
                  target_audience: { ...formData.target_audience, gender: e.target.value }
                })}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                placeholder="e.g. Female-skewed"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Location</label>
              <input
                type="text"
                value={formData.target_audience?.location || ""}
                onChange={(e) => setFormData({
                  ...formData,
                  target_audience: { ...formData.target_audience, location: e.target.value }
                })}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                placeholder="e.g. USA, Tier 1 cities"
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Core Interests</label>
              <input
                type="text"
                value={formData.target_audience?.interests || ""}
                onChange={(e) => setFormData({
                  ...formData,
                  target_audience: { ...formData.target_audience, interests: e.target.value }
                })}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 outline-none focus:ring-2 focus:ring-violet-500"
                placeholder="e.g. Sustainable living, Travel"
              />
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section className="space-y-6 rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm">
          <h2 className="text-xl font-bold text-slate-800">4. Pricing Tier</h2>
          <div className="flex gap-2 p-1 bg-slate-100 rounded-2xl">
            {["budget", "mid", "premium"].map((tier) => (
              <button
                key={tier}
                onClick={() => setFormData({ ...formData, pricing_range: tier })}
                className={`flex-1 rounded-xl py-4 text-sm font-bold uppercase tracking-widest transition-all ${
                  formData.pricing_range === tier
                    ? "bg-white text-violet-600 shadow-sm"
                    : "text-slate-400 hover:text-slate-600"
                }`}
              >
                {tier}
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
