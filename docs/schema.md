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
| `TrustSummary` | object | no | Computed trust roll-up, see [Trust levels](#trust-levels) |
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
Mechanism by OS: `Service` (systemd/SCM), `Registry`, `Cron`, `LaunchAgent`, `LaunchDaemon`,
`ShellRC` (shell startup files such as `~/.bashrc`), `XDGAutostart` (`~/.config/autostart/*.desktop`).

### EventLog / Registry
Windows-specific forensic artifacts.

## Detections

References to detection rule files in the repo:

- `Sigma[].Path` — must match `detections/sigma/*.yml`
- `YARA[].Path` — must match `detections/yara/*.yar`

Every referenced rule file must exist in the repository (checked by `scripts/validate.py`).

## Trust levels

Every artifact and detection row may carry a `Trust` level and an `Evidence` list
(`{Type, Ref, Excerpt}`; `Type` is one of `url` | `source` | `lab` | `checker` | `human`,
`Excerpt` at most 200 characters). The entry's computed `TrustSummary` gives the lowest
level among its rows (`Min`), the number of rows per level (`Counts`) and the number of rows
excluded because they were refuted or are not actionable (`Excluded`).

| Level | Name | Meaning | Who can set it |
|---|---|---|---|
| 0 | `ai-generated` | Drafted by an LLM, unchecked | any agent |
| 1 | `ai-cross-checked` | An independent skeptic agent tried to refute it and failed; passes deterministic checks | skeptic agent |
| 2 | `source-cited` | Backed by official docs, the tool's source code, or packaging (install script, .deb/.rpm, MSI, Homebrew formula), with an exact URL + excerpt | research worker, confirmed by retester |
| 3 | `lab-observed` | Seen directly in a sandbox run (file created, process/cmdline, port bound, DNS lookup) | lab worker, confirmed by retester |
| 4 | `human-verified` | Maintainer confirmed in the UI | human only |

Levels may be skipped: a row's level is the highest level backed by evidence. `ReviewStatus`
follows from `TrustSummary.Min`: `unreviewed` = `ai-generated`, `in-review` =
`ai-cross-checked` to `lab-observed`, `reviewed` = `human-verified`.
