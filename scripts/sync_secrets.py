#!/usr/bin/env python3
"""
sync_secrets.py — push secrets from a local .env to GitHub Actions / Vercel.

SAFETY:
- Never hardcode secret values in this file.
- Only syncs keys listed in SECRETS_ALLOWLIST that exist in the local .env.
- Does not print secret values.
- Requires gh auth and vercel auth (or VERCEL_TOKEN).

Usage:
  cp .env.example .env   # fill values
  python scripts/sync_secrets.py
  python scripts/sync_secrets.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

# Names only — values come from .env
SECRETS_ALLOWLIST = [
    "GROK_API_KEY",
    "DATABASE_URL",
    "CLEARANCE_VAULT_PASS",
    "VERCEL_TOKEN",
]

GITHUB_REPO = os.getenv("GITHUB_REPO", "")  # owner/repo
VERCEL_PROJECT = os.getenv("VERCEL_PROJECT", "clearance-dashboard")
VERCEL_SCOPE = os.getenv("VERCEL_SCOPE", "")  # team slug/id optional


def load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            out[key] = val
    return out


def which(cmd: str) -> bool:
    return subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


def run(cmd: list[str], input_text: str | None = None, dry: bool = False) -> int:
    if dry:
        print(f"  [dry-run] {' '.join(cmd)}  (stdin={'yes' if input_text else 'no'})")
        return 0
    proc = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip().splitlines()
        print(f"  [!] failed: {err[-1] if err else proc.returncode}")
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--github-repo", default=GITHUB_REPO)
    parser.add_argument("--vercel-project", default=VERCEL_PROJECT)
    args = parser.parse_args()

    env = load_dotenv(ENV_PATH)
    # also allow process env for CI
    for k in SECRETS_ALLOWLIST:
        if k not in env and os.getenv(k):
            env[k] = os.environ[k]

    selected = {k: env[k] for k in SECRETS_ALLOWLIST if env.get(k)}
    if not selected:
        print(f"[!] No secrets found. Create {ENV_PATH} with allowlisted keys and re-run.")
        print(f"    Allowlist: {', '.join(SECRETS_ALLOWLIST)}")
        return 1

    print(f"[*] Will sync {len(selected)} keys (names only): {', '.join(selected)}")
    if not which("gh"):
        print("[!] gh CLI missing")
        return 1
    if not which("vercel"):
        print("[!] vercel CLI missing")
        return 1

    repo = args.github_repo
    if not repo:
        # try gh repo from current dir
        r = subprocess.run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], capture_output=True, text=True)
        repo = (r.stdout or "").strip()
    if not repo:
        print("[!] Set GITHUB_REPO=owner/repo or --github-repo")
        return 1

    print(f"\n[*] GitHub Actions secrets → {repo}")
    for key, value in selected.items():
        code = run(["gh", "secret", "set", key, "-R", repo], input_text=value, dry=args.dry_run)
        print(f"  {'✓' if code == 0 else '!'} {key}")

    print(f"\n[*] Vercel env (production/preview/development) → {args.vercel_project}")
    for key, value in selected.items():
        # skip VERCEL_TOKEN itself into Vercel env usually
        if key == "VERCEL_TOKEN":
            continue
        for target in ("production", "preview", "development"):
            # remove if exists (best effort)
            run(["vercel", "env", "rm", key, target, "-y"], dry=args.dry_run)
            code = run(["vercel", "env", "add", key, target], input_text=value + "\n", dry=args.dry_run)
            if code == 0:
                print(f"  ✓ {key} ({target})")
                break
        else:
            print(f"  ! {key} (vercel add failed for all targets)")

    print("\n[✓] Sync finished. Secret values were never printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
