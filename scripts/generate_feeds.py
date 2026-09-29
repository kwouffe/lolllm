#!/usr/bin/env python3
"""Generate machine-readable JSON and CSV feeds from YAML tool entries."""

import csv
import json
from datetime import date
from pathlib import Path

import yaml

YAML_DIR = Path(__file__).parent.parent / "yaml"
FEED_DIR = Path(__file__).parent.parent / "site" / "api"


def _serialise(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Not serialisable: {type(obj)}")


def flatten_for_csv(tool: dict) -> dict:
    """Extract high-signal fields into a flat row suitable for SIEM lookup tables."""
    arts = tool.get("Artifacts", {})

    disk_paths = [d["Path"] for d in arts.get("Disk", [])]
    model_paths = [m["Path"] for m in arts.get("ModelStorage", [])]
    magic_bytes = [
        mb["Hex"]
        for m in arts.get("ModelStorage", [])
        for mb in m.get("MagicBytes", [])
    ]
    ports = [
        str(p)
        for n in arts.get("Network", [])
        for p in n.get("Ports", [])
    ]
    domains = [
        d
        for n in arts.get("Network", [])
        for d in n.get("Domains", [])
    ]
    process_names = [p["Name"] for p in arts.get("Process", [])]
    persistence_paths = [p["Path"] for p in arts.get("Persistence", [])]
    sigma_paths = [s["Path"] for s in tool.get("Detections", {}).get("Sigma", [])]
    yara_paths = [y["Path"] for y in tool.get("Detections", {}).get("YARA", [])]

    return {
        "name": tool["Name"],
        "category": tool["Category"],
        "os": "|".join(tool["Details"]["SupportedOS"]),
        "privileges": tool["Details"]["Privileges"],
        "capabilities": "|".join(tool["Details"].get("Capabilities", [])),
        "disk_paths": "|".join(disk_paths),
        "model_storage_paths": "|".join(model_paths),
        "magic_bytes_hex": "|".join(magic_bytes),
        "process_names": "|".join(process_names),
        "network_ports": "|".join(ports),
        "network_domains": "|".join(domains),
        "persistence_paths": "|".join(persistence_paths),
        "sigma_rules": "|".join(sigma_paths),
        "yara_rules": "|".join(yara_paths),
        "created": tool["Created"],
        "last_modified": tool["LastModified"],
    }


def main() -> None:
    FEED_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(YAML_DIR.glob("*.yaml"))
    tools = []
    for path in files:
        with path.open() as f:
            tools.append(yaml.safe_load(f))

    # Full JSON feed
    json_out = FEED_DIR / "tools.json"
    with json_out.open("w") as f:
        json.dump(tools, f, indent=2, default=_serialise)
    print(f"Wrote {json_out} ({len(tools)} tools)")

    # Flat CSV feed for SIEM lookup tables
    csv_out = FEED_DIR / "tools.csv"
    rows = [flatten_for_csv(t) for t in tools]
    if rows:
        with csv_out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {csv_out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
