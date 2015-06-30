# RabbitMQ Dockerfile
# Solnet Solutions
# Version: 3.5.3

# Pull base image (Ubunu 14.04)
FROM ubuntu:14.04

# Build Instructions
# When building use the following flags:
#      --tag "solnetcloud/rabbitmq:3.5.3"

# Run Instructions:
# When running use the following flags:
#       --restart=on-failure  --log-driver=syslog
# The following command line arguments are supported.
# usage: entry rep_addr member_addr [member_addr ...]
#
# positional arguments:
#   rep_addr              The IP address for this node in cluster
#   member_addr           IP address(es) for other member(s) of the cluster


# Information
MAINTAINER Antonia Caskey <antonia.caskey@solnet.co.nz>
LABEL Description="This image is used to stand up a RabbitMQ instance with clustering." Version="3.5.3"

# Patch notes:
# Version 3.5.3
#       - Current working version of RabbitMQ

# Install any required packages
# Updating our system's default application toolset
RUN \
	apt-get -q update && \
	apt-get -q -y upgrade
# Enable RabbitMQ application repository
RUN echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list

# install curl
RUN sudo apt-get -q -y install curl
# Add the verification key for the package
RUN curl http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | sudo apt-key add -

# Update the sources
RUN apt-get update

# Install Erlang packages
RUN sudo apt-get -q -y install erlang erlang-doc

# download and install rabbitmq-server and extra packages
RUN \
	 sudo apt-get -q -y install rabbitmq-server python-software-properties python python-jinja2 python-ipy && \
	apt-get -q clean && \
	sudo /usr/sbin/rabbitmq-plugins enable rabbitmq_mqtt rabbitmq_stomp rabbitmq_management  rabbitmq_management_agent rabbitmq_management_visualiser rabbitmq_federation rabbitmq_federation_management sockjs

# Prepare directrories
RUN \
    mkdir -p /rmq-data/ && \
    mkdir -p /rmq-templates

ADD templates/rabbitmq.config /rmq-templates/rabbitmq.config

# Change the rabbitmq-server file
COPY config/rabbitmq-server /etc/default/rabbitmq-server

# Entry script
COPY scripts/entry.py /usr/local/bin/entry
RUN chmod +x /usr/local/bin/entry

# Set timezone
RUN \
    echo "Pacific/Auckland" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# Expose ports to other containers
EXPOSE 5672
EXPOSE 4369
EXPOSE 25672
EXPOSE 15672

EXPOSE 9100
EXPOSE 9101
EXPOSE 9102
EXPOSE 9103
EXPOSE 9104
EXPOSE 9105

# Define the default command as entrypoint
ENTRYPOINT ["/usr/local/bin/entry"]
