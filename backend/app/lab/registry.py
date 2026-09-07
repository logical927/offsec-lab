import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LabDefinition:
    mission_id: int
    compose_file: Path
    project_name: str
    services: frozenset[str]
    target_container: str
    network_name: str


def _project_root() -> Path:
    configured_root = os.getenv("OFFSEC_PROJECT_ROOT")
    if configured_root:
        return Path(configured_root).resolve()
    return Path(__file__).resolve().parents[3]


LAB_REGISTRY: dict[int, LabDefinition] = {
    1: LabDefinition(
        mission_id=1,
        compose_file=(
            _project_root() / "challenges" / "m01-recon" / "compose.lab.yml"
        ),
        project_name="offsec-m01",
        services=frozenset({"attacker", "target"}),
        target_container="target-m01",
        network_name="offsec-m01-net",
    )
}


def get_lab_definition(mission_id: int) -> LabDefinition | None:
    return LAB_REGISTRY.get(mission_id)
