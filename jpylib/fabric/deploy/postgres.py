'''
Contains all deployment fabric scripts for postgres
Created on Oct 29, 2011

@author: john
'''

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

from ..utils import log_to_file
@fab.task(alias='stop')
def postgres_stop():
    
    if files.exists('/etc/init.d/postgresql', use_sudo=True):
        
        print(colors.green("Postgres File Exists... stopping Postgres process on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service postgresql stop', user='postgres')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Stopping Postgres service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when Postgres stop service failed."))
            
    else:
        print(colors.green('Postgres not found on server {host}. Not running Postgres stop command on that host.'.format(host=fab.env.host)))
        
@fab.task(alias='start')
def postgres_start():
    
    if files.exists('/etc/init.d/postgresql', use_sudo=True):
        
        print(colors.green("Postgres File Exists... starting Postgres Postgres on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service postgresql start', user='postgres')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Starting Postgres service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when Postgres start service failed."))
                
    else:
        print(colors.green('Postgres not found on server {host}. Not running Postgres start command on that host.'.format(host=fab.env.host)))
            
@fab.task(alias='status')
def postgres_status():
    
    if files.exists('/etc/init.d/postgresql', use_sudo=True):
        
        print(colors.green("Postgres File Exists... getting Postgres process status on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service postgresql status', user='postgres')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Getting status for Postgres service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when getting Postgres status failed."))
                
    else:
        print(colors.green('Postgres not found on server {host}. Not running Postgres status command on that host.'.format(host=fab.env.host)))
            