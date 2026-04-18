"use client";

import Link from "next/link";
import { useState } from "react";
import { TaskStatusPoller } from "@/components/jobs/TaskStatusPoller";
import {
  enqueueAdcreative,
  enqueueElevenlabs,
  enqueuePictory,
} from "@/lib/api/media-jobs";
import { swaggerUrl } from "@/lib/services-config";

type Provider = "adcreative" | "pictory" | "elevenlabs";

export function MediaStudio() {
  const [jsonText, setJsonText] = useState("{}");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(provider: Provider) {
    setErr(null);
    setTaskId(null);
    let input: Record<string, unknown>;
    try {
      const parsed = JSON.parse(jsonText) as unknown;
      input =
        parsed && typeof parsed === "object" && !Array.isArray(parsed)
          ? (parsed as Record<string, unknown>)
          : {};
    } catch {
      setErr("Invalid JSON in payload");
      return;
    }
    setBusy(true);
    try {
      const res =
        provider === "adcreative"
          ? await enqueueAdcreative(input)
          : provider === "pictory"
            ? await enqueuePictory(input)
            : await enqueueElevenlabs(input);
      setTaskId(res.task_id);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Enqueue failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <p className="text-sm">
        <Link
          href="/media-assets"
          className="font-medium text-violet-400 hover:text-violet-300"
        >
          Browse media asset library →
        </Link>
      </p>
      <p className="text-sm text-slate-400">
        Queues Celery jobs via{" "}
        <code className="text-slate-500">POST /media/…/create</code>. Payload
        shape depends on the provider SDK — check{" "}
        <a href={swaggerUrl()} className="text-violet-400 hover:text-violet-300 hover:underline">
          Swagger
        </a>{" "}
        and backend integration code.
      </p>

      <label className="block text-sm text-slate-400">
        JSON input (object)
        <textarea
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
          rows={12}
          className="mt-1 w-full rounded-xl border border-white/[0.1] bg-white/[0.04] p-3 font-mono text-xs text-slate-200 focus:border-violet-500/50 focus:outline-none focus:ring-2 focus:ring-violet-500/20"
        />
      </label>

      {err && (
        <p className="text-sm text-rose-400" role="alert">
          {err}
        </p>
      )}

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={busy}
          onClick={() => void submit("adcreative")}
          className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          AdCreative
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => void submit("pictory")}
          className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Pictory
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={() => void submit("elevenlabs")}
          className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          ElevenLabs
        </button>
      </div>

      <TaskStatusPoller taskId={taskId} />
    </div>
  );
}
