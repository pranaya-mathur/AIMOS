import { BannerStudio } from "@/components/creatives/BannerStudio";
import { Sparkles } from "lucide-react";
import Link from "next/link";

export const metadata = {
  title: "Banner Studio | AIMOS",
  description: "Generate high-fidelity ad banners using local sovereign AI engine.",
};

export default function BannerStudioPage() {
  return (
    <div className="space-y-12 pb-24 max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-8 pt-8">
        <div className="space-y-4">
          <nav className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">
             <Link href="/creatives" className="hover:text-primary transition-colors">Creative Studio</Link>
             <span>/</span>
             <span className="text-white">Banner Engine</span>
          </nav>
          
          <div className="flex items-center gap-3">
            <div className="px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-[10px] font-black uppercase tracking-widest text-primary shadow-[0_0_15px_rgba(139,92,246,0.1)]">
              Modular Extension v1.2
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-black uppercase tracking-widest text-emerald-400">
               <Sparkles className="h-3.5 w-3.5" />
               Sovereign Node
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-black text-white tracking-tighter uppercase italic leading-none">
            Banner <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-violet-400">Studio</span>
          </h1>
          <p className="text-slate-400 font-medium max-w-2xl text-lg leading-relaxed pt-2">
            Generate production-ready horizontal ad banners. Optimized for 16:9 cinema layouts with localized physically grounded lighting.
          </p>
        </div>
      </header>

      <BannerStudio />
    </div>
  );
}
