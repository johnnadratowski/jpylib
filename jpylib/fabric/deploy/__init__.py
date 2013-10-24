'''
Created on Oct 29, 2011

@author: john
'''
import imp

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm
from fabric.contrib import django as fab_django
from .. import amazon

from ..utils import log_to_file
from . import (apache, nginx, celery, svn, django, puppet, memcached, uwsgi, git)

fab_django.settings_module('project.settings')
fab_django.project('project')

fab.env.user = 'ubuntu'
fab.env.key_filename = '~/.ssh/key.pem'

@fab.task(alias='command')
def run_command(command, cd="/", use_sudo=True):
    """
    Runs an arbitrary command on the servers
    
    PARAMS:
        command - The command to run on the servers
        cd - The path on which to run the command (defaults to "/")
        use_sudo - Boolean specifying if you want to use sudo when running the command (Defaults to True)
    """
    print(colors.green("Running command {command} on server {host}".format(host=fab.env.host, command=command)))
    
    with fab.cd(cd):
        if use_sudo:
            result = fab.sudo(command)
        else:
            result = fab.run(command)
    
    log_to_file(result)
    
    if result.failed and confirm(colors.yellow("Running command failed for server. Abort Fabric script?")):
        fab.abort(colors.red("Fabric scripted aborted because of user input when command failed."))
        
    print(colors.green("Command successfully ran on server {host}".format(host=fab.env.host)))
    
@fab.task(alias='ifconfig')
def get_if_config():
    """
    Runs the ifconfig commadn to print out the internet adapter configuration
    """
    
    print(colors.green("Getting IFConfig for server {host}".format(host=fab.env.host)))
    
    result = fab.sudo('ifconfig')
    
    log_to_file(result)
    
    if result.failed and confirm(colors.yellow("IFConfig failed for server. Abort Fabric script?")):
        fab.abort(colors.red("Fabric scripted aborted because of user input when ifconfig failed."))
        
    print(colors.green("IFConfig successfully retreived for server {host}".format(host=fab.env.host)))
    
@fab.task(alias='top')
def get_top_snapshot(num_snaps=3):
    """
    Gets snapshots of the top command on the servers
    
    PARAMS:
        num_snaps - The total number of snapshots to get from all servers (defaults to 3)
    """
    
    print(colors.green("Getting top snapshot(s) for server {host}".format(host=fab.env.host)))
    
    result = fab.sudo('top -b -n {num}'.format(num=num_snaps))
    
    log_to_file(result)
    
    if result.failed and confirm(colors.yellow("Top snapshot failed for server. Abort Fabric script?")):
        fab.abort(colors.red("Fabric scripted aborted because of user input when top snapshot failed."))
        
    print(colors.green("Top snapshot(s) successfully retreived for server {host}".format(host=fab.env.host)))
    
@fab.task(alias='shell')
def open_shell():
    """
    Opens a shell sequentially on all servers passed into the command.
    """
    
    print(colors.green("Opening shell on server {host}".format(host=fab.env.host)))
    
    fab.open_shell()
    
    print(colors.green("Finished shell session on server {host}".format(host=fab.env.host)))
    
@fab.task(alias='get_file')
def get_file(remote_path, local_path=None):
    """
    Retreives a file from all servers given.
    
    PARAMS:
        remote_path - the path to the remote file you want to retreive
        local_path - the path that you want to download the file to (defaults to the path you execute in)
    """
    
    print(colors.green("Getting {file} from server {host}".format(file=remote_path, host=fab.env.host)))
    
    result = fab.get(remote_path, local_path)
    
    if result.failed: 
        file_msg = "\n".join([f for f in result])
        if confirm(colors.yellow("The following files could not be retreived from server: \n\n {files}\n\n Abort Fabric script?".format(files=file_msg))):
            fab.abort(colors.red("Fabric scripted aborted because of user input when file retrieval failed."))
        
    file_msg = "\n".join([f for f in result])
    print(colors.green("The following files were successfully retreived for server {host}: \n\n{files}".format(host=fab.env.host, files=file_msg)))
    
@fab.task(alias='put_file')
def put_file(local_path, remote_path, use_sudo=False, mirror_local_mode=False, mode=None):
    """
    Puts a file on all the servers

    PARAMS:
        local_path - the path to the file on your local machine that you wnat to put on the servers
        remote_path - The path where you'd like to place the file on the server
        use_sudo - True to use sudo when placing the file on the server (Defaults to True)
    """        
    
    print(colors.green("Putting {file} on server {host} at location {remote_file}".format(file=local_path, host=fab.env.host, remote_file=remote_path)))
    
    result = fab.put(local_path, remote_path, use_sudo=use_sudo, mirror_local_mode=mirror_local_mode, mode=mode)
    
    if result.failed: 
        file_msg = "\n".join([f for f in result])
        if confirm(colors.yellow("The following files could not be put on the server: \n\n {files}\n\n Abort Fabric script?".format(files=file_msg))):
            fab.abort(colors.red("Fabric scripted aborted because of user input when put file failed."))
        
    file_msg = "\n".join([f for f in result])
    print(colors.green("The following files were successfully put on server {host}: \n\n{files}".format(host=fab.env.host, files=file_msg)))
    
@fab.task(alias='get_prod')
def get_servers(conf_file, hosts_script_path='/usr/lib/project/fabric/deploy/amazon'):
    """
    Gets all of the production servers form boto that have correct production prefixes

    :param conf_file:The configuration file to use for this fabric deployment
    :type conf_file: string of file name
    :param hosts_script_path: The path to the host_config script to run if
        you need to update your hosts config (defaults to
        /usr/lib/project/fabric/deploy/amazon)
    :type hosts_script_path: string of file name

    PARAMS:
        conf_file -
        hosts_script_path -
    """
    print(colors.green("Beginning production server update process"))
    
    try:
        conf = imp.load_source('config_module', conf_file)
    except:
        fab.abort(colors.red("Could not get config file {file}, "
                             "please check the path and try again.".format(file=conf_file)))
        
    server_names = getattr(conf, 'server_names', [])
    server_prefixes = getattr(conf, 'server_prefixes', [])
    
    script_path = getattr(conf, 'host_script_path', None)
    if script_path:
        hosts_script_path = script_path
    
    if not server_prefixes and not server_names:
        fab.abort(colors.red("Config file did not contain either server prefixes or server names." 
                             " Cannot get the proper servers to update. Exiting."))
    
    if confirm(colors.yellow("You should have an updated hosts file before you begin. Run hosts config updater?")):
        print(colors.green("Using hosts_config.py script in {path} to update hosts file.".format(path=hosts_script_path)))
        with fab.cd(hosts_script_path):
            result = fab.local('cd {path} && sudo python ./hosts_config.py -e'.format(path=hosts_script_path))
            
            if result.failed and confirm(colors.yellow("Updating hosts file failed.  Abort fabric script?")):
                fab.abort(colors.red("Fabric scripted aborted because of user input when attempting to update local hosts file."))
                
    amazon_obj = amazon.AmazonBase()
    
    hosts = []
    if server_names:
        hosts += server_names
    
    if server_prefixes:
        for reservation in amazon_obj.reservations:
            for instance in reservation.instances:
                host_name = instance.tags.get('Name', '')
                    
                for prefix in server_prefixes:
                    if host_name.startswith(prefix):
                        hosts.append(host_name)
                        break
    
    print(colors.green("The following hosts have been found and will be updated:\n{hosts}".format(hosts="\n".join(hosts))))
    
    fab.env.user = 'ubuntu'
    fab.env.hosts = hosts
    
    for attr in [attr_name for attr_name in dir(conf) if not attr_name.startswith('__')]:
        setattr(fab.env, attr, getattr(conf, attr))
    
@fab.task(alias='stop_prod')
def stop_servers():
    """
    Stops the uwsgi, apache, nginx, celery, celerybeat, and celeryev on all servers
        PARAMS:
        path - A string path to use for the codebase on the server. 
                   If you want to use multiple paths, you can send a single string
                   and separate the paths with pipes "|"
                   (defaults to /usr/lib/project/)
                   
        beat_server - the server that celerybeat is installed on (Defaults to taskserver1)
        
        ev_server - the server that celeryev is installed on (Defaults to taskserver1)
        
    """
    
    print(colors.green("Stopping production for server {host}".format(host=fab.env.host)))
    
    #memcached.memcached_stop()
    uwsgi.uwsgi_stop()    
    apache.apache_stop()
    nginx.nginx_stop()
    celery.celeryd_stop()
    celery.celerybeat_stop()
    celery.celeryevcam_stop()
    
    print(colors.green("Production stopped for server {host}".format(host=fab.env.host)))
    
@fab.task(alias='update_prod')
def update_servers(path='/usr/lib/project/'):
    """
    Runs puppet update and update on the given servers
    
    PARAMS:    
        path - A string path to use for the codebase on the server. 
                   If you want to use multiple paths, you can send a single string
                   and separate the paths with pipes "|"
                   (defaults to /usr/lib/project/)
                   
        beat_server - the server that celerybeat is installed on (Defaults to taskserver1)
        
        ev_server - the server that celeryev is installed on (Defaults to taskserver1)
    """
    
    print(colors.green("Updating production for server {host}".format(host=fab.env.host)))
    
    call_puppet = getattr(fab.env, 'call_puppet', True)
    if call_puppet:
        puppet.puppet_agent()
    else:
        print(colors.green("Call puppet configuration is false, puppet will NOT be ran on this box."))
    
    git.git_pull(file_path=path)
#    svn.svn_cleanup(file_path=path)
#    svn.svn_update(file_path=path)
    
    amazon.update_hosts()
    
    collect_server = getattr(fab.env, 'collect_static_server', 'webserver1')
    if fab.env.host.lower() == collect_server:
        django.collect_static(file_path=path)
    else:
        print(colors.green("Not running collectstatic on {host}.".format(host=fab.env.host)))
        
    print(colors.green("Production updated for server {host}".format(host=fab.env.host)))
    
@fab.task(alias='start_prod')
def start_servers(beat_server='taskserver1', ev_server='taskserver1'):
    """
    Starts the uwsgi, apache, nginx, celery, celerybeat, and celeryev on all servers
    
    PARAMS:
        path - A string path to use for the codebase on the server. 
                   If you want to use multiple paths, you can send a single string
                   and separate the paths with pipes "|"
                   (defaults to /usr/lib/project/)
                   
        beat_server - the server that celerybeat is installed on (Defaults to taskserver1)
        
        ev_server - the server that celeryev is installed on (Defaults to taskserver1)
    """
    
    print(colors.green("Starting production for server {host}".format(host=fab.env.host)))
    
    if getattr(fab.env, 'beat_server', None):
        beat_server = fab.env.beat_server
    if getattr(fab.env, 'ev_server', None):
        ev_server = fab.env.ev_server
        
    #memcached.memcached_start()
    uwsgi.uwsgi_start()    
    nginx.nginx_start()
    celery.celeryd_start()
    celery.celerybeat_start(beat_server=beat_server)
    celery.celeryevcam_start(ev_server=ev_server) 
    
    print(colors.green("Production started for server {host}".format(host=fab.env.host)))
    
@fab.task(alias='check_prod')
def check_servers(path='/usr/lib/project/', beat_server='taskserver1', ev_server='taskserver1'):
    """
    Checks the uwsgi, apache, nginx, celery, celerybeat, and celeryev on all servers by
    running a tail on theri log files and running service status checks
    
    PARAMS:
        path - A string path to use for the codebase on the server. 
                   If you want to use multiple paths, you can send a single string
                   and separate the paths with pipes "|"
                   (defaults to /usr/lib/project/)
                   
        beat_server - the server that celerybeat is installed on (Defaults to taskserver1)
        
        ev_server - the server that celeryev is installed on (Defaults to taskserver1)
    """
    
    print(colors.green("Checking production for server {host}".format(host=fab.env.host)))
    
    if getattr(fab.env, 'beat_server', None):
        beat_server = fab.env.beat_server
    if getattr(fab.env, 'ev_server', None):
        ev_server = fab.env.ev_server
        
    uwsgi.uwsgi_error_tail()
    nginx.nginx_error_tail()
    celery.celeryd_grep_process()
    celery.celerybeat_grep_process(beat_server=beat_server)
    celery.celeryevcam_grep_process(ev_server=ev_server)
    
    amazon.check_hosts()
    
    #memcached.memcached_status()
    uwsgi.uwsgi_status()
    nginx.nginx_status()
    #git.git_show(file_path=path)
    #svn.svn_info()
    
    print(colors.green("Production checked for server {host}".format(host=fab.env.host)))
    
@fab.task(alias='full_update')
def full_update_servers(path='/usr/lib/project/', beat_server='taskserver1', ev_server='taskserver1'):
    """
    Starts, updates, stops, then checks the uwsgi, apache, nginx, 
    celery, celerybeat, and celeryev on all servers
    
    PARAMS:
        path - A string path to use for the codebase on the server. 
                   If you want to use multiple paths, you can send a single string
                   and separate the paths with pipes "|"
                   (defaults to /usr/lib/project/)
                   
        beat_server - the server that celerybeat is installed on (Defaults to taskserver1)
        
        ev_server - the server that celeryev is installed on (Defaults to taskserver1)
    """
    
    print(colors.green("Starting FULL production update for server {host}".format(host=fab.env.host)))
    
    if getattr(fab.env, 'beat_server', None):
        beat_server = fab.env.beat_server
    if getattr(fab.env, 'ev_server', None):
        ev_server = fab.env.ev_server
        
    stop_servers()
    
    update_servers(path=path)
    
    start_servers(beat_server=beat_server, ev_server=ev_server)
    
    check_servers(path=path, beat_server=beat_server, ev_server=ev_server)
    
    print(colors.green("FULL Production update completed for server {host}".format(host=fab.env.host)))

if __name__ == '__main__':
    from fabric.tasks import execute
    execute(run_command, cd="/usr/lib/project/", host="webserver1", user="ubuntu", key_filename="~/.ssh/key.pem")
