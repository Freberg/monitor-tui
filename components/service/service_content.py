from typing import Optional

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Static

from components.sensor.sensor_content import SensorContent
from config.config import Config, ServiceConfig


class ServiceContent(Static):
    selected_service_config = reactive(None)

    def __init__(self, config: Config, id: Optional[str] = None) -> None:
        super().__init__(id=id)
        self.config = config

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield ServiceContentData(None, id="service-content-data")

    def update_selected_service(self, service: ServiceConfig):
        """Update the service which to display sensor data for by replacing the content using a different config."""
        self.selected_service_config = service
        content_id = f"service-content-data-{service.get_name().replace(' ', '_')}"
        should_create_new_content = True

        for content_data in self.query(ServiceContentData):
            if content_data.id == content_id:
                content_data.show(True)
                should_create_new_content = False
            else:
                content_data.show(False)

        if should_create_new_content:
            content_data = ServiceContentData(service, id=content_id)
            content_data.show(True)
            self.mount(content_data)


class ServiceContentData(Static):

    def __init__(self, service_config: Optional[ServiceConfig], id: Optional[str] = None):
        super().__init__(id=id)
        self.service_config = service_config

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        if self.service_config is None:
            sensor_content = []
        else:
            sensor_content = [SensorContent(sensor_config, self.service_config.get_context())
                              for sensor_config in self.service_config.get_sensors()]

        yield VerticalScroll(*sensor_content)

    def show(self, show: bool) -> None:
        self.set_class(show, "-show-content")
        for sensor_content in self.query(SensorContent):
            sensor_content.show(show)
