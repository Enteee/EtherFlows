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
            "properties": {
                "ip": {
                    "properties": {
                        "dst": {
                            "properties": {
                                "raw" : { "type" : "ip" },
                                "geoip": {
                                    "properties": {
                                        "ip": { "type": "ip"},
                                        "location" : { "type" : "geo_point"},
                                        "latitude" : { "type" : "float"},
                                        "longitude" : { "type" : "float"}
                                    }
                                }
                            }
                        },
                        "src": {
                            "properties": {
                                "raw" : { "type" : "ip" },
                                "geoip": {
                                    "properties": {
                                        "ip": { "type": "ip"},
                                        "location" : { "type" : "geo_point"},
                                        "latitude" : { "type" : "float"},
                                        "longitude" : { "type" : "float"}
                                    }
                                }
                            }
                        }
                    }
                },
                "ipv6": {
                    "properties": {
                        "dst": {
                            "properties": {
                                "raw" : { "type" : "string" },
                                "geoip": {
                                    "properties": {
                                        "ip": { "type": "string"},
                                        "location" : { "type" : "geo_point"},
                                        "latitude" : { "type" : "float"},
                                        "longitude" : { "type" : "float"}
                                    }
                                }
                            }
                        },
                        "src": {
                            "properties": {
                                "raw" : { "type" : "string" },
                                "geoip": {
                                    "properties": {
                                        "ip": { "type": "string"},
                                        "location" : { "type" : "geo_point"},
                                        "latitude" : { "type" : "float"},
                                        "longitude" : { "type" : "float"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
