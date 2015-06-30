#!/usr/bin/env python
# This script parses command line arguments and uses these to create nodes for the RabbitMQ service

########################################################################################################################
# LIBRARY IMPORT  TODO: Seemingly I don't need to remove any parts of this code, but it could be better form to not    #
########################################################################################################################
# Import required libaries
import sys,os,pwd,grp   # OS Libraries
import argparse         # Parse Arguments
from subprocess import Popen, PIPE, STDOUT
                        # Open up a process

# Important required templating libarires
from jinja2 import Environment as TemplateEnvironment, \
                   FileSystemLoader, Template
                        # Import the jinja2 libaries required by this script
from jinja2.exceptions import TemplateNotFound
                        # Import any exceptions that are caught by the Templates section

# Specific to to this script
from IPy import IP
from shutil import copyfile

# Functions

# Checks if an ip address is valid or not
def isIP(address):
   try:
      IP(address)
      ip = True
   except ValueError:
      ip = False
   return ip

########################################################################################################################
# ARGUMENT PARSER                                                                                                      #
# This is where you put the Argument Parser lines                                                                      #
########################################################################################################################
# A minimum of 1 positional arguments required:
# member_addr - IP address(es) of all member(s) of the cluster
# These are used to allow the nodes to be successfully clustered
argparser = argparse.ArgumentParser(description='Run a docker container containing a RabbitMQ Instance')

argparser.add_argument('member_addr',
                       action='store',
                       nargs='+',
                       help='Replication IP address(es) for other member(s) of the cluster')

try:
   args = argparser.parse_args()
except SystemExit:
   sys.exit(0) # This should be a return 0 to prevent the container from restarting.

    
########################################################################################################################
# ARGUMENT VERIRIFCATION                                                                                               #
# This is where you put any logic to verify the arguments, and failure messages                                        #
########################################################################################################################
# 
# Check that other cluster addresses are valid
for addr in args.member_addr:
   if not isIP(addr):
      print "The argument %s must be a valid IP address" % addr
      sys.exit(0) # This should be a return 0 to prevent the container from restarting.

########################################################################################################################
# Variables                                                                                                            #
# Construct Variables from arguments passed                                                                            #
########################################################################################################################
addrs = args.member_addr

########################################################################################################################
# TEMPLATES                                                                                                            #
# This is where you manage any templates                                                                               #
########################################################################################################################

template_location = "/rmq-templates"

template_name = "rabbitmq.config"

template_dict= {'content':{
		'ip_addresses':addrs
			},
		'path':'',
		'user':'root',
		'group':'root',
		'mode':'0644'}

########################################################################################################################
# SPAWN CHILD                                                                                                          #
########################################################################################################################

