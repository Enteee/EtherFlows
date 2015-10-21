[
  {
    "_id": "Dash1",
    "_type": "dashboard",
    "_source": {
      "title": "ExampleDashboard",
      "hits": 0,
      "description": "",
      "panelsJSON": "[\n  {\n    \"col\": 1,\n    \"id\": \"ethTypeDst\",\n    \"row\": 7,\n    \"size_x\": 12,\n    \"size_y\": 3,\n    \"type\": \"visualization\"\n  },\n  {\n    \"col\": 11,\n    \"id\": \"GeoIpPort\",\n    \"row\": 1,\n    \"size_x\": 2,\n    \"size_y\": 6,\n    \"type\": \"visualization\"\n  },\n  {\n    \"col\": 1,\n    \"id\": \"DnsResponses\",\n    \"row\": 1,\n    \"size_x\": 4,\n    \"size_y\": 2,\n    \"type\": \"visualization\"\n  },\n  {\n    \"col\": 5,\n    \"id\": \"HTTPcontentLenght_HTTP\",\n    \"row\": 1,\n    \"size_x\": 2,\n    \"size_y\": 2,\n    \"type\": \"visualization\"\n  },\n  {\n    \"col\": 7,\n    \"id\": \"IpTTLHisto\",\n    \"row\": 1,\n    \"size_x\": 4,\n    \"size_y\": 2,\n    \"type\": \"visualization\"\n  },\n  {\n    \"col\": 7,\n    \"id\": \"HttpHostPie\",\n    \"row\": 3,\n    \"size_x\": 4,\n    \"size_y\": 4,\n    \"type\": \"visualization\"\n  },\n  {\n    \"col\": 1,\n    \"id\": \"Top5Ip.addr\",\n    \"row\": 10,\n    \"size_x\": 12,\n    \"size_y\": 2,\n    \"type\": \"visualization\"\n  },\n  {\n    \"col\": 1,\n    \"id\": \"SSL_Ciper\",\n    \"row\": 3,\n    \"size_x\": 6,\n    \"size_y\": 2,\n    \"type\": \"visualization\"\n  },\n  {\n    \"id\": \"SSL_Cert\",\n    \"type\": \"visualization\",\n    \"size_x\": 6,\n    \"size_y\": 2,\n    \"col\": 1,\n    \"row\": 5\n  }\n]",
      "version": 1,
      "timeRestore": false,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\n  \"filter\": [\n    {\n      \"query\": {\n        \"query_string\": {\n          \"analyze_wildcard\": true,\n          \"query\": \"*\"\n        }\n      }\n    }\n  ]\n}"
      }
    }
  },
  {
    "_id": "HTTPcontentLenght_HTTP",
    "_type": "visualization",
    "_source": {
      "title": "HTTPcontentLenght_HTTP",
      "visState": "{\"type\":\"metric\",\"params\":{\"fontSize\":\"20\"},\"aggs\":[{\"id\":\"1\",\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\"http.content_length\"}}],\"listeners\":{}}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "PktCount",
    "_type": "visualization",
    "_source": {
      "title": "PktCount",
      "visState": "{\"type\":\"metric\",\"params\":{\"fontSize\":60},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}}],\"listeners\":{}}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "HttpHostVisual",
    "_type": "visualization",
    "_source": {
      "title": "HttpHostVisual",
      "visState": "{\"aggs\":[{\"id\":\"1\",\"params\":{},\"schema\":\"metric\",\"type\":\"count\"},{\"id\":\"2\",\"params\":{\"field\":\"http.host\",\"order\":\"desc\",\"orderBy\":\"1\",\"size\":5},\"schema\":\"group\",\"type\":\"terms\"},{\"id\":\"3\",\"params\":{\"customInterval\":\"2h\",\"extended_bounds\":{},\"field\":\"@timestamp\",\"interval\":\"auto\",\"min_doc_count\":1},\"schema\":\"segment\",\"type\":\"date_histogram\"}],\"listeners\":{},\"params\":{\"addLegend\":false,\"addTimeMarker\":false,\"addTooltip\":true,\"defaultYExtents\":false,\"drawLinesBetweenPoints\":true,\"interpolate\":\"linear\",\"radiusRatio\":9,\"scale\":\"linear\",\"setYExtents\":false,\"shareYAxis\":true,\"showCircles\":true,\"smoothLines\":true,\"times\":[],\"yAxis\":{}},\"type\":\"line\"}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"analyze_wildcard\":true,\"query\":\"*\"}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "TrafficDatarate",
    "_type": "visualization",
    "_source": {
      "title": "TrafficDatarate",
      "visState": "{\"type\":\"line\",\"params\":{\"addLegend\":false,\"addTimeMarker\":false,\"addTooltip\":true,\"defaultYExtents\":false,\"drawLinesBetweenPoints\":true,\"interpolate\":\"linear\",\"radiusRatio\":9,\"scale\":\"linear\",\"setYExtents\":false,\"shareYAxis\":true,\"showCircles\":true,\"smoothLines\":true,\"times\":[],\"yAxis\":{}},\"aggs\":[{\"id\":\"1\",\"type\":\"sum\",\"schema\":\"metric\",\"params\":{\"field\":\"frame.len\"}},{\"id\":\"2\",\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"@timestamp\",\"interval\":\"auto\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":{}}}],\"listeners\":{}}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"analyze_wildcard\":true,\"query\":\"*\"}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "IpTTLHisto",
    "_type": "visualization",
    "_source": {
      "title": "IpTTLHisto",
      "visState": "{\"type\":\"histogram\",\"params\":{\"shareYAxis\":true,\"addTooltip\":true,\"addLegend\":false,\"scale\":\"linear\",\"mode\":\"stacked\",\"times\":[],\"addTimeMarker\":false,\"defaultYExtents\":false,\"setYExtents\":false,\"yAxis\":{}},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"type\":\"histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"ip.ttl\",\"interval\":20,\"min_doc_count\":false,\"extended_bounds\":{}}}],\"listeners\":{}}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "GeoIpPort",
    "_type": "visualization",
    "_source": {
      "title": "GeoIpPort",
      "visState": "{\"type\":\"pie\",\"params\":{\"shareYAxis\":true,\"addTooltip\":true,\"addLegend\":false,\"isDonut\":false},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"type\":\"terms\",\"schema\":\"split\",\"params\":{\"field\":\"ip.dst.geoip.country_name\",\"size\":3,\"order\":\"desc\",\"orderBy\":\"1\",\"row\":true}},{\"id\":\"3\",\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"ip.dst\",\"size\":5,\"order\":\"desc\",\"orderBy\":\"1\"}},{\"id\":\"4\",\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"tcp.dstport\",\"size\":5,\"order\":\"desc\",\"orderBy\":\"1\"}}],\"listeners\":{}}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "HttpHostPie",
    "_type": "visualization",
    "_source": {
      "title": "HttpHostPie",
      "visState": "{\"type\":\"pie\",\"params\":{\"shareYAxis\":true,\"addTooltip\":true,\"addLegend\":true,\"isDonut\":false},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"http.host\",\"size\":5,\"order\":\"desc\",\"orderBy\":\"1\"}},{\"id\":\"3\",\"type\":\"terms\",\"schema\":\"segment\",\"params\":{\"field\":\"ip.src\",\"size\":5,\"order\":\"desc\",\"orderBy\":\"1\"}}],\"listeners\":{}}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "ethTypeDst",
    "_type": "visualization",
    "_source": {
      "title": "ethTypeDst",
      "visState": "{\"type\":\"area\",\"params\":{\"shareYAxis\":true,\"addTooltip\":true,\"addLegend\":true,\"smoothLines\":true,\"scale\":\"linear\",\"interpolate\":\"linear\",\"mode\":\"stacked\",\"times\":[],\"addTimeMarker\":false,\"defaultYExtents\":false,\"setYExtents\":false,\"yAxis\":{}},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"type\":\"terms\",\"schema\":\"split\",\"params\":{\"field\":\"eth.type.show\",\"size\":2,\"order\":\"desc\",\"orderBy\":\"1\",\"row\":true}},{\"id\":\"3\",\"type\":\"terms\",\"schema\":\"group\",\"params\":{\"field\":\"eth.dst\",\"size\":5,\"order\":\"desc\",\"orderBy\":\"1\"}},{\"id\":\"4\",\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"@timestamp\",\"interval\":\"auto\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":{}}}],\"listeners\":{}}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "DnsResponses",
    "_type": "visualization",
    "_source": {
      "title": "DnsResponses",
      "visState": "{\"type\":\"table\",\"params\":{\"perPage\":10,\"showMeticsAtAllLevels\":false,\"showPartialRows\":false},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"3\",\"type\":\"terms\",\"schema\":\"bucket\",\"params\":{\"field\":\"dns.resp.name\",\"size\":3,\"order\":\"desc\",\"orderBy\":\"1\"}}],\"listeners\":{}}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"index\":\"logstash-*\",\"query\":{\"query_string\":{\"analyze_wildcard\":true,\"query\":\"*\"}},\"filter\":[]}"
      }
    }
  },
  {
    "_id": "SSL_Ciper",
    "_type": "visualization",
    "_source": {
      "title": "SSLCiper",
      "visState": "{\n  \"type\": \"table\",\n  \"params\": {\n    \"perPage\": 10,\n    \"showPartialRows\": false,\n    \"showMeticsAtAllLevels\": false\n  },\n  \"aggs\": [\n    {\n      \"id\": \"1\",\n      \"type\": \"count\",\n      \"schema\": \"metric\",\n      \"params\": {}\n    },\n    {\n      \"id\": \"2\",\n      \"type\": \"terms\",\n      \"schema\": \"bucket\",\n      \"params\": {\n        \"field\": \"ssl.handshake.ciphersuite.show\",\n        \"size\": 5,\n        \"order\": \"desc\",\n        \"orderBy\": \"1\"\n      }\n    }\n  ],\n  \"listeners\": {}\n}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\n  \"index\": \"logstash-*\",\n  \"query\": {\n    \"query_string\": {\n      \"query\": \"*\",\n      \"analyze_wildcard\": true\n    }\n  },\n  \"filter\": []\n}"
      }
    }
  },
  {
    "_id": "SSL_Ciphersuite",
    "_type": "visualization",
    "_source": {
      "title": "SSLCiphersuite",
      "visState": "{\n  \"type\": \"histogram\",\n  \"params\": {\n    \"shareYAxis\": true,\n    \"addTooltip\": true,\n    \"addLegend\": true,\n    \"scale\": \"linear\",\n    \"mode\": \"stacked\",\n    \"times\": [],\n    \"addTimeMarker\": false,\n    \"defaultYExtents\": false,\n    \"setYExtents\": false,\n    \"yAxis\": {}\n  },\n  \"aggs\": [\n    {\n      \"id\": \"1\",\n      \"type\": \"count\",\n      \"schema\": \"metric\",\n      \"params\": {}\n    },\n    {\n      \"id\": \"2\",\n      \"type\": \"terms\",\n      \"schema\": \"segment\",\n      \"params\": {\n        \"field\": \"ssl.handshake.ciphersuite.show\",\n        \"size\": 5,\n        \"order\": \"desc\",\n        \"orderBy\": \"1\"\n      }\n    }\n  ],\n  \"listeners\": {}\n}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\n  \"index\": \"logstash-*\",\n  \"query\": {\n    \"query_string\": {\n      \"query\": \"*\",\n      \"analyze_wildcard\": true\n    }\n  },\n  \"filter\": []\n}"
      }
    }
  },
  {
    "_id": "SSL_Cert",
    "_type": "visualization",
    "_source": {
      "title": "SSLCert",
      "visState": "{\n  \"type\": \"table\",\n  \"params\": {\n    \"perPage\": 10,\n    \"showPartialRows\": false,\n    \"showMeticsAtAllLevels\": false\n  },\n  \"aggs\": [\n    {\n      \"id\": \"1\",\n      \"type\": \"count\",\n      \"schema\": \"metric\",\n      \"params\": {}\n    },\n    {\n      \"id\": \"2\",\n      \"type\": \"terms\",\n      \"schema\": \"bucket\",\n      \"params\": {\n        \"field\": \"ssl.handshake.certificate.show\",\n        \"size\": 5,\n        \"order\": \"desc\",\n        \"orderBy\": \"1\"\n      }\n    }\n  ],\n  \"listeners\": {}\n}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\n  \"index\": \"logstash-*\",\n  \"query\": {\n    \"query_string\": {\n      \"query\": \"*\",\n      \"analyze_wildcard\": true\n    }\n  },\n  \"filter\": []\n}"
      }
    }
  },
  {
    "_id": "Top5Ip.addr",
    "_type": "visualization",
    "_source": {
      "title": "IpAddrHisto",
      "visState": "{\n  \"aggs\": [\n    {\n      \"id\": \"1\",\n      \"params\": {},\n      \"schema\": \"metric\",\n      \"type\": \"count\"\n    },\n    {\n      \"id\": \"2\",\n      \"params\": {\n        \"field\": \"ip.addr\",\n        \"order\": \"desc\",\n        \"orderBy\": \"1\",\n        \"size\": 5\n      },\n      \"schema\": \"group\",\n      \"type\": \"terms\"\n    },\n    {\n      \"id\": \"3\",\n      \"params\": {\n        \"customInterval\": \"2h\",\n        \"extended_bounds\": {},\n        \"field\": \"@timestamp\",\n        \"interval\": \"auto\",\n        \"min_doc_count\": 1\n      },\n      \"schema\": \"segment\",\n      \"type\": \"date_histogram\"\n    }\n  ],\n  \"listeners\": {},\n  \"params\": {\n    \"addLegend\": true,\n    \"addTimeMarker\": false,\n    \"addTooltip\": true,\n    \"defaultYExtents\": false,\n    \"mode\": \"stacked\",\n    \"scale\": \"linear\",\n    \"setYExtents\": false,\n    \"shareYAxis\": true,\n    \"times\": [],\n    \"yAxis\": {}\n  },\n  \"type\": \"histogram\"\n}",
      "description": "",
      "version": 1,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\n  \"index\": \"logstash-*\",\n  \"query\": {\n    \"query_string\": {\n      \"analyze_wildcard\": true,\n      \"query\": \"*\"\n    }\n  },\n  \"filter\": []\n}"
      }
    }
  }
]