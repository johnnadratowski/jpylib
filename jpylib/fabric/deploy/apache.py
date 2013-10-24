'''
Contains all deployment fabric scripts for apache
Created on Oct 29, 2011

@author: john
'''

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

from ..utils import log_to_file

@fab.task(alias='stop')
def apache_stop():
    
    if files.exists('/etc/init.d/apache2', use_sudo=True):
        
        print(colors.green("Apache File Exists... stopping Apache process on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service apache2 stop')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Stopping Apache service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when Apache stop service failed."))
            
    else:
        print(colors.green('Apache not found on server {host}. Not running Apache stop command on that host.'.format(host=fab.env.host)))
        
@fab.task(alias='start')
def apache_start():
    
    if files.exists('/etc/init.d/apache2', use_sudo=True):
        
        print(colors.green("Apache File Exists... starting Apache process on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service apache2 start')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Starting Apache service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when Apache start service failed."))
                
    else:
        print(colors.green('Apache not found on server {host}. Not running Apache start command on that host.'.format(host=fab.env.host)))
            
@fab.task(alias='status')
def apache_status():
    
    if files.exists('/etc/init.d/apache2', use_sudo=True):
        
        print(colors.green("Apache File Exists... getting apache process status on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service apache2 status')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Getting status for Apache service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when getting Apache status failed."))
                
    else:
        print(colors.green('Apache not found on server {host}. Not running Apache status command on that host.'.format(host=fab.env.host)))
            
@fab.task(alias='get_err')
def apache_error_tail(log_path='/var/log/apache2/error.log'):
    
    if files.exists('/etc/init.d/apache2', use_sudo=True):
        
        print(colors.green("Apache File Exists... getting apache error log tail (last 20 lines) on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('tail -n 20 {log_path}'.format(log_path=log_path))
        
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Getting Apache error log tail failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when getting Apache error tail failed."))
                
    else:
        print(colors.green('Apache not found on server {host}. No error logs will be retrieved on this server.'.format(host=fab.env.host)))
        
        