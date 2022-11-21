from typing import Iterable

from rich.console import RenderableType
from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static, DataTable

from sensors.sensor import SensorReading


class SensorTable(Widget):

    def __init__(self, name: str, columns: Iterable[RenderableType], complete_refresh: bool):
        super(SensorTable, self).__init__()
        self.table_name = name
        self.columns = columns
        self.complete_refresh = complete_refresh

    def compose(self) -> ComposeResult:
        yield Static(renderable=Text(self.table_name))
        yield DataTable(name=self.table_name)

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.columns)

    def update_rows(self, rows: Iterable[SensorReading]):
        if self.complete_refresh:
            self.clear()
        table = self.query_one(DataTable)
        table.add_rows(map(lambda row: row.get_values(), rows))
        table.add_columns()
        table.refresh()

    def clear(self):
        table = self.query_one(DataTable)
        table.row_count = 0
        table._clear_caches()
        table._y_offsets.clear()
        table.data.clear()
        table.rows.clear()
        table._line_no = 0
