import { cn } from "@/lib/cn";

export function Badge({
  children,
  tone = "neutral",
  className,
}: {
  children: React.ReactNode;
  tone?: "neutral" | "pass" | "fail" | "warn" | "accent";
  className?: string;
}) {
  const tones = {
    neutral: "border-border bg-bg-subtle text-fg-muted",
    pass: "border-pass/30 bg-pass/10 text-pass",
    fail: "border-fail/30 bg-fail/10 text-fail",
    warn: "border-warn/30 bg-warn/10 text-warn",
    accent: "border-border-strong bg-accent text-accent-fg",
  } as const;
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        tones[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
