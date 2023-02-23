import json
from string import Template
from typing import Optional, Iterable, Dict, Any

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
    def get_sensor_fields(self) -> Iterable[RenderableType]:
        pass

    async def fetch_sensor_data(self) -> Iterable[SensorReading]:
        pass

    @staticmethod
    def format(unformatted: Any, context: Dict[str, Any]):
        return Template(str(unformatted)).substitute(**context)

    @staticmethod
    def format_json(json_dict: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if context is None:
            return json_dict
        untemplated = json.dumps(json_dict)
        templated = Template(untemplated).substitute(**context)
        return json.loads(templated)


EMPTY_SENSOR_READING = SensorReading([])






