#!/usr/bin/env python3
"""Post-process unified_licenses.json: normalize, notices, compliance report, dashboard data."""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spdx_normalizer import SPDXNormalizer  # noqa: E402
from generate_notices import generate_notices  # noqa: E402
from check_license_compliance import evaluate, expression_allowed  # noqa: E402

ROOT = Path("/workspace")
ART = ROOT / "artifacts"
JSON_PATH = ART / "unified_licenses.json"
NOTICES_PATH = ART / "THIRD-PARTY-NOTICES.txt"
PUBLIC_NOTICES = ROOT / "public" / "THIRD-PARTY-NOTICES.txt"
LEDGER_PATH = ROOT / "src" / "data" / "ledger.json"
VAULT_PATH = ROOT / "src" / "data" / "vault.json"
REPORT_PATH = ART / "compliance_report.json"


def synthesize(data: dict) -> dict:
    valid = [x.get("id") for x in data.get("catalog", {}).get("spdx", []) if x.get("id")]
    normalizer = SPDXNormalizer(valid_spdx_ids=valid)
    synthesized = []
    deps = data.get("dependencies", {})
    for pkg in deps.get("python", []) or []:
        raw = pkg.get("License") or pkg.get("license") or "UNKNOWN"
        spdx = normalizer.normalize(raw)
        synthesized.append({
            "name": pkg.get("Name") or pkg.get("name"),
            "version": pkg.get("Version") or pkg.get("version") or "N/A",
            "raw_license": raw,
            "spdx_license": spdx,
            "home_page": pkg.get("URL") or pkg.get("home_page") or "",
            "ecosystem": "python",
            "allowed": expression_allowed(spdx),
        })
        pkg["spdx_license"] = spdx
    node = deps.get("node") or {}
    if isinstance(node, dict):
        for name, info in node.items():
            raw = info.get("licenses", "UNKNOWN")
            if isinstance(raw, list):
                raw = " OR ".join(str(x) for x in raw)
            spdx = normalizer.normalize(str(raw))
            synthesized.append({
                "name": name,
                "version": info.get("version") or "N/A",
                "raw_license": str(raw),
                "spdx_license": spdx,
                "home_page": info.get("repository") or info.get("url") or "",
                "ecosystem": "node",
                "allowed": expression_allowed(spdx),
            })
    synthesized.sort(key=lambda x: (x.get("name") or "").lower())
    rollup = Counter(d["spdx_license"] for d in synthesized)
    raw_to_spdx = defaultdict(list)
    for d in synthesized:
        raw_to_spdx[d["raw_license"]].append(d["spdx_license"])
    data["synthesized_deps"] = synthesized
    data["license_rollup"] = dict(sorted(rollup.items(), key=lambda x: (-x[1], x[0])))
    data["distinct_spdx_count"] = len(rollup)
    data["normalization_map"] = {
        raw: sorted(set(vals))
        for raw, vals in sorted(raw_to_spdx.items(), key=lambda x: x[0].lower())
    }
    data["summary"] = data.get("summary") or {}
    data["summary"]["synthesized_packages"] = len(synthesized)
    data["summary"]["distinct_spdx_normalized"] = len(rollup)
    data["summary"]["normalized_at"] = datetime.now(timezone.utc).isoformat()
    return data


def build_ledger(data: dict) -> dict:
    synth = data.get("synthesized_deps") or []
    allowed = [d for d in synth if d.get("allowed")]
    blocked = [d for d in synth if not d.get("allowed")]
    rollup = data.get("license_rollup") or {}
    github = data.get("catalog", {}).get("github") or []
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            **(data.get("summary") or {}),
            "osi_approved_count": data.get("osi_approved_count"),
            "allowed_packages": len(allowed),
            "blocked_packages": len(blocked),
            "gate_passed": len(blocked) == 0,
        },
        "licenseRollup": [{"id": k, "count": v} for k, v in rollup.items()],
        "dependencies": synth,
        "normalizationMap": [
            {"raw": k, "spdx": v} for k, v in (data.get("normalization_map") or {}).items()
        ],
        "githubPopular": github,
        "spdxSample": (data.get("catalog", {}).get("merged_by_id") or [])[:80],
        "spdxTotal": (data.get("summary") or {}).get("spdx_total", 0),
    }


def build_vault() -> dict:
    vault_dir = ART / "vault"
    remaining = []
    rem_path = vault_dir / "Remaining_59_Skills.md"
    if rem_path.exists():
        for line in rem_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and line[0].isdigit() and ". [" in line:
                # 1. [name](path) — desc
                try:
                    num, rest = line.split(". ", 1)
                    name = rest.split("[", 1)[1].split("]", 1)[0]
                    desc = rest.split("—", 1)[1].strip() if "—" in rest else rest
                    remaining.append({"id": int(num), "name": name, "description": desc, "family": "remaining-59"})
                except Exception:
                    continue

    packages = []
    man_path = vault_dir / "Source-to-Skill_Master_Manifest.md"
    non_op = set()
    if man_path.exists():
        for line in man_path.read_text(encoding="utf-8").splitlines():
            if "Non-operational" in line or "documentation-only" in line.lower():
                # track non-op package names from inventory rows later
                pass
            if line.startswith("|") and "packages/" in line:
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) >= 6 and parts[0].isdigit():
                    pkg_cell = parts[1]
                    name = pkg_cell.split("`")[1] if "`" in pkg_cell else pkg_cell
                    term = parts[2]
                    ptype = parts[4]
                    notes = parts[5] if len(parts) > 5 else ""
                    operational = "Non-operational" not in notes and "non-operational" not in notes.lower()
                    if not operational:
                        non_op.add(name)
                    packages.append({
                        "id": int(parts[0]),
                        "name": name,
                        "terminology": term,
                        "type": ptype,
                        "operational": operational,
                        "family": "source-to-skill-52",
                    })

    index_items = []
    idx = vault_dir / "vault_master_index.md.txt"
    if idx.exists():
        for line in idx.read_text(encoding="utf-8").splitlines():
            line = line.strip().lstrip("- ")
            if line and not line.startswith("#") and not line.startswith("Policy"):
                index_items.append(line)

    # Drive inventory distilled (from prior listing — no binary dumps / no prompt-leak bodies)
    drive_folders = [
        {"name": "openclaw-main", "kind": "agent-runtime", "notes": "Docker compose + task routing"},
        {"name": "rtk-develop", "kind": "tooling", "notes": "RTK filter development tree"},
        {"name": "VoiceStudio-main", "kind": "voice", "notes": "VoiceStudio / OmniVoice backend"},
        {"name": "doombots", "kind": "assets", "notes": "Doombots font pack + license"},
        {"name": "ReTerminal", "kind": "runtime", "notes": "proot / alpine terminal runtime"},
        {"name": "Slack", "kind": "archive", "notes": "Slack export archive"},
        {"name": "canada_2", "kind": "dataset", "notes": "Dataset folder"},
        {"name": "DataSet 12", "kind": "dataset", "notes": "Dataset folder"},
        {"name": "oxproxion", "kind": "empty", "notes": "Empty placeholder"},
        {"name": "rapid-response-font", "kind": "assets", "notes": "Font assets"},
    ]
    drive_skill_artifacts = [
        {"name": "skill_seekers-3.6.0", "type": "wheel", "role": "Source-to-skill packaging CLI"},
        {"name": "awesome-agent-skills-main.zip", "type": "zip", "role": "Agent skill catalog"},
        {"name": "awesome-openclaw-skills-main.zip", "type": "zip", "role": "OpenClaw skills"},
        {"name": "claude-plugins-official-main.zip", "type": "zip", "role": "Claude plugin marketplace"},
        {"name": "skills-main.zip", "type": "zip", "role": "Skill pack archive"},
        {"name": "superpowers-main.zip", "type": "zip", "role": "Superpowers skill pack"},
        {"name": "plugin-marketplace-main.zip", "type": "zip", "role": "Plugin marketplace"},
        {"name": "agent-orchestration.zip", "type": "zip", "role": "Orchestration skill"},
        {"name": "game-dev.zip", "type": "zip", "role": "Game-dev skill"},
        {"name": "tool-use.zip", "type": "zip", "role": "Tool-use skill"},
        {"name": "api_references.md", "type": "md", "role": "QQ Channel API reference"},
        {"name": "ADVANCED_SETUP.md", "type": "md", "role": "Dify advanced deployment"},
        {"name": "Agents SDK.txt", "type": "txt", "role": "OpenAI Agents SDK guide"},
        {"name": "SKILL.md", "type": "md", "role": "Autoresearch skill (MIT)"},
        {"name": "Source-to-Skill_Master_Manifest.md", "type": "md", "role": "52 package inventory"},
        {"name": "Remaining_59_Skills.md", "type": "md", "role": "59 research skills"},
    ]
    restricted = [
        {"name": "system_prompts_leaks references", "reason": "Third-party leaked prompts — cataloged, not inlined"},
        {"name": "Explore Leaked Keys - APIRadar.docx", "reason": "Potential credential exposure — not loaded"},
        {"name": "Gary Simel.vcf", "reason": "Personal contact data — not inlined"},
        {"name": "Non-operational bypass claims", "reason": "Documented as non-executable in source-to-skill boundary"},
    ]
    themes = [
        {"title": "License Compliance Stack", "body": "SPDX catalog, GitHub popular licenses, dependency scan, SPDX normalization, notices generation, CI allowlist gate."},
        {"title": "Agent Skill Ontology", "body": "52 source-to-skill packages + 59 research skills + autoresearch two-loop architecture."},
        {"title": "Runtime Tooling", "body": "OpenClaw, VoiceStudio, RTK, ReTerminal proot, Skill Seekers wheel."},
        {"title": "Public-record OSINT Policy", "body": "Vault master index restricted to public-record only; no private API bypass or unauthorized scanning playbooks."},
        {"title": "Deployment Patterns", "body": "Dify advanced setup: Grafana metrics, Helm/K8s, Terraform, AWS CDK references."},
        {"title": "API Surfaces", "body": "QQ Channel API guilds/channels/members/announces; OpenAI Agents SDK sandboxes and handoffs."},
    ]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFolder": ".md bot",
        "sourceUrl": "https://drive.google.com/drive/folders/1T2vM2apG4c77OA0XGBPUrkZ-xgsKj7oo",
        "stats": {
            "sourceToSkillPackages": len(packages),
            "operationalPackages": sum(1 for p in packages if p.get("operational")),
            "remainingSkills": len(remaining),
            "driveFolders": len(drive_folders),
            "skillArtifacts": len(drive_skill_artifacts),
            "restrictedItems": len(restricted),
            "lawfulIndexItems": len(index_items),
        },
        "themes": themes,
        "sourceToSkill": packages,
        "remainingSkills": remaining,
        "lawfulIndex": index_items,
        "driveFolders": drive_folders,
        "skillArtifacts": drive_skill_artifacts,
        "restricted": restricted,
        "autoresearch": {
            "name": "autoresearch",
            "license": "MIT",
            "author": "Orchestra Research",
            "summary": "Two-loop autonomous research orchestration: inner experiment loop + outer synthesis loop with research-state.yaml continuity.",
        },
    }


def main() -> int:
    if not JSON_PATH.exists():
        print(f"Missing {JSON_PATH}", file=sys.stderr)
        return 1
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    data = synthesize(data)
    JSON_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Updated {JSON_PATH}")

    generate_notices(JSON_PATH, NOTICES_PATH)
    PUBLIC_NOTICES.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_NOTICES.write_text(NOTICES_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Copied notices to {PUBLIC_NOTICES}")

    # compliance report without sys.exit
    deps = data["synthesized_deps"]
    blocked = [d for d in deps if not d.get("allowed")]
    report = {
        "passed": len(blocked) == 0,
        "total": len(deps),
        "blocked": blocked,
        "evaluatedAt": datetime.now(timezone.utc).isoformat(),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Compliance report: passed={report['passed']} blocked={len(blocked)}")

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    ledger = build_ledger(data)
    LEDGER_PATH.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    vault = build_vault()
    VAULT_PATH.write_text(json.dumps(vault, indent=2), encoding="utf-8")
    print(f"Wrote {LEDGER_PATH} and {VAULT_PATH}")

    # distilled skill encyclopedia
    dist = ART / "vault" / "distilled" / "SKILL_ENCYCLOPEDIA.md"
    dist.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Distilled Skill Encyclopedia",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Themes",
        "",
    ]
    for t in vault["themes"]:
        lines.append(f"### {t['title']}")
        lines.append(t["body"])
        lines.append("")
    lines.append("## Source-to-Skill Packages (operational)")
    lines.append("")
    for p in vault["sourceToSkill"]:
        if p.get("operational"):
            lines.append(f"- **{p['name']}** ({p['type']}): {p['terminology']}")
    lines.append("")
    lines.append("## Remaining 59 Skills")
    lines.append("")
    for s in vault["remainingSkills"]:
        lines.append(f"- **{s['name']}**: {s['description']}")
    lines.append("")
    lines.append("## Restricted (catalog only)")
    lines.append("")
    for r in vault["restricted"]:
        lines.append(f"- {r['name']} — {r['reason']}")
    dist.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {dist}")
    return 0 if report["passed"] else 0  # don't fail integrate; gate is separate


if __name__ == "__main__":
    raise SystemExit(main())
