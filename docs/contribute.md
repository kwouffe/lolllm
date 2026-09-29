# Contributing

## Adding a New Tool

1. Copy an existing entry as a template:
   ```bash
   cp yaml/ollama.yaml yaml/your_tool.yaml
   ```

2. Edit the new file — all fields are documented in [Schema Reference](schema.md).

3. Validate locally before committing:
   ```bash
   pip install -e ".[dev]"
   python scripts/validate.py
   ```

4. Add any Sigma rules to `detections/sigma/` and YARA rules to `detections/yara/`,
   then reference them from your YAML entry's `Detections` block.

5. Open a merge request. CI will run validation automatically.

## Naming Convention

YAML files use lowercase with underscores, matching the tool's canonical name:

- `ollama.yaml`
- `llama_cpp.yaml`
- `lm_studio.yaml`

## Controlled Vocabulary

### Category
`InferenceEngine` | `CloudAPIClient` | `FineTuningTool` | `EmbeddingEngine`

### Capabilities
`LocalInference` | `APIServer` | `ModelDownload` | `GPUAcceleration` | `RemoteAPIProxy`

### Artifact Types
`Binary` | `Config` | `Log` | `Cache`

### Persistence Types
`Service` | `Registry` | `Cron` | `LaunchAgent` | `LaunchDaemon`
