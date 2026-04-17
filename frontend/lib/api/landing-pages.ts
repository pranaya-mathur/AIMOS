export type LandingPageData = {
  id: string;
  slug: string;
  title: string;
  description?: string;
  content_json: any;
  is_published: string;
  views_count: number;
  conversions_count: number;
};

export async function listLandingPages(): Promise<LandingPageData[]> {
  const res = await fetch("/api/landing-pages");
  if (!res.ok) throw new Error("Failed to list landing pages");
  return res.json();
}

export async function getLandingPageBySlug(slug: string): Promise<LandingPageData | null> {
  // Public endpoint or internal fetch
  // In a real app, this would be a public endpoint /api/p/{slug}
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/landing-pages/public/${slug}`);
  if (!res.ok) return null;
  return res.json();
}

export async function generateLandingPage(): Promise<{ id: string; slug: string }> {
  const res = await fetch("/api/landing-pages/generate", { method: "POST" });
  if (!res.ok) throw new Error("Failed to generate landing page");
  return res.json();
}
