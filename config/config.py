import os
from enum import Enum
from typing import Any, List, Dict

import yaml


class SensorType(Enum):
    ELASTIC = 1
    PROMETHEUS = 2
    OPEN_SEARCH = 3


class ComponentType(Enum):
    TABLE = 1
    SPARKLINE = 2


class SensorConfig:
    def __init__(self, yaml_config: Dict[str, Any]) -> None:
        super().__init__()
        self.yaml_config = yaml_config

    def get_name(self):
        return self.yaml_config["name"]

    def get_sensor_type(self) -> SensorType:
        return SensorType[str(self.yaml_config["sensor_type"]).upper()]

    def get_component_type(self) -> ComponentType:
        return ComponentType[self.yaml_config.get("component_type", "table").upper()]

    def complete_refresh(self) -> bool:
        return self.yaml_config.get("complete_refresh", True)

    def get_poll_wait_seconds(self) -> int:
        return self.yaml_config.get("poll_wait_seconds", 30)


class ServiceConfig:
    def __init__(self, yaml_config: Dict[str, Any]) -> None:
        super().__init__()
        self.yaml_config = yaml_config

    def get_name(self):
        return self.yaml_config["name"]

    def get_sensors(self) -> List[SensorConfig]:
        return [SensorConfig(service) for service in self.yaml_config.get("sensors", [])]

    def get_hierarchy(self) -> List[str]:
        return self.yaml_config.get("hierarchy", "").split("/")

    def get_context(self) -> Dict[str, Any]:
        return self.yaml_config.get("context", {})


class Config:
    def __init__(self, yaml_config: Dict[str, Any]) -> None:
        super().__init__()
        self.yaml_config = yaml_config

    def get_services(self) -> List[ServiceConfig]:
        return [ServiceConfig(service) for service in self.yaml_config["services"]]

    def get_title(self):
        return self.yaml_config.get("title", "Service Monitoring App")


def read_config(path: str = os.getenv("CONFIG_FILE_PATH", default="config.yaml")) -> Config:
    with open(path) as file:
        yaml_config = yaml.load(file, Loader=yaml.FullLoader)
    return Config(yaml_config)

