'''
Fabric configuration file for production servers

Created on Aug 21, 2012

@author: john
'''

server_prefixes = ['webserver', 'taskserver', ]
beat_server = 'beatserver'
ev_server = 'evserver'
collect_static_server = 'webserver1'
call_puppet = True
host_script_path = '~/git/project/fabric/deploy/amazon'

user = 'ubuntu'
key_filename = ['~/.ssh/key.pem', ]
