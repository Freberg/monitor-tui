import asyncio
import os
from functools import reduce
from typing import Any, Dict, Iterable

from opensearchpy import AsyncOpenSearch, OpenSearchException

import config.config
from sensors.sensor import Sensor, SensorReading, EMPTY_SENSOR_READING

clients: dict[str, AsyncOpenSearch] = {}


class OpenSearchSensor(Sensor):

    def __init__(self, sensor_configuration: Dict[str, Any], context: Dict[str, Any]):
        super(OpenSearchSensor, self).__init__()
        if sensor_configuration["url"] not in clients:
            clients[sensor_configuration["url"]] = AsyncOpenSearch(
                sensor_configuration["url"],
                http_auth=self.get_http_auth()
            )
        self.client = clients[sensor_configuration["url"]]
        self.context = context
        self.result_fields = sensor_configuration["result_fields"]
        self.index = self.format_json(sensor_configuration["index_pattern"], self.context)
        self.size = self.format_json(sensor_configuration["max_hits"], self.context)

        self.query = self.format_json(sensor_configuration["query"], self.context)
        self.sub_query = self.format_json(sensor_configuration.get("sub_query", None), self.context)
        self.aggregation = self.format_json(sensor_configuration.get("aggregation", None), self.context)
        self.sort = self.format_json(sensor_configuration.get("sort", None), self.context)

        self.args = {
            "size": self.format_json(sensor_configuration["max_hits"], self.context)
        }

        if self.sub_query is not None:
            self.args["query"] = {"bool": {"must": [self.query, self.sub_query]}}
        else:
            self.args["query"] = {"bool": {"must": [self.query]}}
        if self.sort is not None:
            self.args["sort"] = sensor_configuration["sort"]
        if self.aggregation is not None:
            self.args["aggs"] = {"groups": self.aggregation}

        self.reverse_results = sensor_configuration.get("reverse_results", False)

    @staticmethod
    def get_http_auth():
        if os.getenv("OPEN_SEARCH_USER") is not None:
            return os.getenv("OPEN_SEARCH_USER"), os.getenv("OPEN_SEARCH_PASS")
        return None

    async def search(self):
        return await self.client.search(body=self.args, index=self.index)

    def get_sensor_fields(self) -> Iterable[str]:
        return self.result_fields

    async def fetch_sensor_data(self) -> Iterable[SensorReading]:
        try:
            results = await self.search()
        except OpenSearchException as opensearch_exception:
            return [SensorReading([str(type(opensearch_exception).__name__)])]

        if self.aggregation is not None:
            results = list(map(lambda result: result, results["aggregations"]["groups"]["buckets"]))
            if not results:
                return [EMPTY_SENSOR_READING]
            results = map(lambda result: result["group_docs"]["hits"]["hits"], results)
            results = reduce(lambda r1, r2: r1 + r2, results, [])
            results = map(lambda result: result["_source"], results)
        else:
            results = map(lambda result: result["_source"], results.get("hits", {}).get("hits", []))

        results = map(lambda result: SensorReading(self.strip_message(result), result), results)

        if self.reverse_results:
            results = list(results)
            results.reverse()

        return results

    def strip_message(self, message: Dict[str, Any]) -> Iterable[str]:
        return map(lambda result_field: str(message.get(result_field, "N/A")), self.result_fields)


if __name__ == '__main__':
    service_config = config.config.read_config().get_services()[5]
    sensor_config = service_config.get_sensors()[0]
    context = sensor_config.yaml_config.get("context", {}) | service_config.get_context()
    sensor = OpenSearchSensor(sensor_config.yaml_config, context)
    readings = asyncio.get_event_loop().run_until_complete(sensor.fetch_sensor_data())
    data = [list(reading.values) for reading in readings]
    sequence = [float(x[0]) for x in data]
    print(len(data))
    print(data)
    print(len(sequence))
    print(sequence)
