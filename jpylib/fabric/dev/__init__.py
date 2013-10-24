'''
Contains fabric scripts to be ran from a developers local environment

Created on Oct 29, 2011

@author: john
'''

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

django.settings_module('project.settings')
django.project('project')


@fab.task(alias='val', default=True)
def validate():
    return fab.local('python ./manage.py validate')
    
@fab.task
def sync():
    with fab.settings(warn_only=True):
        result = validate()
    if result.failed and not confirm('Validation failed. Still attempt sync?'):
        fab.abort('User aborted sync because validation failed')
    result = fab.local('python ./manage.py syncdb')
    
@fab.task
def svn_cleanup():
    fab.local('svn cleanup')
    
def svn_commit(files='', message=''):
    fab.local('svn ci "{files}" -m "{message}"'.format(files=files, message=message))
    
def svn_add(files=''):
    fab.local('svn add "{files}"'.format(files=files))
    
@fab.task(alias='commit')
def check_in(files='', message=''):
    validate()
    svn_cleanup()
    svn_commit(files=files, message=message)
    
@fab.task(alias='add_commit')
def add_and_check_in(files='', message=''):
    validate()
    svn_cleanup()
    svn_add(files=files)
    svn_commit(files=files, message=message)
    
