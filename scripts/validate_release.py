#!/usr/bin/env python3
"""Validate the generated Bank Logo Catalog release package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("docs"), help="Published site root containing v1/")
    args = parser.parse_args()
    root = args.root.resolve()
    countries_payload = read_json(root / "v1/countries.json")
    assert countries_payload["schema_version"] == 1
    assert (root / "index.html").is_file()

    all_records: list[dict] = []
    summary: dict[str, dict] = {}
    for country in countries_payload["countries"]:
        code = country["code"].lower()
        catalog = read_json(root / f"v1/countries/{code}/institutions.json")
        search_index = read_json(root / f"v1/countries/{code}/search-index.json")
        records = catalog["institutions"]
        assert country["record_count"] == len(records)
        assert len(search_index["institutions"]) == len(records)
        assert {item["id"] for item in search_index["institutions"]} == {item["id"] for item in records}
        all_records.extend(records)
        summary[country["code"]] = {
            "records": len(records),
            "search_index_bytes": (root / f"v1/countries/{code}/search-index.json").stat().st_size,
        }

    ids = [record["id"] for record in all_records]
    assert len(ids) == len(set(ids))

    asset_count = 0
    for record in all_records:
        assert record["id"].startswith(record["country"].lower() + "-")
        assert read_json(root / f"v1/institutions/{record['id']}.json") == record
        for variant in record["logos"].values():
            for format_name in ("svg", "png"):
                if format_name not in variant:
                    continue
                path_text = variant[format_name].split("?", 1)[0]
                path = PurePosixPath(path_text)
                assert not path.is_absolute() and ".." not in path.parts
                assert (root / path).is_file(), path_text
                asset_count += 1

    result = {
        "status": "passed",
        "schema_version": 1,
        "total_records": len(all_records),
        "referenced_assets": asset_count,
        "countries": summary,
    }
    output = root.parent / "validation-report.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
