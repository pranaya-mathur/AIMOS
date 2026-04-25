# Bubble.io Integration Guide

To integrate the **AIMOS Enterprise** system with **Bubble.io**, follow these recommended next steps to set up your APIs and connect the systems.

## 1. Required API Keys
Obtain these keys from the respective providers and add them to your `.env` file.

| Provider | Purpose | Key Needed |
| :--- | :--- | :--- |
| **OpenAI** (Critical) | Powers the 14-agent pipeline (`gpt-4o-mini`). | `OPENAI_API_KEY` |
| **Stripe** (Optional) | Handles payments and subscriptions in Bubble. | `STRIPE_SECRET_KEY` |
| **AdCreative.ai** | Generates high-conversion ad images. | `ADCREATIVE_API_KEY` |
| **Pictory** | Generates AI videos for social media. | `PICTORY_API_KEY` |
| **ElevenLabs** | Generates human-like AI voiceovers. | `ELEVENLABS_API_KEY` |
| **Meta Graph API** | Launches ads to Facebook/Instagram. | `META_ACCESS_TOKEN` |

## 2. Step-by-Step Setup

### Step 1: Deploy your AIMOS API
Deploy this repository to a service with a public HTTPS URL (e.g., AWS, Render, Railway, or VPS).
*   **Recommendation**: Use the included `infra/aws/terraform/` for a production-ready AWS stack.

### Step 2: Configure Environment (.env)
Update your production `.env` to allow your Bubble app origins:
```bash
# Allow your Bubble app to talk to the API
CORS_ORIGINS=https://your-app-name.bubbleapps.io
PUBLIC_API_BASE_URL=https://api.yourdomain.com
```

### Step 3: Bubble API Connector Configuration
1.  **Install Plugin**: Install **API Connector** in Bubble.
2.  **Add API**: Name it "AIMOS API".
3.  **Authentication**: Use `Header` with Key: `Authorization`, Value: `Bearer [token]`.
4.  **Import OpenAPI**: Use the URL `https://api.yourdomain.com/openapi.json` to automatically import all endpoints.

### Step 4: The Core Workflow
1.  **Auth**: Call `POST /auth/login` to get a JWT. Store it in a Custom State or browser cookie.
2.  **Campaign**: Call `POST /campaign/create` with the user's brief.
3.  **Polling**: Since the 14-agent pipeline takes time, use a "Do every X seconds" workflow in Bubble to poll `GET /job/{task_id}` until the status is `SUCCESS`.
4.  **Display**: Retrieve the results from `output` once the job is finished.

## 3. Local Development Tip
Use `AUTH_DISABLED=1` and `MOCK_MEDIA_PROVIDER=1` in your local `.env` while building the Bubble UI to avoid costs and skip authentication steps during initial development.
