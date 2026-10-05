#!/usr/bin/env python3
"""Convert YAML tool entries to MkDocs markdown pages."""

from pathlib import Path

import yaml
from jinja2 import Environment, BaseLoader

YAML_DIR = Path(__file__).parent.parent / "yaml"
DOCS_DIR = Path(__file__).parent.parent / "docs" / "tools"

TEMPLATE = """\
# {{ tool.Name }}

!!! info "Quick Reference"
    **Category:** `{{ tool.Category }}` &nbsp;|&nbsp;
    **OS:** {{ tool.Details.SupportedOS | join(", ") }} &nbsp;|&nbsp;
    **Privileges:** `{{ tool.Details.Privileges }}` &nbsp;|&nbsp;
    **Free:** {{ "Yes" if tool.Details.Free else "No" }}

{{ tool.Description }}

---

## Details

| Field | Value |
|-------|-------|
| Website | {{ tool.Details.Website }} |
| License | `{{ tool.Details.License }}` |

**Capabilities:** {% for c in tool.Details.Capabilities %}`{{ c }}`{% if not loop.last %}, {% endif %}{% endfor %}

---
{% if tool.Artifacts.Disk %}

## Disk Artifacts

| Path | OS | Type | Phase | Description |
|------|----|------|-------|-------------|
{% for a in tool.Artifacts.Disk -%}
| `{{ a.Path }}` | {{ a.OS }} | {{ a.Type }} | {{ a.Phase if a.Phase is defined and a.Phase else "—" }} | {{ a.Description }} |
{% endfor %}
{% endif %}
{% if tool.Artifacts.ModelStorage %}

## Model Storage

{% for ms in tool.Artifacts.ModelStorage %}
**`{{ ms.Path }}`** ({{ ms.OS }}) — {{ ms.Description }}{% if ms.Phase is defined and ms.Phase %} *({{ ms.Phase }})*{% endif %}

{% if ms.MagicBytes %}
| Format | Magic Bytes (hex) | Offset |
|--------|-------------------|--------|
{% for mb in ms.MagicBytes -%}
| {{ mb.Format }} | `{{ mb.Hex }}` | {{ mb.Offset }} |
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}
{% if tool.Artifacts.Process %}

## Process Artifacts

{% for p in tool.Artifacts.Process %}
### `{{ p.Name }}`{% if p.Phase is defined and p.Phase %} <small>*({{ p.Phase }})*</small>{% endif %}

{{ p.Description }}
{% if p.ParentProcess %}
**Expected parent:** `{{ p.ParentProcess }}`
{% endif %}
{% if p.CLI %}

| CLI Pattern | Phase | Description |
|-------------|-------|-------------|
{% for c in p.CLI -%}
| `{{ c.Pattern }}` | {{ c.Phase if c.Phase is defined and c.Phase else "—" }} | {{ c.Description }} |
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}
{% if tool.Artifacts.Network %}

## Network Artifacts

| Description | Protocol | Ports | Bind Address | Domains | Phase |
|-------------|----------|-------|--------------|---------|-------|
{% for n in tool.Artifacts.Network -%}
| {{ n.Description }} | {{ n.Protocol }} | {{ n.Ports | join(", ") if n.Ports else "—" }} | `{{ n.BindAddress if n.BindAddress else "—" }}` | {{ n.Domains | join(", ") if n.Domains else "—" }} | {{ n.Phase if n.Phase is defined and n.Phase else "—" }} |
{% endfor %}
{% endif %}
{% if tool.Artifacts.Persistence %}

## Persistence Mechanisms

| OS | Type | Path | Phase | Description |
|----|------|------|-------|-------------|
{% for p in tool.Artifacts.Persistence -%}
| {{ p.OS }} | {{ p.Type }} | `{{ p.Path }}` | {{ p.Phase if p.Phase is defined and p.Phase else "—" }} | {{ p.Description }} |
{% endfor %}
{% endif %}
{% if tool.Artifacts.EventLog %}

## Windows Event Log

| Event ID | Provider | Log File | Phase | Description |
|----------|----------|----------|-------|-------------|
{% for e in tool.Artifacts.EventLog -%}
| {{ e.EventID }} | {{ e.ProviderName }} | {{ e.LogFile }} | {{ e.Phase if e.Phase is defined and e.Phase else "—" }} | {{ e.Description }} |
{% endfor %}
{% endif %}
{% if tool.Artifacts.Registry %}

## Registry Artifacts

| Path | Phase | Description |
|------|-------|-------------|
{% for r in tool.Artifacts.Registry -%}
| `{{ r.Path }}` | {{ r.Phase if r.Phase is defined and r.Phase else "—" }} | {{ r.Description }} |
{% endfor %}
{% endif %}
{% if tool.Detections.Sigma or tool.Detections.YARA %}

## Detection Rules

{% if tool.Detections.Sigma %}
### Sigma
{% for s in tool.Detections.Sigma %}
- `{{ s.Path }}` *({{ s.Phase if s.Phase is defined and s.Phase else "—" }})* — {{ s.Description }}
{% endfor %}
{% endif %}
{% if tool.Detections.YARA %}
### YARA
{% for y in tool.Detections.YARA %}
- `{{ y.Path }}` *({{ y.Phase if y.Phase is defined and y.Phase else "—" }})* — {{ y.Description }}
{% endfor %}
{% endif %}
{% endif %}
{% if tool.References %}

## References

{% for r in tool.References %}
- {{ r }}
{% endfor %}
{% endif %}
"""


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    env = Environment(loader=BaseLoader())
    env.filters["basename"] = lambda p: Path(p).name
    tmpl = env.from_string(TEMPLATE)

    files = sorted(YAML_DIR.glob("*.yaml"))
    print(f"Generating docs for {len(files)} tool(s)...")

    for path in files:
        with path.open() as f:
            tool = yaml.safe_load(f)

        # Normalise nested dicts to objects with attribute access via SimpleNamespace
        rendered = tmpl.render(tool=_to_ns(tool))
        out = DOCS_DIR / f"{path.stem}.md"
        out.write_text(rendered)
        print(f"  wrote {out.relative_to(Path(__file__).parent.parent)}")

    # Write the tools index
    index_lines = ["# Tools\n"]
    for path in files:
        with path.open() as f:
            t = yaml.safe_load(f)
        index_lines.append(f"- [{t['Name']}]({path.stem}.md) — {t['Category']}")
    (DOCS_DIR / "index.md").write_text("\n".join(index_lines) + "\n")
    print(f"  wrote docs/tools/index.md")


def _to_ns(obj):
    """Recursively convert dicts/lists to SimpleNamespace for template attribute access."""
    from types import SimpleNamespace
    if isinstance(obj, dict):
        return SimpleNamespace(**{k: _to_ns(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [_to_ns(i) for i in obj]
    return obj


if __name__ == "__main__":
    main()
