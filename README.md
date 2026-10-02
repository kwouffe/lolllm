# lolllm — Living Off The Land: Large Language Models

[![CI](https://github.com/kwouffe/lolllm/actions/workflows/ci.yml/badge.svg)](https://github.com/kwouffe/lolllm/actions)

Community-driven detection repository for local LLM inference engines and cloud LLM API
clients abused on endpoints. Live site: **[lolllm.io](https://lolllm.io)**

## What's inside

| Path | Contents |
|------|----------|
| `yaml/` | One YAML file per tracked tool — the single source of truth |
| `detections/sigma/` | Sigma detection rules |
| `detections/yara/` | YARA rules (GGUF magic bytes, binary heuristics) |
| `schema/lolllm.schema.json` | Published JSON Schema for editor/CI validation |
| `scripts/validate.py` | Pydantic schema validation gate |
| `scripts/generate_docs.py` | YAML → MkDocs markdown pages |
| `scripts/generate_feeds.py` | YAML → `site/api/tools.json` + `tools.csv` |

## Quick start

```bash
# Install dependencies
pip install -e ".[dev]"

# Validate all YAML entries
python scripts/validate.py

# Generate docs and feeds, then serve locally
python scripts/generate_docs.py
mkdocs serve
```

The local site is available at `http://127.0.0.1:8000`.
Machine-readable feeds are available at `https://lolllm.io/api/tools.json` and `https://lolllm.io/api/tools.csv`.

## LLM-assisted contributions

This project uses LLM-generated content and **welcomes contributions that were created or assisted by LLMs**.
All YAML entries carry a `ReviewStatus: unreviewed` tag until a human maintainer has manually verified the
artifacts, detection logic, and references. If you submit LLM-assisted content, please:

- Keep `ReviewStatus: unreviewed` in your entry
- Include a note in the pull request describing which parts were LLM-generated
- Ensure the factual claims (file paths, process names, network endpoints) are plausible and sourced

Submissions will be accepted on their technical merit regardless of whether a human or an LLM produced the
first draft.

## Contributing

See [docs/contribute.md](docs/contribute.md) or the live site at [lolllm.io/contribute](https://lolllm.io/contribute/).

## License

GPL-3.0
