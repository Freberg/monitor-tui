from typing import Optional, Iterable

from rich.console import RenderableType


class SensorReading:
    def __init__(self, values: Iterable[RenderableType], details: Optional[RenderableType] = None) -> None:
        super().__init__()
        self.values = values
        self.details = details

    def get_values(self) -> Iterable[RenderableType]:
        return self.values

    def get_details(self) -> Optional[RenderableType]:
        return self.details


class Sensor:
    def get_table_headers(self) -> Iterable[RenderableType]:
        pass

    async def fetch_tabular_data(self) -> Iterable[SensorReading]:
        pass


EMPTY_SENSOR_READING = SensorReading([])






