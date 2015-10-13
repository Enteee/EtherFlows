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

##
# Start services
##
screen -d -m -S worksession
export SCREEN_SESSION=$(screen -ls | sed -nre 's/\s*([0-9]+\.worksession).*/\1/p')

screen -S ${SCREEN_SESSION} -X screen -t "elasticsearch" 
screen -S ${SCREEN_SESSION} -p "elasticsearch" -X stuff $"${ELASTIC_HOME}/bin/elasticsearch\n"

screen -S ${SCREEN_SESSION} -X screen -t "logstash"
screen -S ${SCREEN_SESSION} -p "logstash" -X stuff $"${LOGSTASH_HOME}/bin/logstash -f /vagrant/logstash.conf\n"

screen -S ${SCREEN_SESSION} -X screen -t "kibana"
screen -S ${SCREEN_SESSION} -p "kibana" -X stuff $"${KIBANA_HOME}/bin/kibana\n"
