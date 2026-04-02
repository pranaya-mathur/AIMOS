"use client";

import { startTransition, useEffect, useState } from "react";
import {
  createSubscription,
  getSubscription,
  createPortalSession,
  type SubscriptionInfo,
} from "@/lib/api/billing";
import { getUsageMe, type UsageMe } from "@/lib/api/analytics";
import { PLAN_TIERS, type PlanTier } from "@/lib/plan-tiers";

/* ------------------------------------------------------------------ */
/*  Inline styles for the premium pricing page                        */
/* ------------------------------------------------------------------ */

const styles = {
  wrapper: {
    maxWidth: "1200px",
    margin: "0 auto",
    padding: "0 24px",
  } as React.CSSProperties,

  hero: {
    textAlign: "center",
    marginBottom: "48px",
  } as React.CSSProperties,

  heroTitle: {
    fontSize: "36px",
    fontWeight: 800,
    background: "linear-gradient(135deg, #6366f1 0%, #d946ef 50%, #f43f5e 100%)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
    marginBottom: "12px",
    letterSpacing: "-0.02em",
  } as React.CSSProperties,

  heroSub: {
    fontSize: "16px",
    color: "#64748b",
    maxWidth: "600px",
    margin: "0 auto",
    lineHeight: 1.6,
  } as React.CSSProperties,

  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))",
    gap: "24px",
    alignItems: "stretch",
  } as React.CSSProperties,

  card: (tier: PlanTier, isCurrentTier: boolean) =>
    ({
      position: "relative",
      background: "#ffffff",
      borderRadius: "20px",
      padding: "32px 28px",
      display: "flex",
      flexDirection: "column",
      border: tier.popular
        ? "2px solid transparent"
        : isCurrentTier
          ? "2px solid #22c55e"
          : "1px solid #e2e8f0",
      backgroundImage: tier.popular
        ? `linear-gradient(#fff, #fff), ${tier.gradient}`
        : undefined,
      backgroundOrigin: tier.popular ? "border-box" : undefined,
      backgroundClip: tier.popular ? "padding-box, border-box" : undefined,
      boxShadow: tier.popular
        ? "0 20px 60px rgba(139, 92, 246, 0.15)"
        : "0 4px 24px rgba(0, 0, 0, 0.04)",
      transition: "transform 0.25s ease, box-shadow 0.25s ease",
      overflow: "hidden",
    }) as React.CSSProperties,

  cardHover: {
    transform: "translateY(-4px)",
    boxShadow: "0 24px 64px rgba(139, 92, 246, 0.2)",
  } as React.CSSProperties,

  popularBadge: {
    position: "absolute",
    top: "0",
    right: "24px",
    background: "linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)",
    color: "#fff",
    fontSize: "11px",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    padding: "6px 16px",
    borderRadius: "0 0 12px 12px",
  } as React.CSSProperties,

  currentBadge: {
    position: "absolute",
    top: "0",
    left: "24px",
    background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
    color: "#fff",
    fontSize: "11px",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    padding: "6px 16px",
    borderRadius: "0 0 12px 12px",
  } as React.CSSProperties,

  tierName: {
    fontSize: "14px",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    color: "#8b5cf6",
    marginBottom: "8px",
  } as React.CSSProperties,

  priceRow: {
    display: "flex",
    alignItems: "baseline",
    gap: "4px",
    marginBottom: "8px",
  } as React.CSSProperties,

  priceAmount: {
    fontSize: "48px",
    fontWeight: 800,
    color: "#0f172a",
    letterSpacing: "-0.03em",
    lineHeight: 1,
  } as React.CSSProperties,

  pricePeriod: {
    fontSize: "16px",
    color: "#94a3b8",
    fontWeight: 500,
  } as React.CSSProperties,

  tagline: {
    fontSize: "14px",
    color: "#64748b",
    lineHeight: 1.5,
    marginBottom: "24px",
    minHeight: "42px",
  } as React.CSSProperties,

  divider: {
    width: "100%",
    height: "1px",
    background: "linear-gradient(90deg, transparent, #e2e8f0, transparent)",
    margin: "0 0 20px",
  } as React.CSSProperties,

  featureList: {
    listStyle: "none",
    padding: 0,
    margin: "0 0 28px",
    flex: 1,
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  } as React.CSSProperties,

  featureItem: {
    display: "flex",
    alignItems: "flex-start",
    gap: "10px",
    fontSize: "14px",
    color: "#334155",
    lineHeight: 1.4,
  } as React.CSSProperties,

  checkIcon: {
    flexShrink: 0,
    width: "18px",
    height: "18px",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "10px",
    marginTop: "1px",
  } as React.CSSProperties,

  ctaButton: (tier: PlanTier, disabled: boolean) =>
    ({
      width: "100%",
      padding: "14px 24px",
      borderRadius: "12px",
      border: "none",
      fontSize: "15px",
      fontWeight: 700,
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: disabled ? 0.6 : 1,
      color: tier.popular ? "#ffffff" : "#6366f1",
      background: tier.popular
        ? tier.gradient
        : "rgba(99, 102, 241, 0.08)",
      transition: "all 0.2s ease",
      letterSpacing: "0.01em",
    }) as React.CSSProperties,

  /* ── Status Bar ── */
  statusBar: {
    marginBottom: "40px",
    background: "linear-gradient(135deg, rgba(99, 102, 241, 0.04) 0%, rgba(217, 70, 239, 0.04) 100%)",
    borderRadius: "16px",
    padding: "24px 28px",
    border: "1px solid rgba(99, 102, 241, 0.1)",
  } as React.CSSProperties,

  statusGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
    gap: "20px",
  } as React.CSSProperties,

  statusLabel: {
    fontSize: "12px",
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    color: "#94a3b8",
    marginBottom: "4px",
  } as React.CSSProperties,

  statusValue: {
    fontSize: "20px",
    fontWeight: 700,
    color: "#0f172a",
  } as React.CSSProperties,

  manageButton: {
    marginTop: "16px",
    padding: "10px 20px",
    borderRadius: "10px",
    border: "1px solid #e2e8f0",
    background: "#ffffff",
    fontSize: "13px",
    fontWeight: 600,
    color: "#64748b",
    cursor: "pointer",
    transition: "all 0.2s ease",
  } as React.CSSProperties,

  errorBanner: {
    padding: "12px 20px",
    borderRadius: "12px",
    background: "rgba(239, 68, 68, 0.06)",
    border: "1px solid rgba(239, 68, 68, 0.15)",
    color: "#dc2626",
    fontSize: "14px",
    marginBottom: "24px",
  } as React.CSSProperties,
};


/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

export function BillingPlans() {
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [usage, setUsage] = useState<UsageMe | null>(null);
  const [busy, setBusy] = useState<string | null>(null); // tier slug being purchased
  const [err, setErr] = useState<string | null>(null);
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  useEffect(() => {
    startTransition(() => {
      void getSubscription()
        .then(setSubscription)
        .catch(() => setSubscription(null));
      void getUsageMe()
        .then(setUsage)
        .catch(() => setUsage(null));
    });
  }, []);

  async function handleSubscribe(tier: PlanTier) {
    if (tier.slug === "enterprise") {
      window.open("mailto:sales@aimos.ai?subject=AIMOS Enterprise Inquiry", "_blank");
      return;
    }
    setErr(null);
    setBusy(tier.slug);
    try {
      const origin = typeof window !== "undefined" ? window.location.origin : "";
      const res = await createSubscription({
        price_id: tier.slug, // Backend resolves via env
        success_url: `${origin}/billing?subscribed=${tier.slug}`,
        cancel_url: `${origin}/billing`,
      });
      window.location.href = res.url;
    } catch (e) {
      setErr(
        e instanceof Error
          ? e.message
          : "Subscription failed — is Stripe configured?",
      );
    } finally {
      setBusy(null);
    }
  }

  async function handleManage() {
    try {
      const origin = typeof window !== "undefined" ? window.location.origin : "";
      const res = await createPortalSession(`${origin}/billing`);
      window.location.href = res.url;
    } catch (e) {
      setErr(
        e instanceof Error ? e.message : "Could not open billing portal",
      );
    }
  }

  const currentTier = subscription?.tier || "free";
  const currentStatus = subscription?.status || "none";

  return (
    <div style={styles.wrapper}>
      {/* ── Hero ── */}
      <div style={styles.hero}>
        <h1 style={styles.heroTitle}>Choose Your Plan</h1>
        <p style={styles.heroSub}>
          Scale your AI marketing with the power of 12 autonomous agents.
          Launch campaigns across Meta, Google, X, WhatsApp — all from one platform.
        </p>
      </div>

      {/* ── Current Subscription Status ── */}
      {subscription && currentTier !== "free" && (
        <div style={styles.statusBar}>
          <div style={styles.statusGrid}>
            <div>
              <div style={styles.statusLabel}>Current Plan</div>
              <div style={styles.statusValue}>
                {currentTier.charAt(0).toUpperCase() + currentTier.slice(1)}
              </div>
            </div>
            <div>
              <div style={styles.statusLabel}>Status</div>
              <div
                style={{
                  ...styles.statusValue,
                  color:
                    currentStatus === "active"
                      ? "#16a34a"
                      : currentStatus === "past_due"
                        ? "#ea580c"
                        : "#64748b",
                }}
              >
                {currentStatus === "active"
                  ? "● Active"
                  : currentStatus === "past_due"
                    ? "⚠ Past Due"
                    : currentStatus.charAt(0).toUpperCase() + currentStatus.slice(1)}
              </div>
            </div>
            {usage && (
              <>
                <div>
                  <div style={styles.statusLabel}>Campaigns Used</div>
                  <div style={styles.statusValue}>
                    {usage.campaigns.used}
                    {usage.campaigns.limit != null
                      ? ` / ${usage.campaigns.limit}`
                      : ""}
                  </div>
                </div>
                <div>
                  <div style={styles.statusLabel}>Tokens Used</div>
                  <div style={styles.statusValue}>
                    {usage.tokens.used.toLocaleString()}
                    {usage.tokens.limit != null
                      ? ` / ${usage.tokens.limit.toLocaleString()}`
                      : ""}
                  </div>
                </div>
              </>
            )}
          </div>
          {subscription.stripe_customer_id && (
            <button
              type="button"
              onClick={() => void handleManage()}
              style={styles.manageButton}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#8b5cf6";
                e.currentTarget.style.color = "#8b5cf6";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "#e2e8f0";
                e.currentTarget.style.color = "#64748b";
              }}
            >
              Manage Subscription →
            </button>
          )}
        </div>
      )}

      {/* ── Error ── */}
      {err && (
        <div style={styles.errorBanner} role="alert">
          {err}
        </div>
      )}

      {/* ── Pricing Cards ── */}
      <div style={styles.grid}>
        {PLAN_TIERS.map((tier) => {
          const isCurrentTier = currentTier === tier.slug && currentStatus === "active";
          const isHovered = hoveredCard === tier.slug;
          const cardStyle = {
            ...styles.card(tier, isCurrentTier),
            ...(isHovered ? styles.cardHover : {}),
          };

          return (
            <div
              key={tier.slug}
              style={cardStyle}
              onMouseEnter={() => setHoveredCard(tier.slug)}
              onMouseLeave={() => setHoveredCard(null)}
            >
              {tier.popular && (
                <div style={styles.popularBadge}>Most Popular</div>
              )}
              {isCurrentTier && (
                <div style={styles.currentBadge}>Current Plan</div>
              )}

              <div style={styles.tierName}>{tier.name}</div>

              <div style={styles.priceRow}>
                <span style={styles.priceAmount}>{tier.price}</span>
                {tier.priceValue > 0 && (
                  <span style={styles.pricePeriod}>/month</span>
                )}
              </div>

              <p style={styles.tagline}>{tier.tagline}</p>

              <div style={styles.divider} />

              <ul style={styles.featureList}>
                {tier.features.map((feature, i) => (
                  <li key={i} style={styles.featureItem}>
                    <span
                      style={{
                        ...styles.checkIcon,
                        background: tier.popular
                          ? "linear-gradient(135deg, #8b5cf6, #d946ef)"
                          : "rgba(99, 102, 241, 0.1)",
                        color: tier.popular ? "#fff" : "#6366f1",
                      }}
                    >
                      ✓
                    </span>
                    {feature}
                  </li>
                ))}
              </ul>

              <button
                type="button"
                disabled={isCurrentTier || busy === tier.slug}
                onClick={() => void handleSubscribe(tier)}
                style={styles.ctaButton(tier, isCurrentTier || busy === tier.slug)}
                onMouseEnter={(e) => {
                  if (!isCurrentTier) {
                    e.currentTarget.style.transform = "scale(1.02)";
                    if (!tier.popular) {
                      e.currentTarget.style.background = "rgba(99, 102, 241, 0.15)";
                    }
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "scale(1)";
                  if (!tier.popular) {
                    e.currentTarget.style.background = "rgba(99, 102, 241, 0.08)";
                  }
                }}
              >
                {isCurrentTier
                  ? "✓ Current Plan"
                  : busy === tier.slug
                    ? "Redirecting…"
                    : tier.cta}
              </button>
            </div>
          );
        })}
      </div>

      {/* ── Footer note ── */}
      <p
        style={{
          textAlign: "center",
          fontSize: "13px",
          color: "#94a3b8",
          marginTop: "40px",
          lineHeight: 1.6,
        }}
      >
        All plans include a 14-day money-back guarantee. Cancel anytime from
        your billing portal.
        <br />
        Need a custom plan? {" "}
        <a
          href="mailto:sales@aimos.ai"
          style={{ color: "#8b5cf6", textDecoration: "none", fontWeight: 600 }}
        >
          Talk to sales →
        </a>
      </p>
    </div>
  );
}
