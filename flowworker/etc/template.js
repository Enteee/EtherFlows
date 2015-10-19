{
    "template": "logstash-*",
    "settings" : {
        "number_of_shards" : 10,
        "number_of_replicas" : 1
    },
    "mappings": {
        "_default_": {
            "_all": { "enabled": true },
            "dynamic_templates" : [ {
                "string_fields" : {
                    "match" : "*",
                    "match_mapping_type" : "string",
                    "mapping" : {
                        "type" : "string", "index" : "not_analyzed", "omit_norms" : true
                    }
                }
            } ],
            "_source": { "compress": true },
             "properties" : {
                "ip.src.geoip.location" : { "type" : "geo_point", "index" : "not_analyzed" },
                "ip.dst.geoip.location" : { "type" : "geo_point", "index" : "not_analyzed" }
                "dhcpv6.iaid" : { "type" : "string", "index" : "not_analyzed" }
            }
        }
    }
}
