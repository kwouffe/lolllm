# lolllm — Living Off The Land: Large Language Models

[![CI](https://github.com/kwouffe/lolllm/badges/main/pipeline.svg)](https://github.com/kwouffe/lolllm)

Community-driven detection repository for local LLM inference engines and cloud LLM API
clients abused on endpoints.

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
python scripts/generate_feeds.py
mkdocs serve
```

The local site is available at `http://127.0.0.1:8000`.
Machine-readable feeds are written to `site/api/tools.json` and `site/api/tools.csv`.

## Contributing

See [docs/contribute.md](docs/contribute.md) or the live site.

## License

MIT
