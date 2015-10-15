{
    "template": "logstash-*",
    "settings" : {
        "number_of_shards" : 1,
        "number_of_replicas" : 0
    },
    "mappings": {
        "_default_": {
            "_all": { "enabled": true },
            "_source": { "compress": true },
             "properties" : {
                "ip.src.geoip.location" : { "type" : "geo_point", "index" : "not_analyzed" }, 
                "ip.dst.geoip.location" : { "type" : "geo_point", "index" : "not_analyzed" }
            }
        }
    }
}
