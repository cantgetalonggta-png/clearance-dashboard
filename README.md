# Clearance — License & Skill Ledger

Production dashboard + compliance pipeline for open-source license enumeration, SPDX normalization, third-party notices, CI gates, and skill-vault distillation.

## Features

1. **SPDX catalog** + **GitHub popular licenses**
2. **Dependency scan** (pip-licenses / node license-checker)
3. **Aggressive SPDX normalization** of messy raw license strings
4. **THIRD-PARTY-NOTICES.txt** generation
5. **CI compliance gate** (allowlist + copyleft denylist)
6. **Vault distillation** of Drive skill packs (lawful / public only)
7. **Dashboard** — Gate · Dependencies · Catalog · Notices · Vault

## Quick start

```bash
npm install
npm run dev
```

Pipeline:

```bash
npm run license:all          # integrate + gate
npm run license:integrate    # normalize + notices + ledger/vault
npm run license:gate         # exit 0 pass / 1 fail
npm run secrets:sync:dry     # dry-run secret sync from .env
```

## Safety

- Secrets load only from local `.env` (see `.env.example`) — never hardcode keys
- Leaked prompts / credential material: catalog-only, never inlined
- Non-operational bypass claims: documentation-only

## Deploy

GitHub: https://github.com/cantgetalonggta-png/clearance-dashboard

Vercel: link this repo as a TanStack Start / Vite project (team deploy).

## Artifacts

- `artifacts/unified_licenses.json`
- `artifacts/THIRD-PARTY-NOTICES.txt`
- `src/data/ledger.json` / `src/data/vault.json`
- `.github/workflows/license-compliance.yml`
