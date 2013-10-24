'''
Created on Oct 30, 2011

@author: john
'''

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

from ..utils import log_to_file

@fab.task(alias='stop')
def memcached_stop():
    
    if files.exists('/etc/init.d/memcached', use_sudo=True):
        
        print(colors.green("Memcached File Exists... stopping Memcached process on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service memcached stop')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Stopping Memcached service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when Memcached stop service failed."))
            
    else:
        print(colors.green('Memcached not found on server {host}. Not running Memcached stop command on that host.'.format(host=fab.env.host)))
        
@fab.task(alias='start')
def memcached_start():
    
    if files.exists('/etc/init.d/memcached', use_sudo=True):
        
        print(colors.green("Memcached File Exists... starting Memcached process on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service memcached start')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Starting Memcached service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when Memcached start service failed."))
                
    else:
        print(colors.green('Memcached not found on server {host}. Not running Memcached start command on that host.'.format(host=fab.env.host)))
            
@fab.task(alias='status')
def memcached_status():
    
    if files.exists('/etc/init.d/memcached', use_sudo=True):
        
        print(colors.green("Memcached File Exists... getting memcached process status on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service memcached status')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Getting status for Memcached service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when getting Memcached status failed."))
                
    else:
        print(colors.green('Memcached not found on server {host}. Not running Memcached status command on that host.'.format(host=fab.env.host)))
        
        
