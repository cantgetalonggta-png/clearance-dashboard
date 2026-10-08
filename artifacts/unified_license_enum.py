"""
UNIFIED LICENSE ENUMERATION SYSTEM
Multi‑Agent Pipeline for:
1. SPDX License Catalog
2. GitHub License API
3. Local Dependency License Scan (pip + node)
4. Unified License Synthesis

Agents:
- SPDXAgent: Loads full SPDX license list
- GitHubAgent: Queries GitHub License API
- DependencyAgent: Scans Python + Node dependencies
- SynthesizerAgent: Merges, deduplicates, normalizes

Output:
- Full list of all open‑source licenses available + used
"""

import requests
import subprocess
import json
import sys
from collections import defaultdict
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'compliance'))
try:
    from spdx_normalizer import SPDXNormalizer
except Exception:
    SPDXNormalizer = None

# -----------------------------
# SPDX LICENSE AGENT
# -----------------------------
class SPDXAgent:
    def run(self):
        url = "https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json"
        print("[SPDXAgent] Fetching SPDX license list...", file=sys.stderr)
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        licenses = [
            {
                "id": lic["licenseId"],
                "name": lic["name"],
                "osiApproved": lic.get("isOsiApproved", False)
            }
            for lic in data["licenses"]
        ]
        print(f"[SPDXAgent] Loaded {len(licenses)} licenses", file=sys.stderr)
        return {
            "source": "SPDX",
            "count": len(licenses),
            "licenses": licenses
        }

# -----------------------------
# GITHUB LICENSE AGENT
# -----------------------------
class GitHubAgent:
    def run(self):
        url = "https://api.github.com/licenses"
        print("[GitHubAgent] Querying GitHub Licenses API...", file=sys.stderr)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "Unified-License-Enum/1.0"}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        licenses = [
            {
                "id": lic["key"],
                "name": lic["name"],
                "spdx_id": lic.get("spdx_id")
            }
            for lic in data
        ]
        print(f"[GitHubAgent] Loaded {len(licenses)} licenses", file=sys.stderr)
        return {
            "source": "GitHub",
            "count": len(licenses),
            "licenses": licenses
        }

# -----------------------------
# DEPENDENCY LICENSE AGENT
# -----------------------------
class DependencyAgent:
    def run(self):
        results = {}

        # Python dependency licenses
        print("[DependencyAgent] Scanning Python packages with pip-licenses...", file=sys.stderr)
        try:
            py_output = subprocess.check_output(
                ["pip-licenses", "--format=json"], text=True, stderr=subprocess.DEVNULL
            )
            results["python"] = json.loads(py_output)
            print(f"[DependencyAgent] Found {len(results['python'])} Python packages", file=sys.stderr)
        except Exception as e:
            print(f"[DependencyAgent] Python scan failed: {e}", file=sys.stderr)
            results["python"] = []

        # Node dependency licenses
        print("[DependencyAgent] Scanning Node packages with license-checker...", file=sys.stderr)
        try:
            # Run from /workspace/artifacts; if no package.json, create a minimal one or skip
            node_output = subprocess.check_output(
                ["npx", "--yes", "license-checker", "--json", "--production"],
                text=True, stderr=subprocess.PIPE, cwd="/workspace/artifacts", timeout=120
            )
            results["node"] = json.loads(node_output)
            print(f"[DependencyAgent] Found {len(results['node'])} Node packages", file=sys.stderr)
        except Exception as e:
            print(f"[DependencyAgent] Node scan failed/empty: {e}", file=sys.stderr)
            results["node"] = {}

        return {
            "source": "Dependencies",
            "licenses": results
        }

# -----------------------------
# SYNTHESIZER AGENT
# -----------------------------
class SynthesizerAgent:
    def run(self, spdx, github, deps):
        print("[SynthesizerAgent] Merging and normalizing...", file=sys.stderr)

        # Collect unique SPDX-like IDs
        all_ids = set()
        id_to_info = {}

        for lic in spdx["licenses"]:
            lid = lic["id"]
            all_ids.add(lid)
            id_to_info[lid] = {
                "id": lid,
                "name": lic["name"],
                "osiApproved": lic.get("osiApproved", False),
                "sources": ["SPDX"]
            }

        for lic in github["licenses"]:
            lid = lic.get("spdx_id") or lic["id"]
            if lid and lid != "NOASSERTION":
                if lid in id_to_info:
                    if "GitHub" not in id_to_info[lid]["sources"]:
                        id_to_info[lid]["sources"].append("GitHub")
                else:
                    all_ids.add(lid)
                    id_to_info[lid] = {
                        "id": lid,
                        "name": lic["name"],
                        "osiApproved": None,
                        "sources": ["GitHub"]
                    }

        # Extract used licenses from dependencies
        used_licenses = defaultdict(list)

        for pkg in deps["licenses"].get("python", []):
            lic_str = pkg.get("License", "UNKNOWN")
            name = pkg.get("Name", "unknown")
            version = pkg.get("Version", "")
            used_licenses[lic_str].append(f"python:{name}=={version}")

        for pkg_name, info in deps["licenses"].get("node", {}).items():
            lic_str = info.get("licenses", "UNKNOWN")
            if isinstance(lic_str, list):
                lic_str = " OR ".join(lic_str)
            used_licenses[str(lic_str)].append(f"node:{pkg_name}")

        # Aggressive SPDX normalization via SPDXNormalizer when available
        normalizer = SPDXNormalizer([x["id"] for x in spdx["licenses"]]) if SPDXNormalizer else None
        used_normalized = {}
        for raw, packages in used_licenses.items():
            if normalizer:
                key = normalizer.normalize(raw)
            else:
                key = raw.split(";")[0].strip() if raw else "UNKNOWN"
            used_normalized.setdefault(key, []).extend(packages)

        synthesized_deps = []
        for pkg in deps["licenses"].get("python", []):
            raw = pkg.get("License", "UNKNOWN")
            spdx_id = normalizer.normalize(raw) if normalizer else raw
            synthesized_deps.append({
                "name": pkg.get("Name"),
                "version": pkg.get("Version"),
                "raw_license": raw,
                "spdx_license": spdx_id,
                "home_page": pkg.get("URL", ""),
                "ecosystem": "python",
            })
            pkg["spdx_license"] = spdx_id

        unified = {
            "summary": {
                "spdx_total": spdx["count"],
                "github_total": github["count"],
                "unique_catalog_ids": len(id_to_info),
                "python_packages_scanned": len(deps["licenses"].get("python", [])),
                "node_packages_scanned": len(deps["licenses"].get("node", {})),
                "distinct_used_license_strings": len(used_normalized),
                "distinct_spdx_normalized": len(set(d["spdx_license"] for d in synthesized_deps)),
            },
            "catalog": {
                "spdx": spdx["licenses"],
                "github": github["licenses"],
                "merged_by_id": sorted(id_to_info.values(), key=lambda x: x["id"])
            },
            "dependencies": {
                "python": deps["licenses"].get("python", []),
                "node": deps["licenses"].get("node", {}),
                "used_licenses": {k: v for k, v in sorted(used_normalized.items())}
            },
            "synthesized_deps": synthesized_deps,
            "osi_approved_count": sum(1 for v in id_to_info.values() if v.get("osiApproved") is True)
        }
        print("[SynthesizerAgent] Done.", file=sys.stderr)
        return unified

# -----------------------------
# RUN ALL AGENTS
# -----------------------------
if __name__ == "__main__":
    try:
        spdx = SPDXAgent().run()
        github = GitHubAgent().run()
        deps = DependencyAgent().run()
        final = SynthesizerAgent().run(spdx, github, deps)

        out_path = "/workspace/artifacts/unified_licenses.json"
        with open(out_path, "w") as f:
            json.dump(final, f, indent=2)
        print(json.dumps(final["summary"], indent=2))
        print(f"\nFull output written to {out_path}", file=sys.stderr)
        # Also print used licenses nicely
        print("\n=== USED LICENSES FROM DEPENDENCIES ===")
        for lic, pkgs in final["dependencies"]["used_licenses"].items():
            print(f"\n{lic}:")
            for p in pkgs[:10]:
                print(f"  - {p}")
            if len(pkgs) > 10:
                print(f"  ... and {len(pkgs)-10} more")
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
