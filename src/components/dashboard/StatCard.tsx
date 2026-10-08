import { cn } from "@/lib/cn";

export function StatCard({
  label,
  value,
  hint,
  tone = "default",
}: {
  label: string;
  value: string | number;
  hint?: string;
  tone?: "default" | "pass" | "fail";
}) {
  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-bg-elevated p-4 shadow-sm",
        tone === "pass" && "border-pass/25",
        tone === "fail" && "border-fail/25",
      )}
    >
      <div className="text-xs font-medium uppercase tracking-wide text-fg-subtle">
        {label}
      </div>
      <div
        className={cn(
          "mt-2 font-display text-3xl font-semibold tabular tracking-tight text-fg",
          tone === "pass" && "text-pass",
          tone === "fail" && "text-fail",
        )}
      >
        {value}
      </div>
      {hint ? <div className="mt-1 text-sm text-fg-muted">{hint}</div> : null}
    </div>
  );
}
