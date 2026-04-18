"use client";

import Link from "next/link";
import { startTransition, useEffect, useState } from "react";
import { listAgents, type AgentsListResponse } from "@/lib/api/analytics";
import { openapiUrl, SERVICE_MODULES, swaggerUrl } from "@/lib/services-config";

export function ServicesHub() {
  const [agents, setAgents] = useState<AgentsListResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    startTransition(() => {
      void listAgents()
        .then(setAgents)
        .catch((e) =>
          setErr(e instanceof Error ? e.message : "Failed to load agents"),
        );
    });
  }, []);

  return (
    <div className="space-y-10">
      <section>
        <h2 className="text-lg font-semibold text-white">API & integrations</h2>
        <p className="mt-1 max-w-2xl text-sm text-slate-400">
          This app mirrors what the FastAPI backend exposes. Use the Control
          Tower for flows; use Swagger for raw requests.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <a
            href={swaggerUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700"
          >
            Open Swagger UI
          </a>
          <a
            href={openapiUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-xl border border-white/[0.12] px-4 py-2 text-sm text-slate-200 hover:bg-white/[0.06]"
          >
            OpenAPI JSON
          </a>
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
          Product modules
        </h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {SERVICE_MODULES.map((m) => (
            <div
              key={m.id}
              className="rounded-2xl border border-white/[0.06] bg-white/[0.03] p-4 backdrop-blur-sm"
            >
              <h3 className="font-medium text-slate-100">{m.title}</h3>
              <p className="mt-2 text-sm text-slate-400">{m.description}</p>
              <ul className="mt-3 space-y-1 font-mono text-xs text-slate-500">
                {m.methods.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
              <Link
                href={m.href}
                className="mt-4 inline-block text-sm text-violet-400 hover:text-violet-300"
              >
                Open in app →
              </Link>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-sm font-medium uppercase tracking-wide text-slate-500">
          BRD agents (graph order)
        </h2>
        {err && (
          <p className="mb-2 text-sm text-red-400" role="alert">
            {err}
          </p>
        )}
        {!agents && !err && (
          <p className="text-sm text-slate-500">Loading agent registry…</p>
        )}
        {agents && (
          <div className="rounded-2xl border border-white/[0.06] bg-white/[0.03] p-4 backdrop-blur-sm">
            <p className="text-sm text-slate-400">
              <span className="font-medium text-slate-200">{agents.count}</span>{" "}
              runners · single-agent endpoint:{" "}
              <code className="text-xs text-violet-400">
                POST /agents/{"{name}"}/run
              </code>
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {agents.agents.map((name) => (
                <span
                  key={name}
                  className="rounded-lg bg-white/[0.06] px-2.5 py-1 font-mono text-xs text-slate-300"
                >
                  {name}
                </span>
              ))}
            </div>
            {agents.prompt_bundles?.length ? (
              <p className="mt-4 text-xs text-slate-500">
                Prompt bundles: {agents.prompt_bundles.length} under{" "}
                <code className="text-slate-500">prompts/agents/</code>
              </p>
            ) : null}
          </div>
        )}
      </section>
    </div>
  );
}
