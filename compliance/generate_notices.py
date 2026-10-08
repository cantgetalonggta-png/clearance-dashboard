#!/usr/bin/env python3
"""Generate THIRD-PARTY-NOTICES.txt from unified_licenses.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


HEADER = """========================================================================
THIRD-PARTY SOFTWARE NOTICES AND INFORMATION
========================================================================

This product contains third-party software components licensed under open-source
and permissive licenses. The relevant software components, copyright holders,
and license terms are acknowledged below.

------------------------------------------------------------------------
SUMMARY OF THIRD-PARTY DEPENDENCIES
------------------------------------------------------------------------
{summary_table}

========================================================================
DETAILED COMPONENT NOTICES & LICENSES
========================================================================
"""

COMPONENT = """
------------------------------------------------------------------------
Package: {package_name}
Version: {version}
License: {license_id}
Source: {ecosystem}
{repository_info}
------------------------------------------------------------------------
{license_text}

"""


def flatten_dependencies(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(data.get("synthesized_deps"), list) and data["synthesized_deps"]:
        return data["synthesized_deps"]
    deps = data.get("dependencies")
    out: List[Dict[str, Any]] = []
    if isinstance(deps, list):
        return deps
    if isinstance(deps, dict):
        for pkg in deps.get("python", []) or []:
            out.append({
                "name": pkg.get("Name") or pkg.get("name"),
                "version": pkg.get("Version") or pkg.get("version"),
                "raw_license": pkg.get("License") or pkg.get("license") or "UNKNOWN",
                "spdx_license": pkg.get("spdx_license") or pkg.get("License") or "UNKNOWN",
                "home_page": pkg.get("URL") or pkg.get("home_page") or "",
                "ecosystem": "python",
            })
        node = deps.get("node") or {}
        if isinstance(node, dict):
            for pkg_name, info in node.items():
                lic = info.get("licenses", "UNKNOWN")
                if isinstance(lic, list):
                    lic = " OR ".join(str(x) for x in lic)
                out.append({
                    "name": pkg_name,
                    "version": info.get("version") or "N/A",
                    "raw_license": str(lic),
                    "spdx_license": str(lic),
                    "home_page": info.get("repository") or info.get("url") or "",
                    "ecosystem": "node",
                })
    return out


def format_summary(dependencies: List[Dict[str, Any]]) -> str:
    lines = [
        f"{'Package':<32} | {'Version':<12} | {'SPDX License':<28}",
        "-" * 78,
    ]
    for dep in dependencies:
        pkg = str(dep.get("name") or dep.get("Name") or "Unknown")[:32]
        ver = str(dep.get("version") or dep.get("Version") or "N/A")[:12]
        lic = str(dep.get("spdx_license") or dep.get("License") or dep.get("license") or "Unknown")[:28]
        lines.append(f"{pkg:<32} | {ver:<12} | {lic:<28}")
    return "\n".join(lines)


def generate_notices(json_path: Path, output_path: Path) -> int:
    if not json_path.exists():
        print(f"Error: {json_path} not found.", file=sys.stderr)
        return 1
    data = json.loads(json_path.read_text(encoding="utf-8"))
    dependencies = flatten_dependencies(data)
    if not dependencies:
        print("Warning: No dependencies found in JSON file.", file=sys.stderr)
        return 1
    dependencies = sorted(dependencies, key=lambda x: str(x.get("name") or x.get("Name") or "").lower())
    text = HEADER.format(summary_table=format_summary(dependencies))
    for dep in dependencies:
        name = dep.get("name") or dep.get("Name") or "Unknown"
        version = dep.get("version") or dep.get("Version") or "N/A"
        license_id = dep.get("spdx_license") or dep.get("License") or dep.get("license") or "Unknown"
        repo = dep.get("home_page") or dep.get("URL") or dep.get("repository") or ""
        repo_info = f"Repository / URL: {repo}" if repo else ""
        ecosystem = dep.get("ecosystem") or "unknown"
        license_text = dep.get("license_text") or (
            f"This component is distributed under the {license_id} license. "
            f"Full license text is available from the package author / SPDX registry for {license_id}."
        )
        text += COMPONENT.format(
            package_name=name,
            version=version,
            license_id=license_id,
            ecosystem=ecosystem,
            repository_info=repo_info,
            license_text=str(license_text).strip(),
        )
    output_path.write_text(text.strip() + "\n", encoding="utf-8")
    print(f"Successfully generated {output_path} ({len(dependencies)} packages).")
    return 0


if __name__ == "__main__":
    candidates = [
        Path("/workspace/artifacts/unified_licenses.json"),
        Path("artifacts/unified_licenses.json"),
        Path("unified_licenses.json"),
    ]
    input_file = next((p for p in candidates if p.exists()), candidates[0])
    output_file = Path("/workspace/artifacts/THIRD-PARTY-NOTICES.txt")
    if Path("public").exists():
        # also write into app public when run from workspace root
        pass
    sys.exit(generate_notices(input_file, output_file))
