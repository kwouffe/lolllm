#!/usr/bin/env python3
"""Validate all YAML tool entries against the lolllm Pydantic schema."""

import sys
from datetime import date
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, ValidationError, field_validator, Field, NonNegativeInt

YAML_DIR = Path(__file__).parent.parent / "yaml"
REPO_ROOT = Path(__file__).resolve().parent.parent


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


TrustName = Literal["ai-generated", "ai-cross-checked", "source-cited", "lab-observed", "human-verified"]
TrustType = Optional[TrustName]


class EvidenceRef(BaseModel):
    Type: Literal["url", "source", "lab", "checker", "human"]
    Ref: str
    Excerpt: str = Field(max_length=200)


class DiskArtifact(BaseModel):
    Path: str
    Description: str
    OS: Literal["Windows", "Linux", "macOS", "Any"]
    Type: Literal["Binary", "Config", "Log", "Cache"]
    Phase: PhaseType = None
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []


class ModelStorageArtifact(BaseModel):
    Path: str
    Description: str
    OS: Literal["Windows", "Linux", "macOS", "Any"]
    Phase: PhaseType = None
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []
    MagicBytes: list[MagicByte] = []


class CLIPattern(BaseModel):
    Pattern: str
    Description: str
    Phase: PhaseType = None
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []


class ProcessArtifact(BaseModel):
    Name: str
    Description: str
    Phase: PhaseType = None
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []
    CLI: list[CLIPattern] = []
    ParentProcess: Optional[str] = None


class NetworkArtifact(BaseModel):
    Description: str
    Protocol: Literal["TCP", "UDP"]
    Ports: list[int] = []
    BindAddress: str = ""
    Domains: list[str] = []
    Phase: PhaseType = None
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []


class PersistenceArtifact(BaseModel):
    OS: Literal["Windows", "Linux", "macOS"]
    Type: Literal["Service", "Registry", "Cron", "LaunchAgent", "LaunchDaemon", "ShellRC", "XDGAutostart"]
    Path: str
    Description: str
    Phase: PhaseType = None
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []


class EventLogArtifact(BaseModel):
    EventID: int
    ProviderName: str
    LogFile: str
    Description: str
    Phase: PhaseType = None
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []


class RegistryArtifact(BaseModel):
    Path: str
    Description: str
    Phase: PhaseType = None
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []


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
    Trust: TrustType = None
    Evidence: list[EvidenceRef] = []

    @field_validator("Path")
    @classmethod
    def path_exists(cls, v: str) -> str:
        target = (REPO_ROOT / v).resolve()
        if Path(v).is_absolute() or not target.is_relative_to(REPO_ROOT):
            raise ValueError(f"detection path escapes the repository: {v!r}")
        if not target.is_file():
            raise ValueError(f"detection file does not exist: {v}")
        return v


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


class EntryTrustSummary(BaseModel):
    Min: TrustName
    Counts: dict[TrustName, NonNegativeInt]
    Excluded: NonNegativeInt


class LolLLMEntry(BaseModel):
    Name: str
    Category: Literal["InferenceEngine", "CloudAPIClient", "FineTuningTool", "EmbeddingEngine"]
    Description: str
    Author: str
    Created: date
    LastModified: date
    ReviewStatus: Literal["unreviewed", "in-review", "reviewed"]
    TrustSummary: Optional[EntryTrustSummary] = None
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
