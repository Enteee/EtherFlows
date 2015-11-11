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
            "properties": {
                "ip": {
                    "properties": {
                        "dst": {
                            "properties": {
                                "raw" : { "type" : "ip" },
                                "geoip": {
                                    "properties": {
                                        "raw": {
                                            "properties" : {
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
                        "src": {
                            "properties": {
                                "raw" : { "type" : "ip" },
                                "geoip": {
                                    "properties": {
                                        "raw": {
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
                                        "raw": {
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
                        },
                        "src": {
                            "properties": {
                                "raw" : { "type" : "string" },
                                "geoip": {
                                    "properties": {
                                        "raw": {
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
    }
}
