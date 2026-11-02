"""Render template-base, then template-typescript (and template-container for an image), across the
matrix in conftest.py, and check the projects that result.

    uv run pytest -n auto         # every test (../template-base, or $TEMPLATE_BASE)
    uv run pytest -m docker       # also the Docker-only checks: secrets, markdownlint, hadolint, actionlint

Each render must pass its own Definition of done unchanged: `sh scripts/checks.sh`, then the
project's lint, format, type check, tests and generated-wiki check.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from conftest import BASE, MATRIX, render
from stacking import GIT, ROOT, checks, commit, copy, sh, stage

SLOTS = [".github/workflows/stack-ci.yml", ".agents/stack.md", ".gitignore", ".pre-commit-config.yaml",
         ".claude/settings.json", "README.md", ".github/dependabot.yml"]  # fmt: skip
# Files project-template v0.1.23 rendered that are now another template's (decision 0001).
NOT_OURS = ["AGENTS.md", "CLAUDE.md", "GEMINI.md", "LICENSE", ".editorconfig", ".gitleaks.toml",
            ".github/workflows/base-ci.yml", ".github/workflows/template-update.yml", ".github/workflows/pr-title.yml",
            ".github/pull_request_template.md", ".github/copilot-instructions.md", ".github/CODEOWNERS",
            "scripts/checks.sh", "scripts/bootstrap.sh", "scripts/post-update.sh", "scripts/check-docs-secrets.sh",
            "scripts/repo-boundary.py", "scripts/repo-metadata.py", "scripts/base-contract.py"]  # fmt: skip


def run(project: Path, *cmd: str) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k not in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT")}
    return subprocess.run(cmd, cwd=project, capture_output=True, text=True, env=env)


def test_checks_pass(project: Path) -> None:
    result = checks(project)
    assert result.returncode == 0, result.stdout + result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "00-base OK" and lines[-1] == "20-typescript OK", lines
    assert re.fullmatch(r"wiki OK( \(\d+ warning\(s\); --verbose lists them\))?", lines[1]), lines


DOD = [
    ("npm", "ci", "--no-audit", "--no-fund", "--loglevel=error"),
    ("npm", "run", "lint"),
    ("npm", "run", "format:check"),
    ("npm", "run", "typecheck"),
    ("npm", "test"),
    ("node", "scripts/gen-wiki.ts", "--check"),
]


def test_definition_of_done(project: Path) -> None:
    """The project's own lint, format, type check, tests and wiki check, as stack-ci.yml runs them."""
    for cmd in [*DOD, *([("npm", "run", "build")] if (project / "vite.config.ts").is_file() else [])]:
        result = run(project, *cmd)
        assert result.returncode == 0, f"{' '.join(cmd)}:\n{result.stdout}\n{result.stderr}"
    if (project / "scripts/check-manifests.sh").is_file():
        result = run(project, "bash", "scripts/check-manifests.sh")
        assert result.returncode == 0 and "manifests OK" in result.stdout, result.stdout + result.stderr


@pytest.mark.docker
def test_docker_checks(project: Path) -> None:
    """The Definition of done's Docker-only checks, and the CI-only linters."""
    cmds = [("bash", "scripts/check-docs-secrets.sh"), ("bash", "scripts/check-markdown.sh"),
            ("docker", "run", "--rm", "-v", f"{project}:/repo", "-w", "/repo", "rhysd/actionlint:1.7.12", "-color")]  # fmt: skip
    if (project / "Dockerfile").is_file():
        cmds.append(("sh", "-c", "docker run --rm -i hadolint/hadolint:v2.14.0 < Dockerfile"))
    for cmd in cmds:
        result = run(project, *cmd)
        assert result.returncode == 0, f"{' '.join(cmd)}:\n{result.stdout}\n{result.stderr}"


def test_never_asks_base_questions(base_src: Path) -> None:
    """One answer, one place: base's identity is read through _external_data (decision 0001)."""
    config = yaml.safe_load((ROOT / "copier.yml").read_text())
    asked = {k for k, v in config.items() if not k.startswith("_") and v.get("when") is not False}
    assert asked == {"kind", "node_version", "port", "extra_ports", "health_path", "container_image", "contrib",
                     "puid_pgid", "timezone"}  # fmt: skip
    base = yaml.safe_load((base_src / "copier.yml").read_text())
    assert not asked & {k for k in base if not k.startswith("_")}
    assert config["_external_data"] == {"base": ".copier-answers.base.yml"}
    assert config["_answers_file"] == ".copier-answers.stack-typescript.yml"
    assert set(config["kind"]["choices"].values()) == {"service", "cli", "library", "web"}


def test_answers_files(project: Path, variant: str) -> None:
    stack = yaml.safe_load((project / ".copier-answers.stack-typescript.yml").read_text())
    expected = {k: v for k, v in MATRIX[variant].items() if k != "container"}
    assert {k: stack[k] for k in expected} == expected
    # Base's answers are never asked here; the overlay keeps a read-only copy for `copier update`.
    assert not set(stack) & set(BASE)
    assert stack["base_answers"]["project_name"] == "demo"
    assert (project / ".copier-answers.base.yml").is_file() and not (project / ".copier-answers.yml").exists()


def test_reads_base_answers(project: Path) -> None:
    assert (project / "README.md").read_text().startswith("# demo\n")
    assert "A demo project" in (project / "README.md").read_text()
    assert '"name": "demo"' in (project / "package.json").read_text()


@pytest.mark.parametrize(("base", "error"), [
    (None, "needs template-base first: .copier-answers.base.yml is missing"),
    ("v0.9.0", "needs template-base v1.0.0 or later; this project has v0.9.0"),
])  # fmt: skip
def test_needs_base_first(base: str | None, error: str, ts_src: Path, base_src: Path, tmp_path: Path) -> None:
    """Base goes first, at the version the overlay needs; otherwise the copy fails and says why."""
    dst = tmp_path / "p"
    if base:
        copy(stage(base_src, tmp_path / "old-base", tag=base), dst, BASE)
    with pytest.raises(Exception, match=re.escape(error)):
        copy(ts_src, dst, {"kind": "library"})


def test_fills_every_slot_and_prefixes_its_files(project: Path) -> None:
    for slot in SLOTS:
        assert (project / slot).is_file(), slot
    workflows = {p.name for p in (project / ".github/workflows").glob("*.yml")}
    base = {"base-ci.yml", "template-update.yml", "pr-title.yml"}
    ours = {w for w in workflows - base if not w.startswith("container-")}
    assert ours == {"stack-ci.yml", "typescript-release.yml", "typescript-wiki.yml"}
    for d in ("checks.d", "bootstrap.d", "post-update.d"):
        names = [p.name for p in (project / "scripts" / d).glob("*.sh") if "base" not in p.name]
        assert all(re.match(r"\d\d-(typescript|container)", n) for n in names), names


def test_every_template_file_is_marked(project: Path) -> None:
    """Every workflow and script names its owner near its top, so base's contract can check it."""
    for path in [*(project / ".github/workflows").glob("*.yml"), *(p for p in (project / "scripts").rglob("*")
                 if p.is_file() and "__pycache__" not in p.parts)]:  # fmt: skip
        head = "\n".join(path.read_text().splitlines()[:12])
        assert re.search(r"Template-owned: template-[a-z]+", head), path.relative_to(project)


def test_takes_none_of_base_files(base_src: Path, ts_src: Path, tmp_path: Path) -> None:
    """One owner per file: rendered alone (over an empty base answers file), typescript writes none of base's."""
    dst = tmp_path / "p"
    dst.mkdir()
    (dst / ".copier-answers.base.yml").write_text(
        "_commit: v1.0.0\nproject_name: demo\ndescription: d\ngithub_owner: o\n"
    )
    copy(ts_src, dst, {"kind": "service", "container_image": True, "contrib": ["systemd"]})
    assert [f for f in NOT_OURS if (dst / f).exists()] == []


def test_agent_permissions(project: Path) -> None:
    """Agents may run every gh command except releases, repo delete and repo archive (template-base 0001)."""
    permissions = json.loads((project / ".claude/settings.json").read_text())["permissions"]
    assert "Bash(gh:*)" in permissions["allow"]
    for deny in ["Bash(gh release:*)", "Bash(gh api *releases*)", "Bash(gh repo delete:*)", "Bash(gh repo archive:*)",
                 "Edit(.copier-answers.*.yml)", "Edit(CHANGELOG.md)", "Edit(.release-please-manifest.json)"]:  # fmt: skip
        assert deny in permissions["deny"], deny


def test_no_unrendered_jinja(project: Path) -> None:
    leftovers = []
    for path in project.rglob("*"):
        if path.is_file() and not {".git", ".venv", "node_modules", "dist"} & set(path.parts):
            try:
                text = path.read_text()
            except UnicodeDecodeError:
                continue
            # This template's delimiters ({{branch}} and ${{ }} are docker/metadata-action's and Actions').
            if re.search(r"\[\[ |\[% |\[#!", text):
                leftovers.append(str(path.relative_to(project)))
    assert leftovers == []


HEADROOM = 0.75  # the skeleton may use at most 75% of the shared budget (template-base's test_base.py)


def test_stack_md_within_budget(project: Path) -> None:
    size = len((project / "AGENTS.md").read_text()) + len((project / ".agents/stack.md").read_text())
    assert size <= 9000 * HEADROOM, f"AGENTS.md + .agents/stack.md: {size} characters"


def test_stack_ci_holds_no_required_list(project: Path) -> None:
    """stack-ci.yml is reusable, and base-ci's `ci` is the only required check (template-base 0001)."""
    ci = yaml.safe_load((project / ".github/workflows/stack-ci.yml").read_text())
    assert list(ci[True]) == ["workflow_call"]  # `on:` parses as True
    assert "concurrency" not in ci


def test_release_never_names_the_container_overlay(project: Path) -> None:
    """The stack's release workflow is `Release`, which template-container follows; it never calls it."""
    release = (project / ".github/workflows/typescript-release.yml").read_text()
    assert yaml.safe_load(release)["name"] == "Release"
    assert "uses: ./.github/workflows/" not in release  # calls nothing; container-build follows it


def test_container_contrib_needs_the_container_overlay(base_src: Path, ts_src: Path, tmp_path: Path) -> None:
    """docker or k8s manifests come from template-container: without it, the checks say so."""
    project = render(base_src, ts_src, tmp_path / "p", kind="service", container_image=True, contrib=["docker"])
    result = checks(project)
    assert result.returncode != 0 and "template-container isn't applied" in result.stdout, result.stdout


def update(project: Path, ref: str) -> None:
    sh("uvx", "--from", "copier>=9.6,<10", "copier", "update", "-a", ".copier-answers.stack-typescript.yml", "--trust",
       "--skip-tasks", "--defaults", "--conflict", "inline", "--vcs-ref", ref, cwd=project)  # fmt: skip


def test_update_is_a_no_op(base_src: Path, ts_src: Path, tmp_path: Path) -> None:
    """`copier update` from the same version changes nothing: every file is stable under its answers."""
    project = render(base_src, ts_src, tmp_path / "p", kind="service", container_image=False, contrib=["systemd"])
    update(project, "v1.0.0")
    assert sh("git", "status", "--porcelain", cwd=project) == ""


def test_update_keeps_base_values(base_src: Path, ts_src: Path, tmp_path: Path) -> None:
    """A real update (v1.0.0 -> v1.0.1) renders base's values, not blanks, though Copier replays both
    versions in a directory without base's answers file; a project edit survives it."""
    project = render(base_src, ts_src, tmp_path / "p", kind="cli", container_image=False)
    with (project / "src/index.ts").open("a") as f:
        f.write("// a project edit\n")
    commit(project)
    newer = tmp_path / "newer"
    shutil.copytree(ts_src, newer)
    (newer / "template/CONTRIBUTING.md.jinja").write_text(
        (newer / "template/CONTRIBUTING.md.jinja").read_text() + "\nA newer line.\n"
    )
    sh(*GIT, "commit", "-qam", "newer", cwd=newer)
    sh("git", "tag", "v1.0.1", cwd=newer)
    answers = project / ".copier-answers.stack-typescript.yml"
    answers.write_text(answers.read_text().replace(str(ts_src), str(newer)))
    commit(project)
    update(project, "v1.0.1")
    status = sh("git", "status", "--porcelain", cwd=project)
    assert sorted(line[3:] for line in status.splitlines()) == [
        ".copier-answers.stack-typescript.yml",
        "CONTRIBUTING.md",
    ]
    assert "A newer line." in (project / "CONTRIBUTING.md").read_text()
    assert "// a project edit" in (project / "src/index.ts").read_text()
    assert "<<<<<<<" not in sh("git", "diff", cwd=project)
    assert '"name": "demo"' in (project / "package.json").read_text()
