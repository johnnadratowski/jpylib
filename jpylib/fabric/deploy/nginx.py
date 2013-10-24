'''
Contains all deployment fabric scripts for nginx
Created on Oct 29, 2011

@author: john
'''

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

from ..utils import log_to_file

@fab.task(alias='stop')
def nginx_stop():
    
    if files.exists('/etc/init.d/nginx', use_sudo=True):
        
        print(colors.green("Nginx File Exists... stopping Nginx process on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service nginx stop')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Stopping Nginx service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when Nginx stop service failed."))
            
    else:
        print(colors.green('Nginx not found on server {host}. Not running Nginx stop command on that host.'.format(host=fab.env.host)))
        
@fab.task(alias='start')
def nginx_start():
    
    if files.exists('/etc/init.d/nginx', use_sudo=True):
        
        print(colors.green("Nginx File Exists... starting Nginx process on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service nginx start')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Starting Nginx service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when Nginx start service failed."))
                
    else:
        print(colors.green('Nginx not found on server {host}. Not running Nginx start command on that host.'.format(host=fab.env.host)))
            
@fab.task(alias='status')
def nginx_status():
    
    if files.exists('/etc/init.d/nginx', use_sudo=True):
        
        print(colors.green("Nginx File Exists... getting nginx process status on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service nginx status')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Getting status for Nginx service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when getting Nginx status failed."))
                
    else:
        print(colors.green('Nginx not found on server {host}. Not running Nginx status command on that host.'.format(host=fab.env.host)))
            
@fab.task(alias='get_err')
def nginx_error_tail(log_path='/var/log/nginx/error.log'):
    
    if files.exists('/etc/init.d/nginx', use_sudo=True):
        
        print(colors.green("Nginx File Exists... getting nginx error log tail (last 20 lines) on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('tail -n 20 {log_path}'.format(log_path=log_path))
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Getting Nginx error log tail failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when getting Nginx error tail failed."))
                
    else:
        print(colors.green('Nginx not found on server {host}. No error logs will be retrieved on this server.'.format(host=fab.env.host)))
        
        