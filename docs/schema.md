# Schema Reference

The canonical schema is defined in `schema/lolllm.schema.json` (JSON Schema draft 2020-12).
The Pydantic implementation lives in `scripts/validate.py`.

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `Name` | string | yes | Display name, Title Case |
| `Category` | enum | yes | `InferenceEngine` \| `CloudAPIClient` \| `FineTuningTool` \| `EmbeddingEngine` |
| `Description` | string | yes | Forensics-focused description |
| `Author` | string | yes | `@handle` or `First Last` |
| `Created` | date | yes | `YYYY-MM-DD` |
| `LastModified` | date | yes | `YYYY-MM-DD` |
| `Details` | object | yes | See below |
| `Artifacts` | object | yes | See below |
| `Detections` | object | yes | See below |
| `References` | string[] | no | URLs |
| `Acknowledgements` | object[] | no | `Person` + optional `Handle` |

## Details

| Field | Type | Description |
|-------|------|-------------|
| `Website` | string | Canonical URL |
| `License` | string | SPDX identifier |
| `Privileges` | enum | `user` \| `admin` \| `SYSTEM` \| `root` |
| `Free` | boolean | |
| `SupportedOS` | enum[] | `Windows` \| `Linux` \| `macOS` |
| `Capabilities` | enum[] | See controlled vocabulary |

## Artifacts

### Disk
Binary executables, config files, and logs on the filesystem.

### ModelStorage
Locations where model weight files are stored, with optional `MagicBytes` entries
(useful for YARA rules and filesystem scanning):

| Field | Description |
|-------|-------------|
| `Format` | `GGUF` \| `safetensors` \| `ONNX` \| `PyTorch` |
| `Hex` | Space-separated byte pairs at `Offset` |
| `Offset` | Byte offset from file start (usually `0`) |

### Process
Process image names with CLI argument regex patterns and expected parent process.

### Network
Ports, bind addresses, and domains. `BindAddress: 127.0.0.1` vs `0.0.0.0` is a key
signal — an exposed API is a lateral movement risk.

### Persistence
Mechanism by OS: `Service` (systemd/SCM), `Registry`, `Cron`, `LaunchAgent`, `LaunchDaemon`.

### EventLog / Registry
Windows-specific forensic artifacts.

## Detections

References to detection rule files in the repo:

- `Sigma[].Path` — must match `detections/sigma/*.yml`
- `YARA[].Path` — must match `detections/yara/*.yar`
