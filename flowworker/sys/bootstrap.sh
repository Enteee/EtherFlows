#!/usr/bin/env bash


##
# Base set up
##
mkdir -p "${SERVICES}"
newgrp wireshark

##
# Installing RVM
##
gpg --keyserver hkp://keys.gnupg.net --recv-keys D39DC0E3
curl -sSL https://get.rvm.io | bash -s stable

##
# Installing Elasticsearch
##
wget "https://download.elasticsearch.org/elasticsearch/elasticsearch/${ELASTIC_TAR}"
tar -xvzf "${ELASTIC_TAR}" -C "${SERVICES}"

##
# Download Marvel.
##
wget "https://download.elasticsearch.org/elasticsearch/marvel/${MARVEL_FILENAME}"
${ELASTIC_HOME}/bin/plugin -i "elasticsearch/marvel/latest" -u "file:/home/vagrant/${MARVEL_FILENAME}"

##
# Installing logstash
##
wget "http://download.elastic.co/logstash/logstash/${LOGSTASH_TAR}"
tar -xvzf "${LOGSTASH_TAR}" -C "${SERVICES}"


##
# Installing kibana
##
wget "https://download.elastic.co/kibana/kibana/${KIBANA_TAR}"
tar -xvzf "${KIBANA_TAR}" -C "${SERVICES}"

