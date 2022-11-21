# monitor-tui



## Run

Install requirements
```
pip install -r requirements.txt
```

run the application
```
python main.py
```

run the application in docker
```
docker run --rm -t -i -e "TERM=xterm-256color" -v <PATH_TO_CONNF>:app/config.yml freberg/monitor-tui:latest
```

## Configuration
Each service is defined in a list under services
```
services:
  - name: "backend"
    hierarchy: "production/"
```
In turn, each service defines a list of sensors, data can currently be pulled from prometheus and elastic

### Prometheus configuration
When a service is selected, below configuration will display the current total and free memory as reported by 
node_exporter's prometheus endpoint
```
services:
  - name: "backend"
    hierarchy: "production/"
    sensors:
      - type: "prometheus"
        url: <PROMETHEUS_URL>
        name: "node_exporter_memory"
        metrics:
          - name: "total"
            query: 'node_memory_MemTotal_bytes{{instance="backend"}}'
          - name: "free"
            query: 'node_memory_MemFree_bytes{{instance="backend"}}'
```
To make sensor configuration reusable "additional_label" can be used along with yaml anchors
```
node_exporter_memory: &node_exporter_memory
  type: "prometheus"
  url: <PROMETHEUS_URL>
  name: "node_exporter_memory"
  metrics:
    - name: "total"
      query: 'node_memory_MemTotal_bytes{{instance="{additional_label}"}}'
    - name: "free"
      query: 'node_memory_MemFree_bytes{{instance="{additional_label}"}}'
      
services:
  - name: "backend"
    hierarchy: "production/"
    sensors:
      - <<: *node_exporter_memory
        additional_label: "backend"
  - name: "frontend"
    hierarchy: "production/"
    sensors:
      - <<: *node_exporter_memory
        additional_label: "frontend"
```


### Elastic configuration
When a service is selected in the tui, below configuration will display the latest 50 matching documents indexed by 
elastic in a table containing two columns, "@timestamp" and "message"
```
services:
  - name: "backend"
    hierarchy: "production/"
    sensors:
      - type: "elastic"
        url: <ELASTIC_URL>
        name: "elastic_tail"
        max_hits: 50
        index_pattern: "<INDEX_PATTERN>"
        sort: {"@timestamp": "desc"}
        query: { "bool": { "filter": [
               { "match": { "tags": "production" } },
               { "match": { "tags": "backend" } }
               ] } }
    result_fields: [ "@timestamp", "message" ]
```
To make sensor configuration reusable "sub_query" can be used along with yaml anchors
```
elastic_tail: &elastic_tail
  type: "elastic"
  url: <ELASTIC_URL>
  name: "elastic_tail"
  max_hits: 50
  index_pattern: "<INDEX_PATTERN>"
  sort: {"@timestamp": "desc"}
  query: { "bool": { "filter": [
         { "match": { "tags": "production" } }
         ] } }
  result_fields: [ "@timestamp", "message" ]
         
services:
  - name: "backend"
    hierarchy: "production/"
    sensors:
      - <<: *elastic_tail
        sub_query: { "bool": { "filter": [ { "match": { "tags": "backend" } } ] } }
  - name: "frontend"
    hierarchy: "production/"
    sensors:
      - <<: *elastic_tail
        sub_query: { "bool": { "filter": [ { "match": { "tags": "frontend" } } ] } }
```