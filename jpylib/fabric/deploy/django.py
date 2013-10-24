'''
Created on Oct 30, 2011

@author: john
'''

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

from ..utils import log_to_file

@fab.task(alias='static')
def collect_static(file_path='/usr/lib/project/'):
    
    if files.exists(file_path, use_sudo=True):        
        
        print(colors.green("Codebase exists... running collect static command on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            with fab.cd(file_path):
                result = fab.sudo('python ./manage.py collectstatic --noinput')
            
                log_to_file(result)
                
            if result.failed and confirm(colors.yellow("Collect Static call failed. Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when collectstatic call failed."))
            
    else:
        print(colors.green('Codebase not found on server {host}. Not running collectstatic command on that host.'.format(host=fab.env.host)))        
        
