"""Tests for desktop app bridge helpers."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from fast_resume.adapters.base import Session
from fast_resume.desktop import (
    DesktopAppTarget,
    build_handoff_prompt,
    get_desktop_target,
    get_handoff_targets,
    get_native_desktop_target,
    get_installed_desktop_targets,
    open_in_desktop_app,
)


class TestDesktopTargets:
    """Tests for desktop target discovery."""

    def test_get_desktop_target_returns_known_target(self):
        """Known target ids resolve to target metadata."""
        target = get_desktop_target("codex")
        assert target is not None
        assert target.label == "Codex"

    def test_get_native_desktop_target_for_codex(self):
        """Codex agent resolves to Codex desktop app when installed."""
        with patch("pathlib.Path.exists", return_value=True):
            target = get_native_desktop_target("codex")
        assert target is not None
        assert target.id == "codex"

    def test_get_installed_desktop_targets_filters_missing_apps(self, tmp_path):
        """Only installed targets are returned."""
        (tmp_path / "Codex.app").mkdir()
        (tmp_path / "Claude.app").mkdir()

        with patch(
            "fast_resume.desktop.DESKTOP_APP_TARGETS",
            (
                DesktopAppTarget(
                    id="codex",
                    label="Codex",
                    bundle_id="com.openai.codex",
                    app_path=tmp_path / "Codex.app",
                ),
                DesktopAppTarget(
                    id="claude",
                    label="Claude",
                    bundle_id="com.anthropic.claudefordesktop",
                    app_path=tmp_path / "Claude.app",
                ),
                DesktopAppTarget(
                    id="opencode",
                    label="OpenCode",
                    bundle_id="ai.opencode.desktop",
                    app_path=tmp_path / "OpenCode.app",
                ),
            ),
        ):
            targets = get_installed_desktop_targets()
        assert [target.id for target in targets] == ["codex", "claude"]

    def test_get_handoff_targets_excludes_native_target(self):
        """Cross-app handoff options should not include the current agent app."""
        with patch("fast_resume.desktop.Path.exists", return_value=True):
            targets = get_handoff_targets("codex")
        ids = [target.id for target in targets]
        assert "codex" not in ids
        assert "claude" in ids


class TestDesktopLaunch:
    """Tests for desktop app launching."""

    def test_open_in_desktop_app_with_directory(self, tmp_path):
        """Desktop app launch uses bundle id plus directory."""
        target = DesktopAppTarget(
            id="codex",
            label="Codex",
            bundle_id="com.openai.codex",
            app_path=tmp_path / "Codex.app",
        )
        target.app_path.mkdir()
        with (
            patch("fast_resume.desktop.sys.platform", "darwin"),
            patch("fast_resume.desktop.subprocess.run") as mock_run,
        ):
            ok, message = open_in_desktop_app(target, "/tmp/project")

        assert ok is True
        assert "Opened Codex" in message
        mock_run.assert_called_once_with(
            ["open", "-b", "com.openai.codex", "/tmp/project"],
            check=True,
            capture_output=True,
        )

    def test_open_in_desktop_app_handles_missing_install(self, tmp_path):
        """Missing desktop apps fail cleanly."""
        target = DesktopAppTarget(
            id="opencode",
            label="OpenCode",
            bundle_id="ai.opencode.desktop",
            app_path=tmp_path / "OpenCode.app",
        )
        with patch("fast_resume.desktop.sys.platform", "darwin"):
            ok, message = open_in_desktop_app(target, "/tmp/project")

        assert ok is False
        assert "not installed" in message


class TestHandoffPrompt:
    """Tests for handoff prompt generation."""

    def test_build_handoff_prompt_contains_session_metadata(self):
        """Handoff prompt should carry useful session context."""
        target = get_desktop_target("claude")
        assert target is not None
        session = Session(
            id="antigravity:abc123",
            agent="antigravity",
            title="Fix the sync bug",
            directory="/Users/test/project",
            timestamp=datetime(2026, 5, 19, 20, 30),
            content="User asked to fix sync bug.\nAssistant inspected adapters.",
        )

        prompt = build_handoff_prompt(session, target)

        assert "Source agent: antigravity" in prompt
        assert "Target app" not in prompt  # prompt should stay concise
        assert "Fix the sync bug" in prompt
        assert "/Users/test/project" in prompt
        assert "cross-app handoff" in prompt
