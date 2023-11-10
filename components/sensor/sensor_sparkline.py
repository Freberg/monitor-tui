from statistics import mean
from typing import Iterable

from rich.console import RenderableType
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Sparkline, Static

from components.sensor.sensor_widget import SensorWidget
from sensors.sensor import SensorReading


class SensorSparkline(SensorWidget):
    DEFAULT_CSS = """
    SensorSparkline {
        width: 1fr;
        height: auto;
        layout: grid;
    }
    """

    def __init__(self, columns: Iterable[RenderableType]):
        super(SensorSparkline, self).__init__()
        self.columns = list(columns)
        self.latest_readings = [None] * len(self.columns)

    def compose(self) -> ComposeResult:
        yield Static()
        for i, column in enumerate(self.columns):
            yield Horizontal(
                Static(column),
                Static(classes="latest_reading"),
                Sparkline(summary_function=mean)
            )

    def on_mount(self) -> None:
        sparklines = self.query(Sparkline)
        for sparkline in sparklines:
            sparkline.set_loading(True)
        self.set_styles(f"height: {len(self.columns) * 2 + 1}; align-vertical: middle;")

    def update_data(self, readings: Iterable[SensorReading]):
        data = [list(reading.values) for reading in readings]

        if len(data[0]) == len(self.columns):
            self.latest_readings = data[-1]
            sparklines = self.query(Sparkline)
            for i, sparkline in enumerate(sparklines):
                sparkline.set_loading(False)
                sparkline.data = [float(x[i]) for x in data]
        else:
            self.latest_readings = [data[0][0]] * len(self.columns)

        statics = self.query(selector=".latest_reading")
        for i, static in enumerate(statics):
            static.update(self.latest_readings[i])

        self.refresh()
