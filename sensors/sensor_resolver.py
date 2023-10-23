from typing import Dict, Any

from config.config import SensorConfig, SensorType
from sensors.elastic.elastic_sensor import ElasticSensor
from sensors.prometheus.prometheus_sensor import PrometheusSensor
from sensors.sensor import Sensor


def resolve_sensor(sensor_config: SensorConfig, context: Dict[str, Any]) -> Sensor:
    context = sensor_config.yaml_config.get("context", {}) | context
    match sensor_config.get_sensor_type():
        case SensorType.PROMETHEUS:
            return PrometheusSensor(sensor_config.yaml_config, context)
        case SensorType.ELASTIC:
            return ElasticSensor(sensor_config.yaml_config, context)
        case _:
            Exception(f"Unhandled sensor type: {sensor_config.get_sensor_type()}")
