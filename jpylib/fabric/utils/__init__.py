'''
Contains methods that can be used throughout the fabric python modules
Created on Nov 16, 2011

@author: john
'''
import os
import datetime
import traceback

from fabric import api as fab
from fabric import colors
from fabric.contrib.console import confirm

def log_to_file(result, path="/var/log/fabric/"):
    """ Logs the given result to a file in the corresponding fabric log folder """
    
    try:
        #output_path = os.path.join(path, datetime.datetime.now().strftime("%m-%d-%y"), fab.env.host)
        output_path = os.path.join(path, fab.env.host)
        output_file = os.path.join(output_path, fab.env.command+".log")
        
        if not os.path.exists(output_path):
            fab.local("mkdir -p {path}".format(path=output_path))
        
        log = file(output_file, 'a')
        
        log.write(result)
        
        log.close()
        
    except:
        print(colors.yellow("An error occurred while trying to log result of fabric call.  "\
                            "This is a warning, fabric script will continue. Error: {exc}"\
                            .format(exc=traceback.format_exc())))