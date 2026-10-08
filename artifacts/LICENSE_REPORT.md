# Unified License Enumeration Report

**Generated:** 2026-10-08 04:46 UTC

Multi-agent pipeline: **SPDXAgent** → **GitHubAgent** → **DependencyAgent** → **SynthesizerAgent**

## Summary

| Metric | Value |
|--------|------:|
| Spdx Total | 740 |
| Github Total | 13 |
| Unique Catalog Ids | 740 |
| Python Packages Scanned | 45 |
| Node Packages Scanned | 0 |
| Distinct Used License Strings | 15 |
| OSI-approved in SPDX catalog | 154 |

## 1. GitHub License API (popular licenses)

| Key | SPDX ID | Name |
|-----|---------|------|
| `agpl-3.0` | `AGPL-3.0` | GNU Affero General Public License v3.0 |
| `apache-2.0` | `Apache-2.0` | Apache License 2.0 |
| `bsd-2-clause` | `BSD-2-Clause` | BSD 2-Clause "Simplified" License |
| `bsd-3-clause` | `BSD-3-Clause` | BSD 3-Clause "New" or "Revised" License |
| `bsl-1.0` | `BSL-1.0` | Boost Software License 1.0 |
| `cc0-1.0` | `CC0-1.0` | Creative Commons Zero v1.0 Universal |
| `epl-2.0` | `EPL-2.0` | Eclipse Public License 2.0 |
| `gpl-2.0` | `GPL-2.0` | GNU General Public License v2.0 |
| `gpl-3.0` | `GPL-3.0` | GNU General Public License v3.0 |
| `lgpl-2.1` | `LGPL-2.1` | GNU Lesser General Public License v2.1 |
| `mit` | `MIT` | MIT License |
| `mpl-2.0` | `MPL-2.0` | Mozilla Public License 2.0 |
| `unlicense` | `Unlicense` | The Unlicense |

## 2. Local Dependency Licenses (Python)

Scanned **45** packages via `pip-licenses`.

| Package | Version | License |
|---------|---------|---------|
| beautifulsoup4 | 4.15.0 | MIT License |
| certifi | 2026.7.22 | Mozilla Public License 2.0 (MPL 2.0) |
| cffi | 2.1.1 | MIT-0 |
| charset-normalizer | 3.5.1 | MIT |
| click | 8.5.0 | BSD-3-Clause |
| coloredlogs | 15.0.1 | MIT License |
| cryptography | 50.0.1 | Apache-2.0 OR BSD-3-Clause |
| defusedxml | 0.7.1 | Python Software Foundation License |
| et_xmlfile | 2.0.0 | MIT License |
| flatbuffers | 25.12.19 | Apache Software License |
| humanfriendly | 10.0 | MIT License |
| idna | 3.20 | BSD-3-Clause |
| lxml | 6.1.1 | BSD-3-Clause |
| magika | 0.6.3 | Apache Software License |
| markdownify | 1.2.3 | MIT License |
| markitdown | 0.1.7 | MIT |
| mpmath | 1.3.0 | BSD License |
| numpy | 2.2.6 | BSD License |
| onnxruntime | 1.23.2 | MIT License |
| openpyxl | 3.1.5 | MIT License |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pandas | 2.3.3 | BSD License |
| pdf2image | 1.17.0 | MIT License |
| pdfminer.six | 20260107 | MIT |
| pdfplumber | 0.11.10 | MIT License |
| pillow | 12.3.0 | MIT-CMU |
| protobuf | 7.36.2 | 3-Clause BSD License |
| pycparser | 3.0 | BSD-3-Clause |
| pypdf | 6.14.2 | BSD-3-Clause |
| pypdfium2 | 5.12.1 | BSD-3-Clause, Apache-2.0, dependency licenses |
| pytesseract | 0.3.13 | Apache Software License |
| python-dateutil | 2.9.0.post0 | Apache Software License; BSD License |
| python-docx | 1.2.0 | MIT License |
| python-dotenv | 1.2.3 | BSD-3-Clause |
| python-pptx | 1.0.2 | MIT License |
| pytz | 2026.4 | MIT License |
| reportlab | 5.0.0 | BSD License |
| requests | 2.34.2 | Apache Software License |
| six | 1.17.0 | MIT License |
| soupsieve | 2.10 | MIT |
| sympy | 1.14.0 | BSD License |
| typing_extensions | 4.16.0 | PSF-2.0 |
| tzdata | 2026.4 | Apache-2.0 |
| urllib3 | 2.8.0 | MIT |
| xlsxwriter | 3.2.9 | BSD License |

### Grouped by license string

**3-Clause BSD License** (1 package(s))
- `python:protobuf==7.36.2`

**Apache Software License** (1 package(s))
- `python:python-dateutil==2.9.0.post0`

**Apache-2.0** (1 package(s))
- `python:tzdata==2026.4`

**Apache-2.0 OR BSD-2-Clause** (1 package(s))
- `python:packaging==26.3`

**Apache-2.0 OR BSD-3-Clause** (1 package(s))
- `python:cryptography==50.0.1`

**BSD License** (6 package(s))
- `python:mpmath==1.3.0`
- `python:numpy==2.2.6`
- `python:pandas==2.3.3`
- `python:reportlab==5.0.0`
- `python:sympy==1.14.0`
- `python:xlsxwriter==3.2.9`

**BSD-3-Clause** (6 package(s))
- `python:click==8.5.0`
- `python:idna==3.20`
- `python:lxml==6.1.1`
- `python:pycparser==3.0`
- `python:pypdf==6.14.2`
- `python:python-dotenv==1.2.3`

**BSD-3-Clause, Apache-2.0, dependency licenses** (1 package(s))
- `python:pypdfium2==5.12.1`

**MIT** (5 package(s))
- `python:charset-normalizer==3.5.1`
- `python:markitdown==0.1.7`
- `python:pdfminer.six==20260107`
- `python:soupsieve==2.10`
- `python:urllib3==2.8.0`

**MIT License** (13 package(s))
- `python:beautifulsoup4==4.15.0`
- `python:coloredlogs==15.0.1`
- `python:et_xmlfile==2.0.0`
- `python:humanfriendly==10.0`
- `python:markdownify==1.2.3`
- `python:onnxruntime==1.23.2`
- `python:openpyxl==3.1.5`
- `python:pdf2image==1.17.0`
- `python:pdfplumber==0.11.10`
- `python:python-docx==1.2.0`
- `python:python-pptx==1.0.2`
- `python:pytz==2026.4`
- `python:six==1.17.0`

**MIT-0** (1 package(s))
- `python:cffi==2.1.1`

**MIT-CMU** (1 package(s))
- `python:pillow==12.3.0`

**Mozilla Public License 2.0 (MPL 2.0)** (1 package(s))
- `python:certifi==2026.7.22`

**PSF-2.0** (1 package(s))
- `python:typing_extensions==4.16.0`

**Python Software Foundation License** (1 package(s))
- `python:defusedxml==0.7.1`

## 3. Node Dependencies

_No `package.json` / node_modules found in working directory — Node scan empty._

## 4. SPDX Catalog Snapshot

Full SPDX list: **740** licenses (from [spdx/license-list-data](https://github.com/spdx/license-list-data)).
OSI-approved: **154**.

Sample (alphabetical, first 30):

| SPDX ID | OSI | Name |
|---------|-----|------|
| `0BSD` | Yes | BSD Zero Clause License |
| `3D-Slicer-1.0` |  | 3D Slicer License v1.0 |
| `AAL` | Yes | Attribution Assurance License |
| `ADSL` |  | Amazon Digital Services License |
| `AFL-1.1` | Yes | Academic Free License v1.1 |
| `AFL-1.2` | Yes | Academic Free License v1.2 |
| `AFL-2.0` | Yes | Academic Free License v2.0 |
| `AFL-2.1` | Yes | Academic Free License v2.1 |
| `AFL-3.0` | Yes | Academic Free License v3.0 |
| `AGPL-1.0` |  | Affero General Public License v1.0 |
| `AGPL-1.0-only` |  | Affero General Public License v1.0 only |
| `AGPL-1.0-or-later` |  | Affero General Public License v1.0 or later |
| `AGPL-3.0` | Yes | GNU Affero General Public License v3.0 |
| `AGPL-3.0-only` | Yes | GNU Affero General Public License v3.0 only |
| `AGPL-3.0-or-later` | Yes | GNU Affero General Public License v3.0 or later |
| `ALGLIB-Documentation` | Yes | ALGLIB Documentation License |
| `AMD-newlib` |  | AMD newlib License |
| `AMDPLPA` |  | AMD's plpa_map.c License |
| `AML` |  | Apple MIT License |
| `AML-glslang` |  | AML glslang variant License |
| `AMPAS` |  | Academy of Motion Picture Arts and Sciences BSD |
| `ANTLR-PD` |  | ANTLR Software Rights Notice |
| `ANTLR-PD-fallback` |  | ANTLR Software Rights Notice with license fallback |
| `APAFML` |  | Adobe Postscript AFM License |
| `APL-1.0` | Yes | Adaptive Public License 1.0 |
| `APSL-1.0` | Yes | Apple Public Source License 1.0 |
| `APSL-1.1` | Yes | Apple Public Source License 1.1 |
| `APSL-1.2` | Yes | Apple Public Source License 1.2 |
| `APSL-2.0` | Yes | Apple Public Source License 2.0 |
| `ASWF-Digital-Assets-1.0` |  | ASWF Digital Assets License version 1.0 |

... (see `unified_licenses.json` for complete catalog)

## Artifacts

- `unified_licenses.json` — full machine-readable output (catalog + deps + synthesis)
- `unified_license_enum.py` — multi-agent runner script
- `LICENSE_REPORT.md` — this report
