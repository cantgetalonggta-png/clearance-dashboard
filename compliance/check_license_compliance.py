#!/usr/bin/env python3
"""CI license compliance gate. Exit 0 pass / 1 fail."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ALLOWED_LICENSES: Set[str] = {
    "MIT", "MIT-0", "MIT-CMU", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause",
    "BSL-1.0", "CC0-1.0", "ISC", "PSF-2.0", "Unlicense", "MPL-2.0",
    "Apache-2.0 OR BSD-3-Clause", "Apache-2.0 OR BSD-2-Clause",
    "MIT OR Apache-2.0", "BSD-3-Clause OR Apache-2.0",
}

DENIED_LICENSES: Set[str] = {
    "GPL-1.0-only", "GPL-1.0-or-later",
    "GPL-2.0-only", "GPL-2.0-or-later",
    "GPL-3.0-only", "GPL-3.0-or-later",
    "AGPL-1.0-only", "AGPL-1.0-or-later",
    "AGPL-3.0-only", "AGPL-3.0-or-later",
    "SSPL-1.0",
}


def load_deps(json_path: Path) -> List[Dict[str, Any]]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
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
                "spdx_license": pkg.get("spdx_license") or pkg.get("License") or "UNKNOWN",
                "raw_license": pkg.get("License") or "UNKNOWN",
            })
    return out


def expression_allowed(expr: str) -> bool:
    expr = (expr or "UNKNOWN").strip()
    if expr in DENIED_LICENSES:
        return False
    if expr in ALLOWED_LICENSES:
        return True
    # Atom-wise: OR → any allowed; AND → all allowed; deny if any atom denied
    if " OR " in expr:
        atoms = [a.strip() for a in expr.split(" OR ")]
        if any(a in DENIED_LICENSES for a in atoms):
            return False
        return any(a in ALLOWED_LICENSES for a in atoms)
    if " AND " in expr:
        atoms = [a.strip() for a in expr.split(" AND ")]
        if any(a in DENIED_LICENSES for a in atoms):
            return False
        return all(a in ALLOWED_LICENSES for a in atoms)
    return False


def evaluate(dependencies: List[Dict[str, Any]]) -> bool:
    violations = []
    denied = []
    print(f"Evaluating {len(dependencies)} package dependencies...\n")
    for dep in dependencies:
        name = dep.get("name") or dep.get("Name") or "Unknown"
        version = dep.get("version") or dep.get("Version") or "N/A"
        license_id = (
            dep.get("spdx_license")
            or dep.get("license")
            or dep.get("License")
            or "UNKNOWN"
        ).strip()
        info = {"package": name, "version": version, "license": license_id}
        atoms = re.split(r"\s+OR\s+|\s+AND\s+", license_id)
        if any(a.strip() in DENIED_LICENSES for a in atoms) or license_id in DENIED_LICENSES:
            denied.append(info)
        elif not expression_allowed(license_id):
            violations.append(info)

    if denied:
        print("BLOCKED LICENSES DETECTED (Copyleft / Restricted):")
        for item in denied:
            print(f"  - {item['package']} v{item['version']} — {item['license']}")
        print()
    if violations:
        print("UNAPPROVED LICENSES DETECTED (Not in Allowlist):")
        for item in violations:
            print(f"  - {item['package']} v{item['version']} — {item['license']}")
        print()
    if denied or violations:
        print(f"Compliance Gate Failed: {len(denied)+len(violations)} violation(s).")
        return False
    print("License Compliance Gate Passed: All dependencies match allowlist.")
    return True


if __name__ == "__main__":
    candidates = [
        Path("/workspace/artifacts/unified_licenses.json"),
        Path("artifacts/unified_licenses.json"),
        Path("unified_licenses.json"),
    ]
    path = next((p for p in candidates if p.exists()), None)
    if not path:
        print("Error: unified_licenses.json not found", file=sys.stderr)
        sys.exit(1)
    ok = evaluate(load_deps(path))
    sys.exit(0 if ok else 1)
