from typing import Dict, Any

from rich.text import Text
from textual.app import ComposeResult
from textual.timer import Timer
from textual.widgets import Static

from components.sensor.sensor_table import SensorTable
from config.config import SensorConfig
from sensors.sensor_resolver import resolve_sensor


class SensorContent(Static):
    sensor_data = None
    update_timer: Timer = None

    def __init__(self, sensor_config: SensorConfig, context: Dict[str, Any]) -> None:
        super().__init__()
        self.sensor_config = sensor_config
        self.sensor = resolve_sensor(sensor_config, context)
        self.poll_wait_seconds = sensor_config.get_poll_wait_seconds()

    def compose(self) -> ComposeResult:
        """Create child widgets for the sensor."""
        yield Static(renderable=Text(self.sensor_config.get_name()))
        yield SensorTable(self.sensor_config.get_name(), self.sensor.get_sensor_fields(),
                          self.sensor_config.complete_refresh())

    async def on_mount(self) -> None:
        """Event handler called when sensor widget is added to the app."""
        self.update_timer = self.set_interval(self.poll_wait_seconds, self.update_sensor_data)
        await self.update_sensor_data()

    async def update_sensor_data(self):
        """Fetch new sensor data."""
        table = self.query_one(SensorTable)
        self.sensor_data = await self.sensor.fetch_sensor_data()
        table.update_data(self.sensor_data)

    def show(self, show: bool) -> None:
        if show:
            self.update_timer.resume()
        else:
            self.update_timer.pause()
