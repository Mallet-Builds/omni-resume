"""Modal dialogs for the TUI."""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from ..desktop import DesktopAppTarget
from .styles import APP_PICKER_MODAL_CSS, YOLO_MODAL_CSS


class YoloModeModal(ModalScreen[bool]):
    """Modal to choose yolo mode for resume."""

    BINDINGS = [
        Binding("y", "select_yolo", "Yolo Mode", show=False),
        Binding("n", "select_normal", "Normal", show=False),
        Binding("escape", "dismiss", "Cancel", show=False),
        Binding("enter", "select_focused", "Select", show=False),
        Binding("left", "focus_normal", "Left", show=False),
        Binding("right", "focus_yolo", "Right", show=False),
    ]

    CSS = YOLO_MODAL_CSS

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Resume with yolo mode?", id="title")
            with Horizontal(id="buttons"):
                yield Button("No", id="normal-btn")
                yield Button("Yolo", id="yolo-btn")

    def on_mount(self) -> None:
        """Focus the first button when modal opens."""
        self.query_one("#normal-btn", Button).focus()

    def action_toggle_focus(self) -> None:
        """Toggle focus between the two buttons."""
        if self.focused and self.focused.id == "yolo-btn":
            self.query_one("#normal-btn", Button).focus()
        else:
            self.query_one("#yolo-btn", Button).focus()

    def action_focus_normal(self) -> None:
        """Focus the normal button."""
        self.query_one("#normal-btn", Button).focus()

    def action_focus_yolo(self) -> None:
        """Focus the yolo button."""
        self.query_one("#yolo-btn", Button).focus()

    def action_select_focused(self) -> None:
        """Select whichever button is currently focused."""
        focused = self.focused
        if focused and focused.id == "yolo-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_select_yolo(self) -> None:
        self.dismiss(True)

    def action_select_normal(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#yolo-btn")
    def on_yolo_pressed(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#normal-btn")
    def on_normal_pressed(self) -> None:
        self.dismiss(False)


class DesktopAppPickerModal(ModalScreen[str | None]):
    """Modal to choose a desktop app target for cross-app handoff."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", show=False),
        Binding("enter", "select_focused", "Select", show=False),
        Binding("tab", "focus_next", "Next", show=False),
        Binding("down", "focus_next", "Down", show=False),
        Binding("up", "focus_previous", "Up", show=False),
        Binding("j", "focus_next", "Down", show=False),
        Binding("k", "focus_previous", "Up", show=False),
    ]

    CSS = APP_PICKER_MODAL_CSS

    def __init__(self, targets: list[DesktopAppTarget]) -> None:
        super().__init__()
        self.targets = targets

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Open Handoff In...", id="title")
            yield Label(
                "This starts a new thread in the target app and copies a handoff prompt.",
                id="subtitle",
            )
            for target in self.targets:
                yield Button(target.label, id=f"target-{target.id}")

    def on_mount(self) -> None:
        """Focus the first option when modal opens."""
        if self.targets:
            self.query_one(f"#target-{self.targets[0].id}", Button).focus()

    def action_select_focused(self) -> None:
        """Select the currently focused target."""
        focused = self.focused
        if focused and focused.id and focused.id.startswith("target-"):
            self.dismiss(focused.id.removeprefix("target-"))

    def action_focus_next(self) -> None:
        """Move focus to the next target button."""
        self.focus_next(Button)

    def action_focus_previous(self) -> None:
        """Move focus to the previous target button."""
        self.focus_previous(Button)

    @on(Button.Pressed)
    def on_target_pressed(self, event: Button.Pressed) -> None:
        target_id = event.button.id
        if target_id and target_id.startswith("target-"):
            self.dismiss(target_id.removeprefix("target-"))
