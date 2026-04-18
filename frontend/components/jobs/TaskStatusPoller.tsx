"use client";

import { startTransition, useEffect, useState } from "react";
import { getJobStatus } from "@/lib/api/campaign";

type Props = { taskId: string | null };

export function TaskStatusPoller({ taskId }: Props) {
  const [status, setStatus] = useState<string | null>(null);
  const [result, setResult] = useState<unknown>(null);

  useEffect(() => {
    if (!taskId) {
      startTransition(() => {
        setStatus(null);
        setResult(null);
      });
      return;
    }
    let cancelled = false;
    const tick = async () => {
      try {
        const j = await getJobStatus(taskId);
        if (cancelled) return;
        setStatus(j.status);
        setResult(j.result);
        if (
          j.status === "SUCCESS" ||
          j.status === "FAILURE" ||
          j.status === "REVOKED"
        ) {
          return;
        }
      } catch {
        if (!cancelled) setStatus("ERROR");
      }
    };
    void tick();
    const id = setInterval(() => void tick(), 2000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [taskId]);

  if (!taskId) return null;

  return (
    <div className="mt-4 rounded-xl border border-white/[0.08] bg-white/[0.04] p-3 font-mono text-xs text-slate-300">
      <p>
        <span className="text-slate-500">task_id</span> {taskId}
      </p>
      <p className="mt-1">
        <span className="text-slate-500">status</span>{" "}
        <span
          className={
            status === "SUCCESS"
              ? "text-emerald-400"
              : status === "FAILURE"
                ? "text-rose-400"
                : "text-amber-400"
          }
        >
          {status ?? "…"}
        </span>
      </p>
      {result != null && (
        <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap text-slate-400">
          {typeof result === "string"
            ? result
            : JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
