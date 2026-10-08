import { useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  CheckCircle2,
  FileText,
  FolderOpen,
  Library,
  Package,
  Search,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import ledger from "@/data/ledger.json";
import vault from "@/data/vault.json";
import { Badge } from "@/components/ui/badge";
import { StatCard } from "@/components/dashboard/StatCard";
import { Section } from "@/components/dashboard/Section";
import { cn } from "@/lib/cn";

export const Route = createFileRoute("/")({ component: ClearanceHome });

type TabId = "gate" | "deps" | "catalog" | "notices" | "vault";

const TABS: { id: TabId; label: string; icon: typeof ShieldCheck }[] = [
  { id: "gate", label: "Gate", icon: ShieldCheck },
  { id: "deps", label: "Dependencies", icon: Package },
  { id: "catalog", label: "Catalog", icon: Library },
  { id: "notices", label: "Notices", icon: FileText },
  { id: "vault", label: "Vault", icon: FolderOpen },
];

function ClearanceHome() {
  const [tab, setTab] = useState<TabId>("gate");
  const [q, setQ] = useState("");
  const [vaultFilter, setVaultFilter] = useState<"all" | "ops" | "research" | "restricted">("all");

  const deps = ledger.dependencies ?? [];
  const rollup = ledger.licenseRollup ?? [];
  const summary = ledger.summary ?? {};
  const passed = Boolean(summary.gate_passed);

  const filteredDeps = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return deps;
    return deps.filter((d) =>
      [d.name, d.version, d.raw_license, d.spdx_license, d.ecosystem]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(needle),
    );
  }, [deps, q]);

  const github = ledger.githubPopular ?? [];
  const normMap = ledger.normalizationMap ?? [];
  const themes = vault.themes ?? [];
  const packages = vault.sourceToSkill ?? [];
  const remaining = vault.remainingSkills ?? [];
  const restricted = vault.restricted ?? [];

  return (
    <div className="min-h-screen bg-bg text-fg">
      <header className="border-b border-border bg-bg-elevated/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-fg-subtle">
                Clearance Ledger
              </div>
              <h1 className="mt-1 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
                License & Skill Distillation
              </h1>
              <p className="mt-2 max-w-2xl text-sm text-fg-muted">
                Unified SPDX catalog, dependency normalization, third-party notices,
                CI compliance gate, and lawful vault skill inventory from the
                connected Drive pack.
              </p>
            </div>
            <div className="flex flex-col items-end gap-2">
              <Badge tone={passed ? "pass" : "fail"}>
                {passed ? "Gate Passed" : "Gate Failed"}
              </Badge>
              <a
                href="/THIRD-PARTY-NOTICES.txt"
                className="text-sm text-fg-muted underline-offset-4 hover:text-fg hover:underline"
              >
                Download notices
              </a>
            </div>
          </div>

          <nav className="flex gap-1 overflow-x-auto pb-1" aria-label="Primary">
            {TABS.map(({ id, label, icon: Icon }) => {
              const active = tab === id;
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => setTab(id)}
                  className={cn(
                    "inline-flex shrink-0 items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors",
                    active
                      ? "border-border-strong bg-bg-subtle text-fg"
                      : "border-transparent text-fg-muted hover:border-border hover:bg-bg-elevated hover:text-fg",
                  )}
                >
                  <Icon className="size-4" strokeWidth={1.75} />
                  {label}
                </button>
              );
            })}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">
        {tab === "gate" && (
          <>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                label="Compliance"
                value={passed ? "PASS" : "FAIL"}
                hint={`${summary.allowed_packages ?? 0} allowed · ${summary.blocked_packages ?? 0} blocked`}
                tone={passed ? "pass" : "fail"}
              />
              <StatCard
                label="Packages scanned"
                value={summary.synthesized_packages ?? summary.python_packages_scanned ?? 0}
                hint="Python environment (pip-licenses)"
              />
              <StatCard
                label="SPDX catalog"
                value={summary.spdx_total ?? 0}
                hint={`${summary.osi_approved_count ?? 0} OSI-approved`}
              />
              <StatCard
                label="Normalized IDs"
                value={summary.distinct_spdx_normalized ?? 0}
                hint={`from ${summary.distinct_used_license_strings ?? 0} raw strings`}
              />
            </div>

            <Section
              title="License family rollup"
              description="Counts after aggressive SPDX normalization of messy dependency metadata."
            >
              <div className="h-72 rounded-xl border border-border bg-bg-elevated p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={rollup} margin={{ top: 8, right: 8, left: 0, bottom: 48 }}>
                    <CartesianGrid stroke="rgba(244,244,245,0.06)" vertical={false} />
                    <XAxis
                      dataKey="id"
                      tick={{ fill: "#a1a1aa", fontSize: 11 }}
                      interval={0}
                      angle={-28}
                      textAnchor="end"
                      height={60}
                    />
                    <YAxis allowDecimals={false} tick={{ fill: "#a1a1aa", fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        background: "#121214",
                        border: "1px solid #3f3f46",
                        borderRadius: 12,
                        color: "#f4f4f5",
                      }}
                    />
                    <Bar dataKey="count" fill="#c8ccd4" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Section>

            <Section
              title="Normalization map"
              description="Raw dependency strings mapped to canonical SPDX expressions."
            >
              <div className="overflow-hidden rounded-xl border border-border">
                <table className="w-full text-left text-sm">
                  <thead className="bg-bg-elevated text-fg-subtle">
                    <tr>
                      <th className="px-4 py-3 font-medium">Raw string</th>
                      <th className="px-4 py-3 font-medium">SPDX</th>
                    </tr>
                  </thead>
                  <tbody>
                    {normMap.map((row) => (
                      <tr key={row.raw} className="border-t border-border">
                        <td className="px-4 py-3 font-mono text-xs text-fg-muted">
                          {row.raw}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex flex-wrap gap-1.5">
                            {row.spdx.map((id) => (
                              <Badge key={id} tone="neutral">
                                {id}
                              </Badge>
                            ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Section>
          </>
        )}

        {tab === "deps" && (
          <Section
            title="Dependencies"
            description="Every scanned package with raw license metadata and normalized SPDX ID."
            action={
              <label className="relative block w-full min-w-[16rem] sm:w-72">
                <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-fg-subtle" />
                <input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Filter packages…"
                  className="w-full rounded-lg border border-border bg-bg-elevated py-2 pl-9 pr-3 text-sm text-fg outline-none ring-0 placeholder:text-fg-subtle focus:border-border-strong"
                />
              </label>
            }
          >
            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-bg-elevated text-fg-subtle">
                  <tr>
                    <th className="px-4 py-3 font-medium">Package</th>
                    <th className="px-4 py-3 font-medium">Version</th>
                    <th className="px-4 py-3 font-medium">Raw</th>
                    <th className="px-4 py-3 font-medium">SPDX</th>
                    <th className="px-4 py-3 font-medium">Gate</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDeps.map((d) => (
                    <tr key={`${d.ecosystem}-${d.name}-${d.version}`} className="border-t border-border">
                      <td className="px-4 py-3 font-medium">{d.name}</td>
                      <td className="px-4 py-3 font-mono text-xs text-fg-muted">
                        {d.version}
                      </td>
                      <td className="max-w-[14rem] truncate px-4 py-3 text-fg-muted" title={d.raw_license}>
                        {d.raw_license}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs">{d.spdx_license}</td>
                      <td className="px-4 py-3">
                        {d.allowed ? (
                          <Badge tone="pass">
                            <span className="inline-flex items-center gap-1">
                              <CheckCircle2 className="size-3.5" /> OK
                            </span>
                          </Badge>
                        ) : (
                          <Badge tone="fail">
                            <span className="inline-flex items-center gap-1">
                              <TriangleAlert className="size-3.5" /> Block
                            </span>
                          </Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        )}

        {tab === "catalog" && (
          <>
            <Section
              title="GitHub popular licenses"
              description="Licenses exposed by the GitHub Licenses API — common choices for new repositories."
            >
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {github.map((lic) => (
                  <div
                    key={lic.id}
                    className="rounded-xl border border-border bg-bg-elevated p-4"
                  >
                    <div className="font-mono text-xs text-fg-subtle">{lic.spdx_id}</div>
                    <div className="mt-1 font-medium">{lic.name}</div>
                    <div className="mt-2 text-xs text-fg-muted">key: {lic.id}</div>
                  </div>
                ))}
              </div>
            </Section>
            <Section
              title="SPDX catalog sample"
              description={`First 80 of ${ledger.spdxTotal ?? summary.spdx_total ?? 0} SPDX identifiers (full list in unified_licenses.json).`}
            >
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {(ledger.spdxSample ?? []).map((lic) => (
                  <div
                    key={lic.id}
                    className="rounded-lg border border-border bg-bg-elevated px-3 py-2"
                  >
                    <div className="font-mono text-[11px] text-fg">{lic.id}</div>
                    <div className="mt-0.5 line-clamp-2 text-[11px] text-fg-muted">
                      {lic.name}
                    </div>
                    {lic.osiApproved ? (
                      <Badge tone="pass" className="mt-2">
                        OSI
                      </Badge>
                    ) : null}
                  </div>
                ))}
              </div>
            </Section>
          </>
        )}

        {tab === "notices" && (
          <Section
            title="Third-party notices"
            description="Production-ready attribution file for distribution. Generated from normalized dependency inventory."
            action={
              <a
                href="/THIRD-PARTY-NOTICES.txt"
                className="inline-flex items-center gap-2 rounded-lg border border-border-strong bg-accent px-3 py-2 text-sm font-medium text-accent-fg"
              >
                <FileText className="size-4" />
                Open notices file
              </a>
            }
          >
            <div className="rounded-xl border border-border bg-bg-elevated p-5">
              <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap font-mono text-xs leading-relaxed text-fg-muted">
                {`========================================================================
THIRD-PARTY SOFTWARE NOTICES AND INFORMATION
========================================================================

Generated from unified_licenses.json after SPDX normalization.
Packages included: ${deps.length}
Gate: ${passed ? "PASSED" : "FAILED"}

Summary rollup:
${rollup.map((r) => `  ${r.id.padEnd(32)} ${r.count}`).join("\n")}

Full attribution text is served at /THIRD-PARTY-NOTICES.txt
(also written to artifacts/THIRD-PARTY-NOTICES.txt).
`}
              </pre>
            </div>
          </Section>
        )}

        {tab === "vault" && (
          <>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard label="Source→Skill packages" value={vault.stats?.sourceToSkillPackages ?? 0} />
              <StatCard label="Extracted SKILL.md" value={vault.stats?.extractedSkillMdCount ?? 0} />
              <StatCard label="OpenClaw catalog" value={vault.stats?.openclawCatalogCount ?? 0} />
              <StatCard label="Research skills" value={vault.stats?.remainingSkills ?? 0} />
            </div>

            <Section
              title="Distillation themes"
              description={`Folder: ${vault.sourceFolder} — inventory only; restricted items cataloged without inlining sensitive bodies.`}
            >
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                {themes.map((t) => (
                  <article
                    key={t.title}
                    className="rounded-xl border border-border bg-bg-elevated p-4"
                  >
                    <h3 className="font-medium text-fg">{t.title}</h3>
                    <p className="mt-2 text-sm text-fg-muted">{t.body}</p>
                  </article>
                ))}
              </div>
            </Section>

            <Section
              title="Skill encyclopedia"
              description="Operational source-to-skill packages and remaining research skills."
              action={
                <div className="flex flex-wrap gap-1">
                  {(
                    [
                      ["all", "All"],
                      ["ops", "Operational"],
                      ["research", "Research"],
                      ["restricted", "Restricted"],
                    ] as const
                  ).map(([id, label]) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setVaultFilter(id)}
                      className={cn(
                        "rounded-lg border px-3 py-1.5 text-xs font-medium",
                        vaultFilter === id
                          ? "border-border-strong bg-bg-subtle text-fg"
                          : "border-border text-fg-muted hover:text-fg",
                      )}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              }
            >
              {(vaultFilter === "all" || vaultFilter === "ops") && (
                <div className="mb-6">
                  <h3 className="mb-2 text-sm font-medium text-fg-subtle">
                    Source-to-Skill (52)
                  </h3>
                  <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                    {packages
                      .filter((p) => (vaultFilter === "ops" ? p.operational : true))
                      .map((p) => (
                        <div
                          key={p.name}
                          className="rounded-lg border border-border bg-bg-elevated px-3 py-2"
                        >
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-sm font-medium">{p.name}</span>
                            <Badge tone={p.operational ? "pass" : "warn"}>
                              {p.operational ? "ops" : "docs-only"}
                            </Badge>
                          </div>
                          <div className="mt-1 text-xs text-fg-muted">{p.type}</div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {(vaultFilter === "all" || vaultFilter === "research") && (
                <div className="mb-6">
                  <h3 className="mb-2 text-sm font-medium text-fg-subtle">
                    Remaining 59 research skills
                  </h3>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {remaining.map((s) => (
                      <div
                        key={s.name}
                        className="rounded-lg border border-border bg-bg-elevated px-3 py-2"
                      >
                        <div className="text-sm font-medium">{s.name}</div>
                        <div className="mt-1 text-xs text-fg-muted">{s.description}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {(vaultFilter === "all" || vaultFilter === "restricted") && (
                <div>
                  <h3 className="mb-2 text-sm font-medium text-fg-subtle">
                    Restricted (catalog only)
                  </h3>
                  <ul className="space-y-2">
                    {restricted.map((r) => (
                      <li
                        key={r.name}
                        className="rounded-lg border border-border bg-bg-elevated px-3 py-2 text-sm"
                      >
                        <span className="font-medium">{r.name}</span>
                        <span className="text-fg-muted"> — {r.reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Section>

            {(vault.extractedSkills?.length ?? 0) > 0 && (
              <Section
                title="Extracted SKILL.md packs"
                description="Skills unpacked from Drive zips (superpowers, game-dev, tool-use, orchestration, plugins)."
              >
                <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                  {(vault.extractedSkills as Array<{
                    name: string;
                    description: string;
                    pack: string;
                    operational: boolean;
                  }>).map((s) => (
                    <div key={`${s.pack}-${s.name}`} className="rounded-lg border border-border bg-bg-elevated px-3 py-2">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-medium">{s.name}</span>
                        <Badge tone={s.operational ? "pass" : "warn"}>
                          {s.operational ? "ops" : "docs"}
                        </Badge>
                      </div>
                      <div className="mt-1 text-xs text-fg-subtle">{s.pack}</div>
                      <div className="mt-1 line-clamp-2 text-xs text-fg-muted">{s.description}</div>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {(vault.openclawCatalog?.length ?? 0) > 0 && (
              <Section
                title="OpenClaw skill catalog (indexed)"
                description={`Category index from awesome-openclaw-skills (${vault.stats?.openclawCatalogCount ?? 0} listed; showing first ${vault.openclawCatalog.length}).`}
              >
                <div className="mb-3 flex flex-wrap gap-1.5">
                  {Array.from(new Set((vault.openclawCatalog as Array<{ category: string }>).map((x) => x.category)))
                    .slice(0, 24)
                    .map((c) => (
                      <Badge key={c} tone="neutral">{c}</Badge>
                    ))}
                </div>
                <div className="max-h-96 overflow-auto rounded-xl border border-border">
                  <table className="w-full text-left text-sm">
                    <thead className="sticky top-0 bg-bg-elevated text-fg-subtle">
                      <tr>
                        <th className="px-3 py-2 font-medium">Skill</th>
                        <th className="px-3 py-2 font-medium">Category</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(vault.openclawCatalog as Array<{ name: string; category: string; description?: string }>)
                        .slice(0, 200)
                        .map((s, i) => (
                          <tr key={`${s.name}-${i}`} className="border-t border-border">
                            <td className="px-3 py-2">
                              <div className="font-medium">{s.name}</div>
                              {s.description ? (
                                <div className="line-clamp-1 text-xs text-fg-muted">{s.description}</div>
                              ) : null}
                            </td>
                            <td className="px-3 py-2 text-xs text-fg-muted">{s.category}</td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </Section>
            )}

            <Section title="Drive folders & artifacts" description="High-level inventory of the connected vault structure.">
              <div className="grid gap-3 lg:grid-cols-2">
                <div className="rounded-xl border border-border bg-bg-elevated p-4">
                  <h3 className="text-sm font-medium">Folders</h3>
                  <ul className="mt-3 space-y-2">
                    {(vault.driveFolders ?? []).map((f) => (
                      <li key={f.name} className="flex items-start justify-between gap-3 text-sm">
                        <span className="font-medium">{f.name}</span>
                        <span className="text-right text-xs text-fg-muted">
                          {f.kind} · {f.notes}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="rounded-xl border border-border bg-bg-elevated p-4">
                  <h3 className="text-sm font-medium">Skill artifacts</h3>
                  <ul className="mt-3 space-y-2">
                    {(vault.skillArtifacts ?? []).map((a) => (
                      <li key={a.name} className="text-sm">
                        <span className="font-mono text-xs text-fg-subtle">{a.type}</span>{" "}
                        <span className="font-medium">{a.name}</span>
                        <div className="text-xs text-fg-muted">{a.role}</div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              {vault.autoresearch ? (
                <div className="mt-3 rounded-xl border border-border bg-bg-elevated p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-medium">{vault.autoresearch.name}</h3>
                    <Badge tone="neutral">{vault.autoresearch.license}</Badge>
                    <span className="text-xs text-fg-muted">{vault.autoresearch.author}</span>
                  </div>
                  <p className="mt-2 text-sm text-fg-muted">{vault.autoresearch.summary}</p>
                </div>
              ) : null}
            </Section>
          </>
        )}
      </main>

      <footer className="border-t border-border py-6 text-center text-xs text-fg-subtle">
        Clearance · SPDX normalize · notices · CI gate · vault distill · generated{" "}
        {new Date(ledger.generatedAt).toLocaleString()}
      </footer>
    </div>
  );
}
