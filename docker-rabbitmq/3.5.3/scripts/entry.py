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

# Define the cleanup function
def cleanup(child):
    # Warning: This function can be registered more than once, code defensively!
    if child is not None: # Make sure the child actually exists
        print "Sending SIGTERM"
        child.terminate() # Terminate the child cleanly
        try:
            for line in iter(child.stdout.readline, ''): # Clear the buffer of any lines remaining
                sys.stdout.write(line)
        except IOError:
            pass # No output found, resulted in IOError


# Variables/Consts TODO: CHANGED THESE


########################################################################################################################
# ARGUMENT PARSER                                                                                                      #
# This is where you put the Argument Parser lines                                                                      #
########################################################################################################################
# A minimum of 2 positional arguments required:
# rep_addr - The replication IP address of this node in the cluster
# member_addr - Replication IP address(es) of other member(s) of the cluster
# These are used to allow the nodes to be successfully clustered
argparser = argparse.ArgumentParser(description='Run a docker container containing a RabbitMQ Instance')

argparser.add_argument('rep_addr',
                       action='store',
                       help='The replication IP address for this node in the cluster')

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
# Check that rep_addr is a valid IP address
if not isIP(args.rep_addr):
   print "The argument %s must be a valid IP address" % args.rep_addr
   sys.exit(0) # This should be a return 0 to prevent the container from restarting.

# Check that other cluster addresses are valid
for addr in args.member_addr:
   if not isIP(addr):
      print "The argument %s must be a valid IP address" % addr
      sys.exit(0) # This should be a return 0 to prevent the container from restarting.

########################################################################################################################
# Variables                                                                                                            #
# Construct Variables from arguments passed                                                                            #
########################################################################################################################
# Create list of cluster hosts from replication address and the other member address(es)
cluster_hosts = [args.rep_addr] + args.member_addr

########################################################################################################################
# Initialize MySQL on first run                                                                                        #
########################################################################################################################
# If ibdata1 does not exist under the mysql path then this is the first time the container has been run
# so mysql_install_db needs to be run to initialize the DB using the volume mounted from a directory on the host
# We also set up the replication DB user and the root DB user password 
# Once run, this does not need to run again for the life of the container (assuming the DB data mount does not get blatted!)
if not os.path.isfile(mysql_init_check_file):
   print "No existing databases found under %s" % mysql_path
   first_run = True
   # Flush anything on the buffer
   sys.stdout.flush()
   # Reopen stdout as unbuffered. This will mean log messages will appear as soon as they become avaliable.
   sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
   if not os.path.isfile(mysql_default_cnf):
      copyfile(mysql_my_cnf,mysql_default_cnf)
   
   print "Creating initial system tables for MySQL"
   # Initialize system tables
   mysql_install = Popen(['/usr/bin/mysql_install_db'], stdout = PIPE, stderr = PIPE, shell = False)
   output, err = mysql_install.communicate() 
   # Ignore errors for install

   print output

   # Start mysql
   mysql_start = Popen(["service", "mysql", "start"], stdout = PIPE, stderr = PIPE, shell = False)
   output, err = mysql_start.communicate()
   if err:
      print err
      sys.exit(0) # This should be a return 0 to prevent the container from restarting

   print output
  
   print "Creating replication DB user and setting password for root DB user"
   # Open database connection
   host = 'localhost'
   user = 'root'
   location = '%'
   db = MySQLdb.connect(host,user)

   # Prepare a cursor object using cursor method
   cursor = db.cursor()

   try:
      # Set wsrep_on to OFF
      wsrep_on_off = "SET wsrep_on=OFF"
      results = cursor.execute(wsrep_on_off)
      print "Setting wsrep_on to OFF returned %s" % results

      # Remove user accounts with empty user names
      remove_user_accounts = "DELETE FROM mysql.user WHERE user=''"
      results = cursor.execute(remove_user_accounts)
      print "Removing MySQL user accounts with empty user names returned %s" % results

      # Grant privileges to replication user
      rep_user_privs = "GRANT ALL ON *.* TO '%s'@'%s' IDENTIFIED BY '%s'" %(rep_user, location, rep_pass)
      results = cursor.execute(rep_user_privs)
      print "Granting privlieges to MySQL replication user %s returned %s" %(rep_user, results)

      # Set root user password
      root_user_pass = "GRANT ALL ON *.* TO '%s'@'%s' IDENTIFIED BY '%s'" %(user, location, root_pass)
      results = cursor.execute(root_user_pass)
      print "Setting password for MySQL %s user returned %s" %(user, results)

   except MySQLdb.Error, e:
      print e
      sys.exit(0) # This should be a return 0 to prevent the container from restarting

   # Close cursor
   cursor.close
   # Close connection
   db.close

   # Stop MySQL
   mysql_stop = Popen(["service", "mysql", "stop"], stdout = PIPE, stderr = PIPE, shell = False)
   output, err = mysql_stop.communicate()
   if err:
      print err
      sys.exit(0) # This should be a return 0 to prevent the container from restarting

   print output


########################################################################################################################
# TEMPLATES                                                                                                            #
# This is where you manage any templates                                                                               #
########################################################################################################################
# Configuration Location goes here
template_location = '/mysql-templates'

# Create the template list
template_list = {}

# Templates go here
### wsrep.cnf ###
template_name = 'wsrep.cnf'
template_dict = { 'context' : { # Subsitutions to be performed
                                'cluster_name' : args.cluster_name,
                                'cluster_addr' : cluster_addr,
                                'rep_addr'     : args.rep_addr,
                                'rep_user'     : args.rep_user,
                                'rep_pass'     : args.rep_pass,
                              },
                  'path'    : '/etc/mysql/conf.d/wsrep.cnf',
                  'user'    : 'root',
                  'group'   : 'root',
                  'mode'    : 0644 }
template_list[template_name] = template_dict

# Load in the files from the folder
template_loader = FileSystemLoader(template_location)
template_env = TemplateEnvironment(loader=template_loader,
                                   lstrip_blocks=True,
                                   trim_blocks=True,
                                   keep_trailing_newline=True)

# Load in expected templates
for template_item in template_list:
   # Attempt to load the template
   try:
       template_list[template_item]['template'] = template_env.get_template(template_item)
   except TemplateNotFound as e:
       errormsg = "The template file %s was not found in %s (returned %s)," % template_item, template_list, e
       errormsg += " terminating..."
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

   # Attempt to open the file for writing
   try:
       template_list[template_item]['file'] = open(template_list[template_item]['path'],'w')
   except IOError as e:
       errormsg = "The file %s could not be opened for writing for template" % template_list[template_item]['path']
       errormsg += " %s (returned %s), terminating..." % template_item, e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

   # Stream
   try:
       template_list[template_item]['render'] = template_list[template_item]['template'].\
                                            render(template_list[template_item]['context'])

       # Submit to file

       template_list[template_item]['file'].write(template_list[template_item]['render'].encode('utf8'))
       template_list[template_item]['file'].close()
   except:
       e = sys.exc_info()[0]
       print "Unrecognised exception occured, was unable to create template (returned %s), terminating..." % e
       sys.exit(0) # This should be a return 0 to prevent the container from restarting.

   # Change owner and group
   try:
       template_list[template_item]['uid'] = pwd.getpwnam(template_list[template_item]['user']).pw_uid
   except KeyError as e:
       errormsg = "The user %s does not exist for template %s" % template_list[template_item]['user'], template_item
       errormsg += "(returned %s), terminating..." % e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

   try:
       template_list[template_item]['gid'] = grp.getgrnam(template_list[template_item]['group']).gr_gid
   except KeyError as e:
       errormsg = "The group %s does not exist for template %s" % template_list[template_item]['group'], template_item
       errormsg += "(returned %s), terminating..." % e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

   try:
       os.chown(template_list[template_item]['path'],
                template_list[template_item]['uid'],
                template_list[template_item]['gid'])
   except OSError as e:
       errormsg = "The file %s could not be chowned for template" % template_list[template_item]['path']
       errormsg += " %s (returned %s), terminating..." % template_item, e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

   # Change permissions
   try:
       os.chmod(template_list[template_item]['path'],
                template_list[template_item]['mode'])
   except OSError as e:
       errormsg = "The file %s could not be chmoded for template" % template_list[template_item]['path']
       errormsg += " %s (returned %s), terminating..." % template_item, e
       print errormsg
       sys.exit(0) # This should be a return 0 to prevent the container from restarting

########################################################################################################################
# SPAWN CHILD                                                                                                          #
########################################################################################################################
# Spawn the child
child_path = ['/usr/sbin/mysqld']
# REMOVED CONTENT
child = Popen(child_path, stdout = PIPE, stderr = STDOUT, shell = False) 

# Output any log items to Docker
for line in iter(child.stdout.readline, ''):
    sys.stdout.write(line)

# If the process terminates, read its errorcode and return it
sys.exit(child.returncode)
