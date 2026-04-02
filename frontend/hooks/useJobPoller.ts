"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getJobStatus } from "@/lib/api/campaign";

type PollState =
  | { phase: "idle" }
  | { phase: "polling"; taskId: string }
  | { phase: "success"; result: unknown }
  | { phase: "failure"; message: string };

const TERMINAL = new Set(["SUCCESS", "FAILURE", "REVOKED"]);

export function useJobPoller(intervalMs = 2500) {
  const [state, setState] = useState<PollState>({ phase: "idle" });
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const stop = useCallback(() => {
    if (timer.current) {
      clearInterval(timer.current);
      timer.current = null;
    }
  }, []);

  const start = useCallback(
    (taskId: string) => {
      stop();
      setState({ phase: "polling", taskId });

      const tick = async () => {
        try {
          const job = await getJobStatus(taskId);
          if (TERMINAL.has(job.status)) {
            stop();
            if (job.status === "SUCCESS") {
              setState({ phase: "success", result: job.result });
            } else {
              setState({
                phase: "failure",
                message: String(job.result ?? job.status),
              });
            }
          }
        } catch (e) {
          stop();
          setState({
            phase: "failure",
            message: e instanceof Error ? e.message : "Job poll failed",
          });
        }
      };

      void tick();
      timer.current = setInterval(() => void tick(), intervalMs);
    },
    [intervalMs, stop],
  );

  useEffect(() => () => stop(), [stop]);

  const reset = useCallback(() => {
    stop();
    setState({ phase: "idle" });
  }, [stop]);

  return { state, start, stop, reset };
}
