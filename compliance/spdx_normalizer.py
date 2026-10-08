"""Normalize raw dependency license strings to canonical SPDX IDs."""
from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple


class SPDXNormalizer:
    EXACT_MAP: Dict[str, str] = {
        "mit": "MIT",
        "mit license": "MIT",
        "mit-0": "MIT-0",
        "mit/cmu": "MIT-CMU",
        "mit-cmu": "MIT-CMU",
        "apache": "Apache-2.0",
        "apache 2": "Apache-2.0",
        "apache 2.0": "Apache-2.0",
        "apache license 2.0": "Apache-2.0",
        "apache software license": "Apache-2.0",
        "apache-2.0": "Apache-2.0",
        "bsd": "BSD-3-Clause",
        "bsd license": "BSD-3-Clause",
        "3-clause bsd": "BSD-3-Clause",
        "3-clause bsd license": "BSD-3-Clause",
        "bsd 3-clause": "BSD-3-Clause",
        "bsd-3-clause": "BSD-3-Clause",
        "2-clause bsd": "BSD-2-Clause",
        "bsd 2-clause": "BSD-2-Clause",
        "bsd-2-clause": "BSD-2-Clause",
        "psf": "PSF-2.0",
        "psf-2.0": "PSF-2.0",
        "psf license": "PSF-2.0",
        "python software foundation": "PSF-2.0",
        "python software foundation license": "PSF-2.0",
        "mpl 2.0": "MPL-2.0",
        "mozilla public license 2.0": "MPL-2.0",
        "mozilla public license 2.0 (mpl 2.0)": "MPL-2.0",
        "mpl-2.0": "MPL-2.0",
        "lgpl": "LGPL-3.0-only",
        "gpl": "GPL-3.0-only",
        "agpl": "AGPL-3.0-only",
        "unlicense": "Unlicense",
        "cc0": "CC0-1.0",
        "isc": "ISC",
        "bsl-1.0": "BSL-1.0",
        "boost software license 1.0": "BSL-1.0",
    }

    REGEX_RULES: List[Tuple[re.Pattern, str]] = [
        (re.compile(r"\bmit-0\b", re.I), "MIT-0"),
        (re.compile(r"\bmit[- ]?cmu\b", re.I), "MIT-CMU"),
        (re.compile(r"\bmit\b", re.I), "MIT"),
        (re.compile(r"\bapache\b.*2(\.0)?\b|\bapache software license\b", re.I), "Apache-2.0"),
        (re.compile(r"\bbsd\b.*3[- ]clause\b|\b3[- ]clause\b.*bsd\b", re.I), "BSD-3-Clause"),
        (re.compile(r"\bbsd\b.*2[- ]clause\b|\b2[- ]clause\b.*bsd\b", re.I), "BSD-2-Clause"),
        (re.compile(r"\bmozilla\b.*2\.0\b|\bmpl\b.*2\.0\b", re.I), "MPL-2.0"),
        (re.compile(r"\bpython software foundation\b|\bpsf\b", re.I), "PSF-2.0"),
        (re.compile(r"\bagpl\b.*3", re.I), "AGPL-3.0-only"),
        (re.compile(r"\bgpl\b.*3", re.I), "GPL-3.0-only"),
        (re.compile(r"\blgpl\b.*2\.1", re.I), "LGPL-2.1-only"),
        (re.compile(r"\bbsl\b|\bboost software license\b", re.I), "BSL-1.0"),
        (re.compile(r"\bunlicense\b", re.I), "Unlicense"),
        (re.compile(r"\bcc0\b", re.I), "CC0-1.0"),
        (re.compile(r"\bisc\b", re.I), "ISC"),
        (re.compile(r"\bbsd\b", re.I), "BSD-3-Clause"),
    ]

    def __init__(self, valid_spdx_ids: Optional[List[str]] = None):
        self.valid_spdx_ids: Set[str] = set(valid_spdx_ids) if valid_spdx_ids else set()

    def normalize(self, raw_license: str) -> str:
        if not raw_license or not str(raw_license).strip():
            return "UNKNOWN"
        raw_clean = str(raw_license).strip()
        raw_clean = re.sub(r",\s*dependency licenses\b", "", raw_clean, flags=re.I)
        raw_clean = re.sub(r"\s+", " ", raw_clean).strip(" ;,")

        # Dual / multi license expressions
        if re.search(r"\b(or|and)\b|/|;|,", raw_clean, re.I):
            parts = re.split(r"\s+(?:OR|AND)\s+|\s*/\s*|\s*;\s*|\s*,\s*", raw_clean, flags=re.I)
            normalized_parts: List[str] = []
            for p in parts:
                p = p.strip()
                if not p:
                    continue
                n = self._normalize_single(p)
                if n and n not in normalized_parts:
                    normalized_parts.append(n)
            if len(normalized_parts) > 1:
                # Prefer OR for permissive duals (packaging style)
                return " OR ".join(normalized_parts)
            if len(normalized_parts) == 1:
                return normalized_parts[0]

        return self._normalize_single(raw_clean)

    def _normalize_single(self, text: str) -> str:
        cleaned = text.strip().strip("()[]")
        lower = cleaned.lower()
        if self.valid_spdx_ids and cleaned in self.valid_spdx_ids:
            return cleaned
        if lower in self.EXACT_MAP:
            return self.EXACT_MAP[lower]
        for pattern, spdx_id in self.REGEX_RULES:
            if pattern.search(cleaned):
                return spdx_id
        return cleaned if cleaned else "UNKNOWN"


def atoms(expression: str) -> List[str]:
    return [p.strip() for p in re.split(r"\s+OR\s+|\s+AND\s+", expression) if p.strip()]
