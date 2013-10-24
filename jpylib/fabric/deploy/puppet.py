'''
Created on Oct 30, 2011

@author: john
'''

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

from ..utils import log_to_file

@fab.task(alias='agent')
def puppet_agent():    
    
    with fab.settings(warn_only=True):
        result = fab.sudo('type puppet')
        
        log_to_file(result)
        
        if result.failed:
            print(colors.green("Puppet command not found.  Cannot run puppet agent on server {host}".format(host=fab.env.host)))
            return
        
        print "Puppet command exists... running puppet agent for host {host}".format(host=fab.env.host)
        
        result = fab.sudo('puppet agent --test')
        
        log_to_file(result)
        
        if result.return_code == 4 and confirm(colors.yellow("Puppet update call failed. Abort Fabric script?")):
            fab.abort(colors.red("Fabric scripted aborted because of user input when svn info call failed."))
            