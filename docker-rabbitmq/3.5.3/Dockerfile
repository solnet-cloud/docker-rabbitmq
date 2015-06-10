# RabbitMQ Dockerfile
# Solnet Solutions
# Version: 3.5.3

# Pull base image (Ubunu 14.04)
FROM ubuntu:14.04

# Build Instructions
# When building use the following flags:
#      --tag "solnetcloud/rabbitmq:3.5.3"

# Run Instructions:
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
	apt-get clean 

# Set timezone
RUN \
    echo "Pacific/Auckland" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata
