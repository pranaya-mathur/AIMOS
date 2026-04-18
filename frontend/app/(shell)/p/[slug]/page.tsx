import { getLandingPageBySlug } from "@/lib/api/landing-pages";
import { LandingPageRenderer } from "@/components/landing/LandingPageRenderer";
import { notFound } from "next/navigation";

type Props = {
  params: { slug: string };
};

export default async function PublicLandingPage({ params }: Props) {
  const { slug } = params;

  try {
    const page = await getLandingPageBySlug(slug);
    
    if (!page) {
        return notFound();
    }

    const sections = page.content_json?.sections || [];

    return <LandingPageRenderer sections={sections} slug={slug} />;
  } catch (err) {
    console.error("Failed to load landing page:", err);
    return notFound();
  }
}
