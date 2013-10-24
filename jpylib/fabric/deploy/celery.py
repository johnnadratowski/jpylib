'''
Contains all deployment fabric scripts for celery
Created on Oct 29, 2011

@author: john
'''
import time

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django, files

from ..utils import log_to_file

def stop(name, grep_name, check_file, sleep_time, check_failed=True):
    
    if files.exists(check_file, use_sudo=True):
        
        print(colors.green("{name} exists... stopping {name} process on {host}.".format(name=name, host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.sudo('service {name} stop'.format(name=name))
            
            log_to_file(result)
            
            if check_failed:
                if result.failed and confirm(colors.yellow("Stopping {name} service failed. Abort Fabric script?".format(name=name))):
                    fab.abort(colors.red("Fabric scripted aborted because of user input when {name} stop service failed.".format(name=name)))
            
            print(colors.green("Sleeping {sec} seconds before checking if {name} was killed").format(sec=sleep_time, name=name))
            
            time.sleep(sleep_time)
                
            error = False
            try:
                result = fab.sudo('ps aux | grep {grep_name} | grep -v grep | wc -l'.format(grep_name=grep_name))
            
                log_to_file(result)
                
                if int(result) > 0:
                    
                    print(colors.red("{name} did not die. Killing {name}.".format(name=name)))
                    result = fab.sudo("ps auxww | grep celeryd | awk '{{print $2}}' | xargs kill".format(name=name))
                    
                    time.sleep(sleep_time)
                    
                    result = fab.sudo('ps aux | grep {grep_name} | grep -v grep | wc -l'.format(grep_name=grep_name))
                    
                    log_to_file(result)
                    
                    if int(result) > 0:
                        if confirm(colors.red("{name} did not die. Forcefully terminate {name}?".format(name=name))):
                            result = fab.sudo("ps auxww | grep celeryd | awk '{{print $2}}' | xargs kill -9".format(name=name))
                        
                        time.sleep(sleep_time)
                        
                        result = fab.sudo('ps aux | grep {grep_name} | grep -v grep | wc -l'.format(grep_name=grep_name))
                        
                        log_to_file(result)
                        
                        error = int(result) > 0
            except:
                import traceback
                print(colors.red("Exception occurred: %s" % traceback.format_exc()))
                error = True
            
            if error:
                if confirm(colors.yellow("Killing {name} service failed. Abort Fabric script?".format(name=name))):
                    fab.abort(colors.red("Fabric scripted aborted because of user input when {name} stop service failed.".format(name=name)))
                    
    else:
        print(colors.green('{name} not found on server {host}. Not running {name} stop command on that host.'.format(name=name, host=fab.env.host)))
        
def start(name, grep_name, check_file, sleep_time):
    
    if files.exists(check_file, use_sudo=True):
        
        print(colors.green("{name} exists... starting {name} process on {host}.".format(name=name, host=fab.env.host)))
        
        success = False
        with fab.settings(warn_only=True):
            
            for x in xrange(3): # Retry restart service 3 times max
                result = fab.sudo('service {name} start'.format(name=name))
            
                log_to_file(result)
                
                if result.failed and confirm(colors.yellow("Starting {name} service failed. Abort Fabric script?".format(name=name))):
                    fab.abort(colors.red("Fabric scripted aborted because of user input when {name} start service failed.".format(name=name)))
                
                print(colors.green("Sleeping {sec} seconds before checking if {name} is running.").format(sec=sleep_time, name=name))
                
                time.sleep(sleep_time)
                    
                result = fab.sudo('ps aux | grep {grep_name} | grep -v grep | wc -l'.format(grep_name=grep_name))
            
                log_to_file(result)
                
                if int(result) == 0:
                    if not confirm(colors.red("{name} did not run.  Try to run it again?".format(name=name))):
                        break
                else:
                    success = True
                    break # Break out of loop if process started.
                
            if not success:
                if confirm(colors.yellow("Starting {name} service failed. Abort Fabric script?".format(name=name))):
                    fab.abort(colors.red("Fabric scripted aborted because of user input when {name} start service failed.".format(name=name)))
                
    else:
        print(colors.green('{name} not found on server {host}. Not running {name} start command on that host.'.format(name=name, host=fab.env.host)))
        
def grep_process(name, grep_name, check_file):
    
    if files.exists(check_file, use_sudo=True):
        
        print(colors.green("{name} exists... grepping for {name} process on {host}.".format(name=name, host=fab.env.host)))
        
        with fab.settings(warn_only=True):
            result = fab.run('ps aux | grep {grep_name} | grep -v grep | wc -l'.format(grep_name=grep_name))
            
            log_to_file(result)
                
            print(colors.green('Total number of {name} processes running on {host}: {num}'.format(name=name, host=fab.env.host, num=result)))
    else:
        print(colors.green('{name} not found on server {host}. Not grepping for {name} processes on that host.'.format(name=name, host=fab.env.host)))
        
@fab.task(alias='stop')
def celeryd_stop():
    
    stop('celeryd', 'celeryd', '/etc/init.d/celeryd', 3)
        
@fab.task(alias='start')
def celeryd_start():
    
    start('celeryd', 'celeryd', '/etc/init.d/celeryd', 3)

@fab.task(alias='celeryd_grep_proc')
def celeryd_grep_process():
    
    grep_process('celeryd', 'celeryd', '/etc/init.d/celeryd')

        
@fab.task(alias='beat_stop')
def celerybeat_stop():
    stop('celerybeat', 'celerybeat', '/etc/init.d/celerybeat', 10, check_failed=False)
        
@fab.task(alias='beat_start')
def celerybeat_start(beat_server='up-task-1'):
    
    if fab.env.host != beat_server:
        print(colors.green('{host} is not the beat server ({beat}).  '\
                           'This command cannot run on this server. Exiting command.'.format(host=fab.env.host,
                                                                                             beat=beat_server)))
        return
    
    start('celerybeat', 'celerybeat', '/etc/init.d/celerybeat', 10)
    
@fab.task(alias='celerybeat_grep_proc')
def celerybeat_grep_process(beat_server='up-task-1'):
    
    if fab.env.host != beat_server:
        print(colors.green('{host} is not the beat server ({beat}).  '\
                           'This command cannot run on this server. Exiting command.'.format(host=fab.env.host,
                                                                                             beat=beat_server)))
        return
    
    grep_process('celerybeat', 'celerybeat', '/etc/init.d/celerybeat')
        
@fab.task(alias='ev_stop')
def celeryevcam_stop():
    
    stop('celeryevcam', 'celerycam', '/etc/init.d/celeryevcam', 10, check_failed=False)
        
@fab.task(alias='ev_start')
def celeryevcam_start(ev_server='up-task-1'):
    
    if fab.env.host != ev_server:
        print(colors.green('{host} is not the ev cam server ({ev}).  '\
                           'This command cannot run on this server. Exiting command.'.format(host=fab.env.host,
                                                                                             ev=ev_server)))
        return

    start('celeryevcam', 'celerycam', '/etc/init.d/celeryevcam', 10)
        
@fab.task(alias='celeryevcam_grep_proc')
def celeryevcam_grep_process(ev_server='up-task-1'):
    
    if fab.env.host != ev_server:
        print(colors.green('{host} is not the ev cam server ({ev}).  '\
                           'This command cannot run on this server. Exiting command.'.format(host=fab.env.host,
                                                                                             ev=ev_server)))
        return
    
    grep_process('celeryevcam', 'celerycam', '/etc/init.d/celeryevcam')
