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
def uwsgi_stop():
    
    if files.exists('/etc/init/uwsgi.conf', use_sudo=True):
        
        print(colors.green("UWSGI File Exists... stopping UWSGI process on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('stop uwsgi')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Stopping UWSGI service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when UWSGI stop service failed."))
            
    else:
        print(colors.green('UWSGI not found on server {host}. Not running UWSGI stop command on that host.'.format(host=fab.env.host)))
        
@fab.task(alias='start')
def uwsgi_start():
    
    if files.exists('/etc/init/uwsgi.conf', use_sudo=True):
        
        print(colors.green("UWSGI File Exists... starting UWSGI process on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('start uwsgi')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Starting UWSGI service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when UWSGI start service failed."))
                
    else:
        print(colors.green('UWSGI not found on server {host}. Not running UWSGI start command on that host.'.format(host=fab.env.host)))
            
@fab.task(alias='status')
def uwsgi_status():
    
    if files.exists('/etc/init/uwsgi.conf', use_sudo=True):
        
        print(colors.green("UWSGI File Exists... getting UWSGI process status on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('status uwsgi')
            
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Getting status for UWSGI service failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when getting UWSGI status failed."))
                
    else:
        print(colors.green('UWSGI not found on server {host}. Not running UWSGI status command on that host.'.format(host=fab.env.host)))
            
@fab.task(alias='get_err')
def uwsgi_error_tail(log_path='/var/log/uwsgi/uwsgi.log'):
    
    if files.exists('/etc/init/uwsgi.conf', use_sudo=True):
        
        print(colors.green("UWSGI File Exists... getting UWSGI error log tail (last 20 lines) on {host}.".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('tail -n 20 {log_path}'.format(log_path=log_path))
        
            log_to_file(result)
            
            if result.failed and confirm(colors.yellow("Getting UWSGI error log tail failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when getting UWSGI error tail failed."))
                
    else:
        print(colors.green('UWSGI not found on server {host}. No error logs will be retrieved on this server.'.format(host=fab.env.host)))
        
        