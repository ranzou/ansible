#!/usr/bin/python

# Install WebSphere Application Server V9

import os
import subprocess
import platform
import datetime
import shutil

def main():

    # WAS offerings
    offerings = [
        'com.ibm.websphere.ND.V9',
        'com.ibm.websphere.IHS.v9',
        'com.ibm.websphere.PLG.v9',
        'com.ibm.websphere.WCT.v9'
    ]

    # Read arguments
    module = AnsibleModule(
        argument_spec = dict(
            state       = dict(default='present', choices=['present', 'absent']),
            instmanager = dict(required=True),
            destination = dict(required=True),
            repository  = dict(required=True),
            offering    = dict(default='com.ibm.websphere.ND.v9', choices=offerings),
            logdir      = dict(required=True)
        )
    )

    state = module.params['state']
    instmanager = module.params['instmanager']
    destination = module.params['destination']
    repository = module.params['repository']
    offering = module.params['offering']
    logdir = module.params['logdir']

    # Check if paths are valid
    if not os.path.exists(instmanager+"/eclipse"):
        module.fail_json(msg=instmanager+"/eclipse not found")

    # Installation
    if state == 'present':
        if not os.path.exists(logdir):
            if not os.listdir(logdir):
                os.makedirs(logdir)
        logfile = platform.node() + "_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "_was_install.log"
        child = subprocess.Popen([instmanager+"/eclipse/tools/imcl install " + offering + " -repositories " + repository + " -installationDirectory " + destination + " -acceptLicense -showProgress -log " + logdir + "/" + logfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(msg="WAS ND install failed", stdout=stdout_value, stderr=stderr_value)

        module.exit_json(changed=True, msg="WAS ND installed successfully", stdout=stdout_value)

    # Uninstall
    if state == 'absent':
        if not os.path.exists(logdir):
            if not os.listdir(logdir):
                os.makedirs(logdir)
        logfile = platform.node() + "_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "_was_uninstall.log"
        child = subprocess.Popen([instmanager+"/eclipse/instmanager --launcher.ini " + instmanager + "/eclipse/silent-install.ini -input " + destination + "/uninstall/uninstall.xml -log " + logdir+"/"+logfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(msg="WAS ND uninstall failed", stdout=stdout_value, stderr=stderr_value)

        # Remove AppServer dir forcefully so that it doesn't prevents us from
        # reinstalling.
        shutil.rmtree(destination, ignore_errors=False, onerror=None)

        module.exit_json(changed=True, msg="WAS ND uninstalled successfully", stdout=stdout_value)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
