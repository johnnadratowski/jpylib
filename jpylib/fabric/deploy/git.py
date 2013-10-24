'''
Contains the deployment scripts for SVN
Created on Oct 29, 2011

@author: john
'''

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

from ..utils import log_to_file

@fab.task(alias='show')
def git_show(file_path='/usr/lib/project/'):
    """
    Runs an GIT SHOW call on the given path(s)
    
    PARAMS:
        file_path - Either a string path or a list of string paths to run svn info
    """
    
    if "|" in file_path:
        for path in file_path.split('|'):
            git_show_path(path)
    else:
        git_show_path(file_path)
    
def git_show_path(file_path):
    
    if files.exists(file_path, use_sudo=True):        
        
        print(colors.green("GIT codebase exists... getting git show "
                           "info on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            with fab.cd(file_path):
                result = fab.sudo('git show')
                
                log_to_file(result)
            
            if result.failed and confirm(colors.yellow("GIT Show call failed. "
                                                       "Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of "
                                     "user input when git show call failed."))
            
    else:
        print(colors.green('Codebase not found on '
                           'server {host}. Not running git show '
                           'command on that host.'.format(host=fab.env.host)))        
        
@fab.task(alias='pull')
def git_pull(file_path='/usr/lib/project/'):
    """
    Runs an GIT PULL call on the given path(s)
    
    PARAMS:
        file_path - Either a string path or a list of string paths to run git pull
    """
    
    if "|" in file_path:
        for path in file_path.split('|'):
            git_pull_path(path)
    else:
        git_pull_path(file_path)

def git_pull_path(file_path):
    
    if files.exists(file_path, use_sudo=True):        
        
        print(colors.green("GIT codebase exists... running git pull "
                           "on {host} at {path}".format(host=fab.env.host, path=file_path)))
        
        with fab.settings(warn_only=True):
            with fab.cd(file_path):
                result = fab.run('git pull')
                
                log_to_file(result)
            
            if result.failed and confirm(colors.yellow("GIT Pull call failed. "
                                                       "Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user "
                                     "input when git pull call failed."))
            
    else:
        print(colors.green('Codebase not found '
                           'on server {host}. Not running git pull '
                           'command on that host.'.format(host=fab.env.host)))        
        
