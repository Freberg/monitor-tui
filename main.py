from typing import Type, Optional

from textual import events
from textual.app import App, ComposeResult, CSSPathType
from textual.containers import Container, Vertical
from textual.driver import Driver
from textual.reactive import var
from textual.widgets import Header, Static, Footer

from components.service.service_content import ServiceContent
from components.service.service_tree import ServiceTree
from config.config import read_config, ServiceConfig, SensorConfig


class ServiceStatusApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "css/main.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "toggle_services", "Toggle Services"),
        ("q", "quit", "Quit"),
    ]

    show_tree = var(True)

    def __init__(self, driver_class: Optional[Type[Driver]] = None, css_path: CSSPathType = None,
                 watch_css: bool = False):
        super().__init__(driver_class, css_path, watch_css)
        self.config = read_config()
        self.title = self.config.get_title()

    def watch_show_tree(self, show_tree: bool) -> None:
        """Called when show_tree is modified."""
        self.set_class(show_tree, "-show-tree")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Container(
            Vertical(ServiceTree(self.config.get_services()), id="tree-view"),
            Vertical(ServiceContent(self.config, id="content-view"))
        )
        yield Footer()

    def on_mount(self, event: events.Mount) -> None:
        self.query_one(ServiceTree).focus()

    def on_service_tree_selected(self, message: ServiceTree.Selected) -> None:
        """Called when a non group is selected in the service tree."""
        service_info = self.query_one(ServiceContent)
        service_info.update_selected_service(message.service.service_config)
        self.sub_title = message.service.name

    def action_toggle_dark(self) -> None:
        """Called in response to key binding to toggle dark mode."""
        self.dark = not self.dark

    def action_toggle_services(self) -> None:
        """Called in response to key binding to toggle service tree."""
        self.show_tree = not self.show_tree


if __name__ == "__main__":
    app = ServiceStatusApp()
    app.run()
