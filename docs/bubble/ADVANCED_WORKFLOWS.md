# Advanced Bubble.io Workflows

This guide covers complex integrations, including the **Admin Dashboard** and **Robust Pipeline Management**.

---

## 🏗️ 1. Admin Dashboard (Quota Management)

**Goal**: Allow platform admins to view and update user quotas from a Bubble page.

### A. List All Users
1. **API Connector**: `GET /admin/users` (Ensure `Authorization: Bearer [admin_token]` is used).
2. **Repeating Group**: Set **Type of content** to `Admin - User` (or the specific AIMOS user data type from API Connector).
3. **Data source**: `Get data from external API → AIMOS - List Users`.

### B. Update User Quotas
1. **Button "Save Quotas"** inside a popup/cell → Workflow:
    - **API Connector**: `PATCH /admin/users/{user_id}`.
    - **Body**: 
      ```json
      {
        "monthly_campaign_quota": input_campaign_quota's value,
        "monthly_token_quota": input_token_quota's value
      }
      ```
    - **Notification**: Show an alert: "User [user's email] quotas updated successfully!"

---

## 🔄 2. Robust Pipeline Management (Status Polling)

**Goal**: Efficiently handle the 30-90 second delay during 12-agent processing.

### The "Loop" Workflow in Bubble:
1.  **Start Generation**: Call `POST /campaign/create` → Store `task_id` in a "Current Job ID" state.
2.  **Toggle a Loader**: Set a custom state `is_loading` = `yes`.
3.  **Recursive Workflow (Backend)**: 
    *   Create a Backend Workflow `check_job_status`.
    *   **Action 1**: `GET /job/{task_id}`.
    *   **Action 2 (Condition: "status" is not SUCCESS/FAILURE)**: Schedule `check_job_status` again in 5 seconds.
    *   **Action 3 (Condition: "status" is SUCCESS)**: 
        *   Trigger a data refresh.
        *   Set `is_loading` = `no`.

---

## 🚀 3. Launch Integrations

**Goal**: Trigger a Meta Ad or WhatsApp message directly from Bubble.

### Template: Meta Ad Launch
1.  **Button "Launch on Meta"**:
    *   `POST /launch/meta`.
    *   Ensure `META_ACCESS_TOKEN` is configured in the AIMOS `.env`.
    *   Handle the response: Display the generated Meta Campaign ID to the user.

---

## 🔒 4. Production Security
*   **Privacy Rules**: In Bubble, ensure that only "Admin" type users can view the page with the `/admin` API calls.
*   **Error Handling**: Always use the **"An API Connector error occurs"** workflow event in Bubble to catch `429` (Quota Exceeded) or `401` (Unauthorized) errors and show friendly messages to the user.
