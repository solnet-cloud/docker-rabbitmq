#!/usr/bin/env python
# This script parses command line arguments and uses these to create nodes for the RabbitMQ service

########################################################################################################################
# LIBRARY IMPORT												       #
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

# set template file location
template_location = "/rmq-templates"
### rabbitmq.config ###

template = {}
template_name = "rabbitmq.config"
template_dict= {'content':{
		'ip_addresses':addrs
			},
		'path':'',
		'user':'root',
		'group':'root',
		'mode':'0644'}
template[template_name] = template_dict

# Load in the files from the folder
template_loader = FileSystemLoader(template_location)
template_env = TemplateEnvironment(loader=template_loader,
                                   lstrip_blocks=True,
                                   trim_blocks=True,
                                   keep_trailing_newline=True)

 # Attempt to load the template
try:
	template[template_name]['template'] = template_env.get_template(template_name)
except TemplateNotFound as e:
	errormsg = "The template file %s was not found (returned %s)," % template_name, e
	errormsg += " terminating..."
	print errormsg
	sys.exit(0) # This should be a return 0 to prevent the container from restarting
# Attempt to open the file for writing
try:
	template[template_name]['file'] = open(template[template_name]['path'],'w')
except IOError as e:
	errormsg = "The file %s could not be opened for writing for template" % template[template_name]['path']
       	errormsg += " %s (returned %s), terminating..." % template_name, e
       	print errormsg
       	sys.exit(0) # This should be a return 0 to prevent the container from restarting

# Stream
try:
      	template[template_name]['render'] = template[template_name]['template'].render(template[template_name]['context'])
	template[template_name]['file'].write(template[template_name]['render'].encode('utf8'))	
       	template[template_name]['file'].close()
except:
	e = sys.exc_info()[0]
	print "Unrecognised exception occured, was unable to create template (returned %s), terminating..." % e
	sys.exit(0) # This should be a return 0 to prevent the container from restarting.

   # Change owner and group
try:
       template[template_name]['uid'] = pwd.getpwnam(template[template_name]['user']).pw_uid
except KeyError as e:
       errormsg = "The user %s does not exist for template %s" % template[template_name]['user'], template
       errormsg += "(returned %s), terminating..." % e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

try:
       template[template_name]['gid'] = grp.getgrnam(template[template_name]['group']).gr_gid
except KeyError as e:
       errormsg = "The group %s does not exist for template %s" % template[template_name]['group'], template_name
       errormsg += "(returned %s), terminating..." % e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

try:
       os.chown(template[template_name]['path'],
                template[template_name]['uid'],
                template[template_name]['gid'])
except OSError as e:
       errormsg = "The file %s could not be chowned for template" % template[template_name]['path']
       errormsg += " %s (returned %s), terminating..." % template_name, e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

   # Change permissions
try:
       os.chmod(template[template_name]['path'],
                template[template_name]['mode'])
except OSError as e:
       errormsg = "The file %s could not be chmoded for template" % template[template_name]['path']
       errormsg += " %s (returned %s), terminating..." % template_name, e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting


########################################################################################################################
# SPAWN CHILD                                                                                                          #
########################################################################################################################
# Flush anything on the buffer
sys.stdout.flush()

# Spawn the child
child_path = ["/usr/lib/rabbitmq/bin/rabbitmq-server", "start"]
child = Popen(child_path, stdout = PIPE, stderr = STDOUT, shell = False) 

# Reopen stdout as unbuffered. This will mean log messages will appear as soon as they become avaliable.
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# Output any log items to Docker
for line in iter(child.stdout.readline, ''):
    sys.stdout.write(line)

# If the process terminates, read its errorcode and return it
sys.exit(child.returncode)
