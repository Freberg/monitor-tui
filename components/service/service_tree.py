from dataclasses import dataclass
from typing import List, Optional

from rich.style import Style
from rich.text import Text
from textual.message import Message, MessageTarget
from textual.widgets._tree import Tree
from textual.widgets.tree import TreeNode

from config.config import ServiceConfig


@dataclass
class ServiceEntry:
    name: str
    is_group: bool
    service_config: Optional[ServiceConfig]


class ServiceTree(Tree[ServiceEntry]):
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
                if len(matching_children) == 0:
                    next_node = ServiceEntry(group_name, True, None)
                    parent_group.add(group_name, next_node)
                parent_group = [child for child in parent_group.children if child.data.name == group_name][0]
            parent_group.add(service.get_name(), ServiceEntry(service.get_name(), False, service))

        self.root.expand()
        self.refresh(layout=True)

    def on_tree_node_expanded(self, event: Tree.NodeSelected) -> None:
        event.stop()
        entry = event.node.data
        if entry is None:
            return
        if entry.is_group:
            return
        else:
            self.post_message_no_wait(self.Selected(self, entry))

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.stop()
        entry = event.node.data
        if not entry.is_group:
            self.post_message_no_wait(self.Selected(self, entry))
        else:
            return

    def render_label(self, node: TreeNode[ServiceEntry], base_style: Style, style: Style):
        node_label = node._label.copy()
        node_label.stylize(style)

        if node._allow_expand and node.data.is_group:
            prefix = ("- " if node.is_expanded else "+ ", base_style)
        else:
            prefix = ""

        text = Text.assemble(prefix, node_label)
        return text
