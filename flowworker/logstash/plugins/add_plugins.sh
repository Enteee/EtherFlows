#!/usr/bin/env bash

PLUGINS_DIR="/etc/logstash/plugins"
LOGSTASH_GEM="/opt/logstash/Gemfile"
PLUGINS=$(ls -1A  ${PLUGINS_DIR} |  grep -v "add_plugins.sh" )

for i in ${PLUGINS}; do
    echo "gem '${i}', :path => '${PLUGINS_DIR}/${i}'"
done

