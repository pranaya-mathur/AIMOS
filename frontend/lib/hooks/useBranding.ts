import { useEffect, useState } from "react";
import { getOrgConfig, type WhitelabelConfig } from "@/lib/api/org";

export function useBranding() {
  const [config, setConfig] = useState<WhitelabelConfig | null>(null);

  useEffect(() => {
    getOrgConfig()
      .then((data) => {
        setConfig(data);
        if (data.primary_color) {
          document.documentElement.style.setProperty("--primary-brand", data.primary_color);
        }
        if (data.site_name) {
          document.title = data.site_name;
        }
      })
      .catch(() => {
        // Fallback to defaults
        document.documentElement.style.setProperty("--primary-brand", "#4f46e5");
      });
  }, []);

  return {
    logoUrl: config?.logo_url,
    siteName: config?.site_name || "AIMOS Enterprise",
    primaryColor: config?.primary_color || "#4f46e5"
  };
}
