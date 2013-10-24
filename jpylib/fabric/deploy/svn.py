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

@fab.task(alias='info')
def svn_info(file_path='/usr/lib/project/'):
    """
    Runs an SVN INFO call on the given path(s)
    
    PARAMS:
        file_path - Either a string path or a list of string paths to run svn info
    """
    
    if "|" in file_path:
        for path in file_path.split('|'):
            svn_info_path(path)
    else:
        svn_info_path(file_path)
    
def svn_info_path(file_path):
    
    if files.exists(file_path, use_sudo=True):        
        
        print(colors.green("SVN codebase exists... getting svn "
                           "info on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            with fab.cd(file_path):
                result = fab.sudo('svn info')
                
                log_to_file(result)
            
            if result.failed and confirm(colors.yellow("SVN Info call failed. "
                                                       "Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of "
                                     "user input when svn info call failed."))
            
    else:
        print(colors.green('Codebase not found on '
                           'server {host}. Not running svn info '
                           'command on that host.'.format(host=fab.env.host)))        
        
@fab.task(alias='cleanup')
def svn_cleanup(file_path='/usr/lib/project/'):
    """
    Runs an SVN CLEANUP call on the given path(s)
    
    PARAMS:
        file_path - Either a string path or a list of string paths to run svn cleanup
    """
    
    if "|" in file_path:
        for path in file_path.split('|'):
            svn_cleanup_path(path)
    else:
        svn_cleanup_path(file_path)

def svn_cleanup_path(file_path):
    
    if files.exists(file_path, use_sudo=True):        
        
        print(colors.green("SVN codebase exists... running svn cleanup on "
                           "{host} at {path}".format(host=fab.env.host, path=file_path)))
        
        with fab.settings(warn_only=True):
            with fab.cd(file_path):
                result = fab.sudo('svn cleanup')
                
                log_to_file(result)
            
            if result.failed and confirm(colors.yellow("SVN cleanup call failed. "
                                                       "Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user "
                                     "input when svn cleanup call failed."))
            
    else:
        print(colors.green('Codebase not found '
                           'on server {host}. Not running svn cleanup '
                           'command on that host.'.format(host=fab.env.host)))        
        
@fab.task(alias='update')
def svn_update(file_path='/usr/lib/project/'):
    """
    Runs an SVN UPDATE call on the given path(s)
    
    PARAMS:
        file_path - Either a string path or a list of string paths to run svn update
    """
    
    if "|" in file_path:
        for path in file_path.split('|'):
            svn_update_path(path)
    else:
        svn_update_path(file_path)

def svn_update_path(file_path):
    
    if files.exists(file_path, use_sudo=True):        
        
        print(colors.green("SVN codebase exists... running svn update "
                           "on {host} at {path}".format(host=fab.env.host, path=file_path)))
        
        with fab.settings(warn_only=True):
            with fab.cd(file_path):
                result = fab.sudo('svn update')
                
                log_to_file(result)
            
            if result.failed and confirm(colors.yellow("SVN update call failed. "
                                                       "Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user "
                                     "input when svn update call failed."))
            
    else:
        print(colors.green('Codebase not found '
                           'on server {host}. Not running svn update '
                           'command on that host.'.format(host=fab.env.host)))        
        
@fab.task(alias='checkout')
def svn_checkout(file_path='/usr/lib/project/'):
    
    if files.exists(file_path, use_sudo=True):        
        
        print(colors.green("SVN codebase exists... running svn "
                           "checkout on {host}".format(host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            with fab.cd(file_path):
                result = fab.sudo('svn checkout')
                
                log_to_file(result)
            
            if result.failed and confirm(colors.yellow("SVN checkout call failed. "
                                                       "Abort Fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input "
                                     "when svn checkout call failed."))
            
    else:
        print(colors.green('Codebase not found on server '
                           '{host}. Not running svn checkout command '
                           'on that host.'.format(host=fab.env.host)))        
        
