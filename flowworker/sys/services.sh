#!/usr/bin/env bash

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
