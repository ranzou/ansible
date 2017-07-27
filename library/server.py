#!/usr/bin/python

#
# Stop/Start an Application Server
#

import os
import subprocess
import platform
import datetime

def main():

    # Read arguments
    module = AnsibleModule(
        argument_spec = dict(
            state   = dict(default='started', choices=['started', 'stopped']),
            name    = dict(required=True),
            profileName = dict(required=True)
        )
    )

    state = module.params['state']
    name = module.params['name']
    profileName = module.params['profileName']
    wasdir = '/apps/websphere/appserver/8.5'

    # Check if paths are valid
    if not os.path.exists(wasdir):
        module.fail_json(msg=wasdir+" does not exist")

    # Stop server
    if state == 'stopped':
        child = subprocess.Popen([wasdir+"/bin/stopServer.sh " + name + " -profileName " + profileName], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            if not stderr_value.find("appears to be stopped") < 0:
                module.fail_json(msg=profileName + "/" + name + " stop failed", stdout=stdout_value, stderr=stderr_value)

        module.exit_json(changed=True, msg=profileName + "/" + name + " stopped successfully", stdout=stdout_value)

    # Start server
    if state == 'started':
        child = subprocess.Popen([wasdir+"/bin/startServer.sh " + name + " -profileName " + profileName], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(msg=profileName + "/" + name + " start failed", stdout=stdout_value, stderr=stderr_value)

        module.exit_json(changed=True, msg=profileName + "/" + name + " started successfully", stdout=stdout_value)


# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
