import { AgentNode } from "./AgentNode";
import type { AgentStep } from "./types";

type PipelineProps = {
  steps: AgentStep[];
};

export function Pipeline({ steps }: PipelineProps) {
  return (
    <div className="w-full overflow-x-auto pb-2">
      <div className="flex min-w-min items-center gap-4 md:gap-6">
        {steps.map((step, i) => (
          <div key={`${step.title}-${i}`} className="flex items-center gap-4">
            <AgentNode title={step.title} status={step.status} />
            {i < steps.length - 1 && (
              <span className="text-slate-400" aria-hidden>
                →
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
