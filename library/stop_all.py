#!/usr/bin/python

#
# Stop all application servers
#

import os
from subprocess import Popen, PIPE
import platform
import datetime
import re

def main():

    # Read arguments
    module = AnsibleModule(
        argument_spec = dict(
            state   = dict(default='stopped', choices=['stopped', 'status']),
            profileName = dict(required=True)
        )
    )

    state = module.params['state']
    profileName = module.params['profileName']
    wasdir = '/apps/websphere/appserver/8.5'

    # Check if paths are valid
    if not os.path.exists(wasdir):
        module.fail_json(msg=wasdir+" does not exist")

    # First, grab a string of all the application servers on the host
#    child = Popen([wasdir+"/bin/serverStatus.sh -all -profileName " + profileName], shell=True, stdout=PIPE, stderr=PIPE)
    child = Popen(["/apps/ebus/build/etc/linux/scripts/psall.sh"], stdout=PIPE, stderr=PIPE)
    stdout_value, stderr_value = child.communicate()
    if state == 'status':
        module.exit_json(changed=False, msg=stdout_value, stdout=stdout_value)

    # Turn the above string of servers into a list
    if state == 'stopped':
        serverList = []
        # Iterate over instances like wasserver:BSN85Cell01Node01:ECS01
        for m in re.finditer('wasserver:\w+:\w+', stdout_value):
            # m.group(0) is the actual text rather than the match object
            server = m.group(0)
            # Isolate the ECS01 part of the string in, for example, wasserver:BSN85Cell01Node01:ECS01 
            server = server.split(':')[2]
            serverList.append(server)

        # Stop all the servers in serverList concurrently, storing their child processes in the 'processes' list for later access
        processes = []
        for server in serverList:
            #child = Popen([wasdir+"/bin/stopServer.sh " + server + " -profileName " + profileName], shell=True, stdout=PIPE, stderr=PIPE)
            child = Popen([wasdir+"/bin/stopServer.sh", server, "-profileName", profileName], stdout=PIPE, stderr=PIPE)
            # Add server name as well as child process, so I can access it in the loop below
            processes.append([server,child])

        # Retrieve the results of all the child processes and add output to list 'messages', which will be returned to the user
        messages = []
        for process in processes:
            server = process[0]
            child = process[1]
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                if not stderr_value.find("appears to be stopped") < 0:
                    messages.append("%s %s stop failed" % (profileName, server))
#            else:
#                messages.append("%s %s stopped successfully" % (profileName, server))

        if not messages:
            output = "All servers stopped successfully"
        else:
            output = "\n".join(messages)
        module.exit_json(changed=True, stdout=output)


# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
