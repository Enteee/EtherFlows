{
    "template": "logstash-*",
	"order": 1,
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
                "ip.src.geoip" : {
					"type" : "object",
				   	"dynamic": true,
				   	"properties" : {
					 	"ip": { "type": "ip"},
					 	"location" : { "type" : "geo_point"},
					 	"latitude" : { "type" : "float"},
					 	"longitude" : { "type" : "float"}
				   	}
                },
				"ip.dst.geoip" : {
					"type" : "object",
				   	"dynamic": true,
				   	"properties" : {
					 	"ip": { "type": "ip"},
					 	"location" : { "type" : "geo_point"},
					 	"latitude" : { "type" : "float"},
					 	"longitude" : { "type" : "float"}
				   	}
                },
                "dhcpv6.iaid" : { "type" : "string", "index" : "not_analyzed" }
            }
        }
    }
}
