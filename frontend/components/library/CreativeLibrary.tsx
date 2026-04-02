"use client";

import { useCallback, useState } from "react";
import { AssetCard } from "@/components/assets/AssetCard";
import { getJobStatus } from "@/lib/api/campaign";
import { queueCreativeVariations } from "@/lib/api/creatives";

type Row = { id: string; title: string; body: string; status: string };

async function waitForJob(taskId: string): Promise<unknown> {
  for (let i = 0; i < 120; i++) {
    const j = await getJobStatus(taskId);
    if (j.status === "SUCCESS") return j.result;
    if (j.status === "FAILURE" || j.status === "REVOKED") {
      throw new Error(String(j.result ?? j.status));
    }
    await new Promise((r) => setTimeout(r, 2000));
  }
  throw new Error("Timed out waiting for creatives");
}

export function CreativeLibrary() {
  const [brief, setBrief] = useState("");
  const [n, setN] = useState(3);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<Row[]>([]);

  const onGenerate = useCallback(async () => {
    setError(null);
    setBusy(true);
    try {
      const { task_ids } = await queueCreativeVariations({
        brief: brief.trim(),
        n: Math.min(10, Math.max(1, n)),
      });
      const next: Row[] = task_ids.map((id, i) => ({
        id,
        title: `Variation ${i + 1}`,
        body: "…",
        status: "running",
      }));
      setRows(next);

      const results = await Promise.all(
        task_ids.map(async (taskId, i) => {
          try {
            const result = (await waitForJob(taskId)) as {
              index?: number;
              copy?: string;
            };
            return {
              id: taskId,
              title: `Variation ${i + 1}`,
              body: result?.copy ?? JSON.stringify(result),
              status: "done",
            } satisfies Row;
          } catch (e) {
            return {
              id: taskId,
              title: `Variation ${i + 1}`,
              body: e instanceof Error ? e.message : "Failed",
              status: "failed",
            } satisfies Row;
          }
        }),
      );
      setRows(results);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }, [brief, n]);

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-medium text-slate-700">
          Generate copy variations
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Calls <code className="text-slate-600">POST /creatives/variations</code>{" "}
          and polls each <code className="text-slate-600">GET /job/{"{id}"}</code>.
        </p>
        <textarea
          value={brief}
          onChange={(e) => setBrief(e.target.value)}
          placeholder="Creative brief"
          rows={4}
          className="mt-4 w-full rounded-xl border border-slate-200 bg-slate-50 p-3 text-slate-900 placeholder:text-slate-400 focus:border-violet-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-violet-500/15"
        />
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-slate-600">
            Count
            <input
              type="number"
              min={1}
              max={10}
              value={n}
              onChange={(e) => setN(Number(e.target.value))}
              className="w-16 rounded-lg border border-slate-200 bg-white px-2 py-1 text-slate-900 shadow-sm"
            />
          </label>
          <button
            type="button"
            disabled={busy || !brief.trim()}
            onClick={() => void onGenerate()}
            className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? "Working…" : "Queue variations"}
          </button>
        </div>
        {error && (
          <p className="mt-3 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
          Results
        </h2>
        {rows.length === 0 ? (
          <p className="text-sm text-slate-500">
            No variations yet — run a brief above.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {rows.map((r) => (
              <AssetCard
                key={r.id}
                title={`${r.title} · ${r.status}`}
                preview={r.body}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
