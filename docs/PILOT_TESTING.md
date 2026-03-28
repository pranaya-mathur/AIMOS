# AIMOS Pilot Testing Guide

This guide describes how to connect your **Local Development Repository** to **Bubble.io** for exhaustive pilot testing without manual configuration.

## 🚀 One-Step Pilot Mode

Run the following command from your project root:

```bash
make pilot
# OR
./scripts/start_pilot.sh
```

### What This Does:
1.  **Starts a Public Tunnel**: Uses `localtunnel` to expose `localhost:8000`.
2.  **Auto-Configures .env**: Updates `PUBLIC_API_BASE_URL` and `CORS_ORIGINS`.
3.  **Refreshes API**: Restores the OpenAPI schema so it uses the correct public URL for Bubble.

---

## 🏗️ Bubble.io Setup

1.  **Install API Connector**: In your Bubble app, go to *Plugins*.
2.  **Add New API**: Name it `AIMOS Pilot`.
3.  **Import from URL**: Copy the JSON link from your terminal (e.g., `https://xxxx.loca.lt/openapi.json`).
4.  **CORS**: Ensure your Bubble app origin (e.g., `https://yourapp.bubbleapps.io`) is in the `CORS_ORIGINS` list (handled automatically by `make pilot`).

---

## 🧪 Exhaustive Testing Scenarios

| Scenario | Goal |
| :--- | :--- |
| **End-to-End Campaign** | Create a campaign in Bubble → Monitor Celery logs locally → View generated strategy in Bubble. |
| **Real Webhooks** | Test Stripe or WhatsApp webhooks by pointing their dynamic URL to your tunnel address. |
| **Sync/Async Jobs** | Observe how Bubble polls the `/job/{task_id}` endpoint for long-running AI tasks. |

---

## 🔐 Security Note

> [!WARNING]
> The public tunnel URL is **temporary**. If you stop the script, your Bubble connection will break. For a permanent staging setup, use the **AWS Infrastructure** provided in `infra/aws/`.

> [!TIP]
> **Persistent URL**: If you have a Cloudflare account, you can create a zero-cost "Tunnel" for a permanent address. Contact support or check `infra/cloudflare/` for more info.
