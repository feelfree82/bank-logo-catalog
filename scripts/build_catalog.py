#!/usr/bin/env python3
"""Build the country-aware local release candidate from read-only logo exports."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import unicodedata
from datetime import date
from pathlib import Path


INDIA_NAME_FIXES = {
    "Bank of Maharastra": ("Bank of Maharashtra", ["Bank of Maharastra"]),
    "Induslnd Bank": ("IndusInd Bank", ["Induslnd Bank"]),
    "IDFC Bank": ("IDFC FIRST Bank", ["IDFC Bank"]),
    "Union Bank": ("Union Bank of India", ["Union Bank"]),
    "Citi Bank": ("Citibank", ["Citi Bank", "Citibank N.A."]),
    "Scotia Bank": ("Scotiabank", ["Scotia Bank", "Bank of Nova Scotia"]),
    "Mizuho Corporate Bank": ("Mizuho Bank", ["Mizuho Corporate Bank"]),
    "Bank Maybank Indonesia": ("Maybank Indonesia", ["Bank Maybank Indonesia"]),
    "JPMorgan Chase": ("J.P. Morgan Chase Bank", ["JPMorgan Chase"]),
    "Crédit Agricole Corporate and Investment Bank": (
        "Crédit Agricole CIB",
        ["Crédit Agricole Corporate and Investment Bank"],
    ),
}

INDIA_HOLDS = {
    "Abu Dhabi Commercial Bank": "not_on_current_rbi_foreign_bank_list",
    "Credit Suisse": "historical_status_requires_review",
    "Krung Thai Bank": "not_on_current_rbi_foreign_bank_list",
    "Paytm Payments Bank": "inactive_or_cancelled_status_requires_review",
    "Westpac": "not_on_current_rbi_foreign_bank_list",
}


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.casefold()).strip("-") or "institution"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def svg_type(path: Path) -> str:
    return "raster_embedded" if b"data:image/" in path.read_bytes() else "vector"


def unique_id(country: str, name: str, source_key: str, used: set[str]) -> str:
    base = f"{country.lower()}-{slugify(name)}"
    candidate = base
    if candidate in used:
        candidate = f"{base}-{hashlib.sha256(source_key.encode()).hexdigest()[:8]}"
    used.add(candidate)
    return candidate


def copy_asset(source: Path, target: Path) -> tuple[str, str]:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    digest = sha256(target)
    return digest[:16], target.suffix.removeprefix(".")


def build_us(source: Path, output: Path, used: set[str]) -> list[dict]:
    stems: dict[str, dict[str, Path]] = {}
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".svg", ".png"}:
            key = path.with_suffix("").relative_to(source).as_posix()
            stems.setdefault(key, {})[path.suffix.lower().removeprefix(".")] = path
    records = []
    for source_key, formats in sorted(stems.items(), key=lambda item: item[0].casefold()):
        name = Path(source_key).name
        institution_id = unique_id("US", name, source_key, used)
        variants: dict[str, dict] = {"icon": {}}
        revisions = []
        for extension in ("svg", "png"):
            source_path = formats.get(extension)
            if not source_path:
                continue
            relative = Path("v1/assets/us") / institution_id / f"icon.{extension}"
            revision, _ = copy_asset(source_path, output / relative)
            revisions.append(f"{extension}:{revision}")
            variants["icon"][extension] = f"{relative.as_posix()}?v={revision}"
        variants["icon"]["artwork_type"] = svg_type(formats["svg"]) if "svg" in formats else "raster"
        records.append({
            "id": institution_id,
            "country": "US",
            "name": name,
            "official_name": None,
            "aliases": [],
            "institution_type": "unclassified",
            "status": "unverified",
            "logo_revision": hashlib.sha256("|".join(revisions).encode()).hexdigest()[:16],
            "updated_at": None,
            "logos": variants,
            "review_status": "identity_provenance_and_current_status_unverified",
        })
    return records


def build_india(small_root: Path, large_root: Path, output: Path, used: set[str]) -> tuple[list[dict], list[dict]]:
    prefix = "Bank Name="
    clean = lambda path: path.stem.removeprefix(prefix)
    small = {clean(path): path for path in sorted(small_root.glob("*.svg"))}
    large = {clean(path): path for path in sorted(large_root.glob("*.svg"))}
    paired = sorted(set(small) & set(large), key=str.casefold)
    records, held = [], []
    for source_name in paired:
        if source_name in INDIA_HOLDS:
            held.append({"source_name": source_name, "reason": INDIA_HOLDS[source_name]})
            continue
        name, aliases = INDIA_NAME_FIXES.get(source_name, (source_name, []))
        institution_id = unique_id("IN", name, source_name, used)
        variants = {}
        revisions = []
        for variant, source_path in (("icon", small[source_name]), ("wordmark", large[source_name])):
            relative = Path("v1/assets/in") / institution_id / f"{variant}.svg"
            revision, _ = copy_asset(source_path, output / relative)
            revisions.append(f"{variant}:{revision}")
            variants[variant] = {
                "svg": f"{relative.as_posix()}?v={revision}",
                "artwork_type": svg_type(source_path),
            }
        records.append({
            "id": institution_id,
            "country": "IN",
            "name": name,
            "official_name": None,
            "aliases": aliases,
            "institution_type": "bank",
            "status": "active_candidate",
            "logo_revision": hashlib.sha256("|".join(revisions).encode()).hexdigest()[:16],
            "updated_at": None,
            "logos": variants,
            "review_status": "visual_pair_checked_provenance_unverified",
        })
    return records, held


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--us", type=Path, required=True, help="Read-only folder containing USA SVG and PNG exports")
    parser.add_argument("--in-small", type=Path, required=True, help="Read-only folder containing India icon SVG exports")
    parser.add_argument("--in-large", type=Path, required=True, help="Read-only folder containing India wordmark SVG exports")
    parser.add_argument("--out", type=Path, default=Path("docs"))
    args = parser.parse_args()
    output = args.out.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()
    us = build_us(args.us.resolve(), output, used)
    india, held = build_india(args.in_small.resolve(), args.in_large.resolve(), output, used)
    generated = date.today().isoformat()

    countries = [
        {
            "code": "US",
            "name": "United States",
            "record_count": len(us),
            "catalog": "v1/countries/us/institutions.json",
            "search_index": "v1/countries/us/search-index.json",
        },
        {
            "code": "IN",
            "name": "India",
            "record_count": len(india),
            "catalog": "v1/countries/in/institutions.json",
            "search_index": "v1/countries/in/search-index.json",
        },
    ]
    write_json(output / "v1/countries.json", {"schema_version": 1, "generated_at": generated, "countries": countries})
    for code, records in (("us", us), ("in", india)):
        payload = {"schema_version": 1, "country": code.upper(), "generated_at": generated, "institutions": records}
        write_json(output / f"v1/countries/{code}/institutions.json", payload)
        write_json(
            output / f"v1/countries/{code}/search-index.json",
            {
                "schema_version": 1,
                "country": code.upper(),
                "generated_at": generated,
                "institutions": [
                    {"id": record["id"], "name": record["name"], "aliases": record["aliases"]}
                    for record in records
                ],
            },
        )
        for record in records:
            write_json(output / f"v1/institutions/{record['id']}.json", record)
    write_json(output.parent / "held-india-assets.json", {"generated_at": generated, "held": held})
    write_json(
        output / "v1/schema.json",
        {
            "schema_version": 1,
            "required_record_fields": ["id", "country", "name", "aliases", "status", "logos", "logo_revision"],
            "logo_variants": ["icon", "wordmark"],
            "status_values": ["active", "active_candidate", "inactive", "historical", "unverified"],
        },
    )
    site_source = Path(__file__).resolve().parent.parent / "site" / "index.html"
    if site_source.is_file():
        shutil.copyfile(site_source, output / "index.html")
    project_root = Path(__file__).resolve().parent.parent
    for filename in ("README.md", "LICENSE", "ASSETS_AND_MARKS.md", "CONTRIBUTING.md", "CHANGELOG.md"):
        source = project_root / filename
        if source.is_file():
            shutil.copyfile(source, output.parent / filename)
    sdk_source = project_root / "sdk" / "logo-catalog.js"
    if sdk_source.is_file():
        sdk_target = output.parent / "sdk" / sdk_source.name
        sdk_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(sdk_source, sdk_target)
    print(f"Built global candidate: {len(us)} US records, {len(india)} India records, {len(held)} India holds.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
