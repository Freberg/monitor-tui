from typing import Iterable

from rich.console import RenderableType
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable

from sensors.sensor import SensorReading


class SensorTable(Widget):

    def __init__(self, name: str, columns: Iterable[RenderableType], complete_refresh: bool):
        super(SensorTable, self).__init__()
        self.table_name = name
        self.columns = columns
        self.complete_refresh = complete_refresh

    def compose(self) -> ComposeResult:
        yield DataTable(name=self.table_name, cursor_type="row")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.columns)

    def update_data(self, rows: Iterable[SensorReading]):
        table = self.query_one(DataTable)
        if self.complete_refresh:
            table.clear()
        table.add_rows(map(lambda row: row.get_values(), rows))

        table.add_rows([[]])
        self.set_styles(f"height: {len(table.rows) + 3};")
        self.refresh()

