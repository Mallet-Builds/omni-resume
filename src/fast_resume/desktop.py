"""Desktop app bridge for opening agent apps and cross-app handoffs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess
import sys

from .adapters.base import Session


@dataclass(frozen=True)
class DesktopAppTarget:
    """A supported desktop app target."""

    id: str
    label: str
    bundle_id: str
    app_path: Path


DESKTOP_APP_TARGETS: tuple[DesktopAppTarget, ...] = (
    DesktopAppTarget(
        id="codex",
        label="Codex",
        bundle_id="com.openai.codex",
        app_path=Path("/Applications/Codex.app"),
    ),
    DesktopAppTarget(
        id="claude",
        label="Claude",
        bundle_id="com.anthropic.claudefordesktop",
        app_path=Path("/Applications/Claude.app"),
    ),
    DesktopAppTarget(
        id="antigravity",
        label="Antigravity",
        bundle_id="com.google.antigravity",
        app_path=Path("/Applications/Antigravity.app"),
    ),
    DesktopAppTarget(
        id="antigravity-ide",
        label="Antigravity IDE",
        bundle_id="com.google.antigravity-ide",
        app_path=Path("/Applications/Antigravity IDE.app"),
    ),
    DesktopAppTarget(
        id="opencode",
        label="OpenCode",
        bundle_id="ai.opencode.desktop",
        app_path=Path("/Applications/OpenCode.app"),
    ),
)

_TARGETS_BY_ID = {target.id: target for target in DESKTOP_APP_TARGETS}

NATIVE_DESKTOP_TARGET_BY_AGENT = {
    "antigravity": "antigravity-ide",
    "claude": "claude",
    "codex": "codex",
    "opencode": "opencode",
}


def get_desktop_target(target_id: str) -> DesktopAppTarget | None:
    """Get a desktop target by identifier."""
    return _TARGETS_BY_ID.get(target_id)


def get_installed_desktop_targets() -> list[DesktopAppTarget]:
    """Get desktop targets that are installed locally."""
    return [target for target in DESKTOP_APP_TARGETS if target.app_path.exists()]


def get_native_desktop_target(agent: str) -> DesktopAppTarget | None:
    """Get the preferred desktop target for an agent."""
    target_id = NATIVE_DESKTOP_TARGET_BY_AGENT.get(agent)
    if not target_id:
        return None
    target = get_desktop_target(target_id)
    if target and target.app_path.exists():
        return target
    return None


def get_handoff_targets(agent: str) -> list[DesktopAppTarget]:
    """Get installed desktop apps suitable for a cross-app handoff."""
    native_target = get_native_desktop_target(agent)
    return [
        target
        for target in get_installed_desktop_targets()
        if native_target is None or target.id != native_target.id
    ]


def open_in_desktop_app(
    target: DesktopAppTarget, directory: str | None = None
) -> tuple[bool, str]:
    """Open a desktop app, optionally targeting a project directory."""
    if sys.platform != "darwin":
        return False, "Desktop app launch is only implemented on macOS."

    if not target.app_path.exists():
        return False, f"{target.label} is not installed."

    cmd = ["open", "-b", target.bundle_id]
    if directory:
        cmd.append(directory)

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        if directory:
            return True, f"Opened {target.label} in {directory}"
        return True, f"Opened {target.label}"
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode().strip() if exc.stderr else ""
        detail = f": {stderr}" if stderr else ""
        return False, f"Failed to open {target.label}{detail}"


def build_handoff_prompt(session: Session, target: DesktopAppTarget) -> str:
    """Build a handoff prompt for starting a new thread in another app."""
    excerpt = session.content.strip()
    if len(excerpt) > 1800:
        excerpt = excerpt[:1800].rsplit(" ", 1)[0] + "..."

    timestamp = session.timestamp.strftime("%Y-%m-%d %H:%M")
    directory = session.directory or "n/a"

    return "\n".join(
        [
            f"Open this project in {target.label} and continue from the prior session context below.",
            "",
            f"Source agent: {session.agent}",
            f"Session title: {session.title}",
            f"Session id: {session.id}",
            f"Session time: {timestamp}",
            f"Working directory: {directory}",
            "",
            "Important:",
            "- This is a cross-app handoff, not an exact native resume.",
            "- Treat the excerpt as context only and verify the live repo state before acting.",
            "",
            "Session excerpt:",
            excerpt or "(no content available)",
            "",
            "Continue from here.",
        ]
    )
