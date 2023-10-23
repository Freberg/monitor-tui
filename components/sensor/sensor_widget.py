from typing import Iterable

from textual.widget import Widget

from sensors.sensor import SensorReading


class SensorWidget(Widget):

    def __init__(self) -> None:
        super().__init__()

    def update_data(self, rows: Iterable[SensorReading]):
        pass


