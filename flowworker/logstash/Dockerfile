FROM logstash:latest

# Copy plugin folder
COPY plugins/ /etc/logstash/plugins/

# Install local plugins
RUN /etc/logstash/plugins/add_plugins.sh
RUN /opt/logstash/bin/plugin install --no-verify
