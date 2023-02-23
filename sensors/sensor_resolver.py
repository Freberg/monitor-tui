from typing import Dict, Any

from config.config import SensorConfig
from sensors.elastic.elastic_sensor import ElasticSensor
from sensors.prometheus.prometheus_sensor import PrometheusSensor
from sensors.sensor import Sensor


def resolve_sensor(sensor_config: SensorConfig, context: Dict[str, Any]) -> Sensor:
    context = sensor_config.yaml_config.get("context", {}) | context
    if sensor_config.get_sensor_type() == "prometheus":
        return PrometheusSensor(sensor_config.yaml_config, context)
    elif sensor_config.get_sensor_type() == "elastic":
        return ElasticSensor(sensor_config.yaml_config, context)
    else:
        Exception(f"Unhandled sensor type: {sensor_config.get_sensor_type()}")
