from config.config import SensorConfig
from sensors.elastic.elastic_sensor import ElasticSensor
from sensors.prometheus.prometheus_sensor import PrometheusSensor
from sensors.sensor import Sensor


def resolve_sensor(sensor_config: SensorConfig) -> Sensor:
    if sensor_config.get_sensor_type() == "prometheus":
        return PrometheusSensor(sensor_config.yaml_config)
    elif sensor_config.get_sensor_type() == "elastic":
        return ElasticSensor(sensor_config.yaml_config)
    else:
        Exception(f"Unhandled sensor type: {sensor_config.get_sensor_type()}")
