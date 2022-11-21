import asyncio
from typing import Any, Dict, Iterable

from prometheus_api_client import PrometheusConnect, PrometheusApiClientException
from requests import RequestException
from rich.console import RenderableType

from sensors.sensor import Sensor, SensorReading

loop = asyncio.get_event_loop()


class PrometheusSensor(Sensor):
    def __init__(self, sensor_configuration: Dict[str, Any]) -> None:
        super().__init__()
        self.url = sensor_configuration["url"]
        self.metrics = sensor_configuration["metrics"]
        self.additional_label = sensor_configuration["additional_label"]
        self.client = PrometheusConnect(url=self.url, disable_ssl=True)

    def get_table_headers(self) -> Iterable[RenderableType]:
        return map(lambda metric: metric["name"], self.metrics)

    async def fetch_tabular_data(self) -> Iterable[SensorReading]:
        return await loop.run_in_executor(None, self.fetch_sensor_readings)

    def fetch_sensor_readings(self) -> Iterable[SensorReading]:
        formatted_readings = map(lambda measurement: self.format_measurement(measurement), self.fetch_measurements())
        return map(lambda formatted_reading: SensorReading(formatted_readings), formatted_readings)

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
        return query.format(additional_label=self.additional_label)

    @staticmethod
    def format_measurement(measurement: Any) -> str:
        return str(measurement[0]["value"][1])


