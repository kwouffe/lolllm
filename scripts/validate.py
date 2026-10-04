#!/usr/bin/env python3
"""Validate all YAML tool entries against the lolllm Pydantic schema."""

import sys
from datetime import date
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, ValidationError, field_validator

YAML_DIR = Path(__file__).parent.parent / "yaml"


class MagicByte(BaseModel):
    Format: str
    Hex: str
    Offset: int = 0

    @field_validator("Hex")
    @classmethod
    def hex_format(cls, v: str) -> str:
        parts = v.split()
        if not all(len(p) == 2 and all(c in "0123456789abcdefABCDEF" for c in p) for p in parts):
            raise ValueError(f"Hex must be space-separated byte pairs, got: {v!r}")
        return v


PhaseType = Optional[Literal["Install", "Activation", "Use", "Abuse"]]


class DiskArtifact(BaseModel):
    Path: str
    Description: str
    OS: Literal["Windows", "Linux", "macOS", "Any"]
    Type: Literal["Binary", "Config", "Log", "Cache"]
    Phase: PhaseType = None


class ModelStorageArtifact(BaseModel):
    Path: str
    Description: str
    OS: Literal["Windows", "Linux", "macOS", "Any"]
    Phase: PhaseType = None
    MagicBytes: list[MagicByte] = []


class CLIPattern(BaseModel):
    Pattern: str
    Description: str
    Phase: PhaseType = None


class ProcessArtifact(BaseModel):
    Name: str
    Description: str
    Phase: PhaseType = None
    CLI: list[CLIPattern] = []
    ParentProcess: Optional[str] = None


class NetworkArtifact(BaseModel):
    Description: str
    Protocol: Literal["TCP", "UDP"]
    Ports: list[int] = []
    BindAddress: str = ""
    Domains: list[str] = []
    Phase: PhaseType = None


class PersistenceArtifact(BaseModel):
    OS: Literal["Windows", "Linux", "macOS"]
    Type: Literal["Service", "Registry", "Cron", "LaunchAgent", "LaunchDaemon"]
    Path: str
    Description: str
    Phase: PhaseType = None


class EventLogArtifact(BaseModel):
    EventID: int
    ProviderName: str
    LogFile: str
    Description: str
    Phase: PhaseType = None


class RegistryArtifact(BaseModel):
    Path: str
    Description: str
    Phase: PhaseType = None


class Artifacts(BaseModel):
    Disk: list[DiskArtifact] = []
    ModelStorage: list[ModelStorageArtifact] = []
    Process: list[ProcessArtifact] = []
    Network: list[NetworkArtifact] = []
    Persistence: list[PersistenceArtifact] = []
    EventLog: list[EventLogArtifact] = []
    Registry: list[RegistryArtifact] = []


class DetectionRef(BaseModel):
    Path: str
    Description: str
    Phase: PhaseType = None


class Detections(BaseModel):
    Sigma: list[DetectionRef] = []
    YARA: list[DetectionRef] = []


class Details(BaseModel):
    Website: str
    License: str
    Privileges: Literal["user", "admin", "SYSTEM", "root"]
    Free: bool
    SupportedOS: list[Literal["Windows", "Linux", "macOS"]]
    Capabilities: list[
        Literal["LocalInference", "APIServer", "ModelDownload", "GPUAcceleration", "RemoteAPIProxy"]
    ]


class Acknowledgement(BaseModel):
    Person: str
    Handle: Optional[str] = None


class LolLLMEntry(BaseModel):
    Name: str
    Category: Literal["InferenceEngine", "CloudAPIClient", "FineTuningTool", "EmbeddingEngine"]
    Description: str
    Author: str
    Created: date
    LastModified: date
    ReviewStatus: Literal["unreviewed", "in-review", "reviewed"]
    Details: Details
    Artifacts: Artifacts
    Detections: Detections
    References: list[str] = []
    Acknowledgements: list[Acknowledgement] = []


def validate_file(path: Path) -> bool:
    with path.open() as f:
        raw = yaml.safe_load(f)
    try:
        LolLLMEntry.model_validate(raw)
        print(f"  OK  {path.name}")
        return True
    except ValidationError as e:
        print(f"  FAIL  {path.name}")
        for err in e.errors():
            loc = " -> ".join(str(x) for x in err["loc"])
            print(f"        [{loc}] {err['msg']}")
        return False


def main() -> None:
    files = sorted(YAML_DIR.glob("*.yaml"))
    if not files:
        print("No YAML files found in yaml/")
        sys.exit(1)

    print(f"Validating {len(files)} tool(s)...")
    failures = [f for f in files if not validate_file(f)]

    if failures:
        print(f"\n{len(failures)} file(s) failed validation.")
        sys.exit(1)
    else:
        print(f"\nAll {len(files)} file(s) valid.")


if __name__ == "__main__":
    main()
