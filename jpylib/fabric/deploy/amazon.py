'''
Created on Oct 28, 2011

@author: john
'''
import logging

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import files


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

@fab.task(alias='hosts')
def update_hosts():
    
    if files.exists('/usr/lib/project/fabric/deploy/amazon/hosts_config.py', use_sudo=True):
        
        print(colors.green("Update Amazon host_config File Exists... updating hosts file on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            with fab.cd('/usr/lib/project/fabric/deploy/amazon/'):
                result = fab.sudo('yes | python hosts_config.py')
            
                if result.failed and confirm(colors.yellow("Updating hosts file failed. Abort Fabric script?")):
                    fab.abort(colors.red("Fabric scripted aborted because of user input when updating hosts file failed."))
            
    else:
        print(colors.green('Update hosts file script not found on server {host}. Not updating hosts file on that host.'.format(host=fab.env.host)))
        
@fab.task(alias='check')
def check_hosts():
    
    if files.exists('/usr/lib/project/fabric/deploy/amazon/hosts_config.py', use_sudo=True):
        
        print(colors.green("Update Amazon host_config File Exists... checking hosts file on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('cat /etc/hosts')
            
            if result.failed and confirm(colors.yellow("Checking hosts file failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when checking hosts file failed."))
            
    else:
        print(colors.green('Update hosts file script not found on server {host}. Not checking hosts file on that host.'.format(host=fab.env.host)))
        
