from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional

from rich.console import RenderableType
from rich.text import Text
from textual.message import Message, MessageTarget
from textual.widgets._tree_control import TreeControl, TreeNode
from config.config import ServiceConfig


@dataclass
class ServiceEntry:
    name: str
    is_group: bool
    service_config: Optional[ServiceConfig]


class ServiceTree(TreeControl[ServiceEntry]):
    class Selected(Message):
        def __init__(self, sender: MessageTarget, service: ServiceEntry) -> None:
            super().__init__(sender)
            self.service = service

    def __init__(self, service_configs: List[ServiceConfig]) -> None:
        data = ServiceEntry("sensors", True, None)
        super().__init__("sensors", data)
        self.service_configs = service_configs

    def on_mount(self) -> None:
        for service in self.service_configs:
            parent_group = self.root
            for group_name in service.get_hierarchy():
                if group_name == "":
                    continue
                matching_children = [child for child in parent_group.children if child.data.name == group_name]
                if len(matching_children) is 0:
                    next_node = ServiceEntry(group_name, True, None)
                    parent_group.add(group_name, next_node)
                parent_group = [child for child in parent_group.children if child.data.name == group_name][0]
            parent_group.add(service.get_name(), ServiceEntry(service.get_name(), False, service))

        self.root.expand(True)
        self.refresh(layout=True)

    async def on_tree_control_node_selected(self, message: TreeControl.NodeSelected[ServiceEntry]) -> None:
        entry = message.node.data
        if not entry.is_group:
            await self.emit(self.Selected(self, entry))
        else:
            message.node.toggle()

    def render_node(self, node: TreeNode[ServiceEntry]) -> RenderableType:
        return self.render_tree_label(
            node,
            node.data.is_group,
            node.expanded,
            node.is_cursor,
            node.id == self.hover_node,
            self.has_focus,
        )

    @lru_cache(maxsize=1024 * 32)
    def render_tree_label(self, node: TreeNode[ServiceEntry],
                          is_group: bool,
                          expanded: bool,
                          is_cursor: bool,
                          is_hover: bool,
                          has_focus: bool,
                          ) -> RenderableType:
        meta = {
            "@click": f"click_label({node.id})",
            "tree_node": node.id,
            "cursor": node.is_cursor,
        }
        label = Text(node.label) if isinstance(node.label, str) else node.label
        if is_hover:
            label.stylize("underline")
        if is_group:
            label.stylize("bold")
            icon = "-" if expanded else "+"
        else:
            icon = ""
            label.highlight_regex(r"\..*$", "italic")

        if label.plain.startswith("."):
            label.stylize("dim")

        if is_cursor and has_focus:
            cursor_style = self.get_component_styles("tree--cursor").rich_style
            label.stylize(cursor_style)

        icon_label = Text(f"{icon} ", no_wrap=True, overflow="ellipsis") + label
        icon_label.apply_meta(meta)
        return icon_label
