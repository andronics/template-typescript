from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stacking import ROOT, commit, copy, sh, sibling, stage  # noqa: E402

# Each render gets a venv: link it to uv's cache instead of copying every package into it.
os.environ.setdefault("UV_LINK_MODE", "symlink")

# The base version this overlay needs, and its tests render (staged copies are tagged with it).
BASE_VERSION = "v2.0.0"
BASE = {"project_name": "demo", "description": "A demo project", "github_owner": "metalayerlab"}

# The render matrix: kind x container_image x contrib (has_cli follows kind). Each one must
# pass its own Definition of done and base's contract cases. `container` adds
# template-container (a sibling checkout) with these answers.
MATRIX: dict[str, dict[str, object]] = {
    "service-image": {"kind": "service", "container_image": True, "contrib": ["docker", "k8s", "systemd"],
                      "puid_pgid": True, "container": {}},
    "service-systemd": {"kind": "service", "container_image": False, "contrib": ["systemd"]},
    "service": {"kind": "service", "container_image": False, "contrib": []},
    "cli-image": {"kind": "cli", "container_image": True, "container": {"multi_arch": False}},
    "cli": {"kind": "cli", "container_image": False},
    "library": {"kind": "library"},
    "web-image": {"kind": "web", "container_image": True, "contrib": ["docker", "k8s"], "container": {}},
    "web-image-bare": {"kind": "web", "container_image": True, "contrib": []},
    "web": {"kind": "web", "container_image": False, "contrib": []},
}  # fmt: skip


@pytest.fixture(scope="session")
def base_src(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """template-base: $TEMPLATE_BASE, or ../template-base."""
    base = sibling("template-base", "TEMPLATE_BASE")
    if base is None:
        pytest.fail("template-base must be checked out next to this repository, or set TEMPLATE_BASE")
    return stage(base, tmp_path_factory.mktemp("src") / "template-base", tag=BASE_VERSION)


@pytest.fixture(scope="session")
def ts_src(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return stage(ROOT, tmp_path_factory.mktemp("src") / "template-typescript")


@pytest.fixture(scope="session")
def container_src(tmp_path_factory: pytest.TempPathFactory) -> Path | None:
    """template-container: $TEMPLATE_CONTAINER, or ../template-container (optional)."""
    found = sibling("template-container", "TEMPLATE_CONTAINER")
    return stage(found, tmp_path_factory.mktemp("src") / "template-container") if found else None


def render(base_src: Path, ts_src: Path, dst: Path, container_src: Path | None = None,
           base: dict | None = None, **answers: object) -> Path:  # fmt: skip
    """base, then typescript, then (with a `container` answer) template-container; bootstrapped."""
    container = answers.pop("container", None)
    copy(base_src, dst, {**BASE, **(base or {})})
    copy(ts_src, dst, answers)
    if container is not None:
        if container_src is None:
            pytest.skip("template-container isn't checked out next to this repository (or $TEMPLATE_CONTAINER)")
        copy(container_src, dst, dict(container))  # type: ignore[arg-type]
    sh("sh", "scripts/bootstrap.sh", cwd=dst)
    return commit(dst)


@pytest.fixture(scope="session", params=list(MATRIX))
def variant(request: pytest.FixtureRequest) -> str:
    return str(request.param)


@pytest.fixture(scope="session")
def project(variant: str, base_src: Path, ts_src: Path, container_src: Path | None,
            tmp_path_factory: pytest.TempPathFactory) -> Path:  # fmt: skip
    return render(base_src, ts_src, tmp_path_factory.mktemp(variant) / "demo", container_src, **MATRIX[variant])
