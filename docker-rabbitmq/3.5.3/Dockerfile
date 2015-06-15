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
# TODO
#
#

# NOTICE:
#TODO
#
#
# Information
MAINTAINER Antonia Caskey <antonia.caskey@solnet.co.nz>
LABEL Description="This image is used to stand up a RabbitMQ instance with clustering." Version="3.5.3"

# Patch notes:
# Version 3.5.3
#       - Current working version of RabbitMQ

# Install any required packages
# Updating our system's default application toolset
RUN \
	apt-get update && \
	apt-get -y upgrade
# Enable RabbitMQ application repository
RUN echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list

# Add the verification key for the package
RUN curl http://www.rabbitmq.com/rabbitmq-signing-key-public.asc | sudo apt-key add -

# Update the sources
RUN apt-get update

# download and install rabbitmq-server and extra packages
RUN \
	 sudo apt-get install rabbitmq-server python-software-properties python python-jinja2 python-ipy && \
	apt-get clean && \
	sudo /usr/sbin/rabbitmq-plugins enable rabbitmq_mqtt rabbitmq_stomp rabbitmq_management  rabbitmq_management_agent rabbitmq_management_visualiser rabbitmq_federation rabbitmq_federation_management sockjs

# Change the rabbitmq-server file
RUN sudo cat config/rabbitmq-server > /etc/default/rabbitmq-server

# Set timezone
RUN \
    echo "Pacific/Auckland" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# Expose ports to other containers
# Expose port 5672: RabbitMQ
# Expose port 4369: clustering
# Expose port 25672: clustering
EXPOSE 5672
EXPOSE 4369
EXPOSE 25672
