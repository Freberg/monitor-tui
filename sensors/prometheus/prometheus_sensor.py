import asyncio
from string import Template
from typing import Any, Dict, Iterable

from prometheus_api_client import PrometheusConnect, PrometheusApiClientException
from requests import RequestException
from rich.console import RenderableType

import config.config
from sensors.sensor import Sensor, SensorReading

clients: dict[str, PrometheusConnect] = {}


class PrometheusSensor(Sensor):
    def __init__(self, sensor_configuration: Dict[str, Any], context: Dict[str, Any]) -> None:
        super().__init__()
        if sensor_configuration["url"] not in clients:
            clients[sensor_configuration["url"]] = PrometheusConnect(url=sensor_configuration["url"], disable_ssl=True)
        self.client = clients[sensor_configuration["url"]]

        self.metrics = sensor_configuration["metrics"]
        self.context = context

    def get_sensor_fields(self) -> Iterable[RenderableType]:
        return map(lambda metric: metric["name"], self.metrics)

    async def fetch_sensor_data(self) -> Iterable[SensorReading]:
        return await asyncio.get_event_loop().run_in_executor(None, self.fetch_sensor_readings)

    def fetch_sensor_readings(self) -> Iterable[SensorReading]:
        formatted_readings = map(lambda measurement: self.format_measurement(measurement), self.fetch_measurements())
        yield SensorReading(formatted_readings)

    def fetch_measurements(self) -> Iterable[Any]:
        return map(self.fetch_measurement, self.metrics)

    def fetch_measurement(self, metric: Dict[str, Any]) -> Any:
        try:
            return self.client.custom_query(self.format_query(metric["query"]))
        except RequestException:
            return "RequestException"
        except PrometheusApiClientException:
            return "PrometheusApiClientException"

    def format_query(self, query: str) -> str:
        if self.context is None:
            return query
        return Template(query).substitute(**self.context)

    @staticmethod
    def format_measurement(measurement: Any) -> str:
        if isinstance(measurement, str):
            return measurement
        return str(measurement[0]["value"][1])


if __name__ == '__main__':
    service = config.config.read_config().get_services()[0]
    sensor = PrometheusSensor(service.get_sensors()[0].yaml_config, service.get_context())
    tabular_data = asyncio.get_event_loop().run_until_complete(sensor.fetch_sensor_data())
    print([list(r.values) for r in tabular_data])
