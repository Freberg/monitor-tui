from functools import reduce
from typing import Any, Dict, Union, Iterable

import elasticsearch.exceptions
from elasticsearch import AsyncElasticsearch

from sensors.sensor import Sensor, SensorReading, EMPTY_SENSOR_READING

elastic_clients: dict[str, AsyncElasticsearch] = {}


class ElasticSensor(Sensor):

    def __init__(self, sensor_configuration: Union[str, Dict[str, Any]]):
        super(ElasticSensor, self).__init__()
        if sensor_configuration["url"] not in elastic_clients:
            elastic_clients[sensor_configuration["url"]] = AsyncElasticsearch(sensor_configuration["url"])
        self.client = elastic_clients[sensor_configuration["url"]]
        self.url = sensor_configuration["url"]
        self.index_pattern = sensor_configuration["index_pattern"]
        self.sort = sensor_configuration.get("sort", None)
        self.query = sensor_configuration["query"]
        self.aggregation = sensor_configuration.get("aggregation", None)
        self.max_hits = sensor_configuration["max_hits"]
        self.aggregation_field = sensor_configuration.get("aggregation_field", None)
        self.result_fields = sensor_configuration["result_fields"]
        self.sub_query = sensor_configuration["sub_query"]

    async def search(self):
        args = {
            "index": self.index_pattern,
            "size": self.max_hits
        }

        if self.sub_query is not None:
            args["query"] = {"bool": {"must": [self.query, self.sub_query]}}
        else:
            args["query"] = {"bool": {"must": [self.query]}}
        if self.sort is not None:
            args["sort"] = self.sort
        if self.aggregation is not None:
            args["aggs"] = {"groups": self.aggregation if self.aggregation is not None else ""}

        return await self.client.search(**args)

    def get_table_headers(self) -> Iterable[str]:
        return self.result_fields

    async def fetch_tabular_data(self) -> Iterable[SensorReading]:
        try:
            results = await self.search()
        except elasticsearch.ElasticsearchException as elastic_exception:
            return [SensorReading([str(type(elastic_exception).__name__)])]

        if self.aggregation is not None:
            results = list(map(lambda result: result, results["aggregations"]["groups"]["buckets"]))
            if not results:
                return [EMPTY_SENSOR_READING]
            results = map(lambda result: result["group_docs"]["hits"]["hits"], results)
            results = reduce(lambda r1, r2: r1 + r2, results, [])
            results = map(lambda result: result["_source"], results)
        else:
            results = map(lambda result: result["_source"], results.get("hits", {}).get("hits", []))

        return map(lambda result: SensorReading(self.strip_message(result), result), results)

    def strip_message(self, message: Dict[str, Any]) -> Iterable[str]:
        return map(lambda result_field: str(message.get(result_field, "N/A")), self.result_fields)

