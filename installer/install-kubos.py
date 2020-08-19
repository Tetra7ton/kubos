#!/usr/bin/env python3

"""
Kubos install
Add 3 mission modes, register all applications and install them in correct mode
"""

__author__ = "Jon Grebe"
__version__ = "0.1.0"
__license__ = "MIT"

import app_api
import argparse
import sys

apps = {
    # health
    "health-mem-query": "/home/kubos/health/health-mem-query",
    "clear-database": "/home/kubos/telemetry/clear-database",
    "health-mem-check": "/home/kubos/health/health-mem-check",
    "health-ping-services": "/home/kubos/health/health-ping-services",
    "query-battery-level": "/home/kubos/eps/eps-app/query-battery-level",

    # rtc
    "set-system-time": "/home/kubos/rtc/rtc-app/set-system-time",
    
    # telemetry
    "get-eps-telemetry": "/home/kubos/eps/eps-app/get-eps-telemetry",
    "get-adcs-telemetry": "/home/kubos/adcs/adcs-app/get-adcs-telemetry",

    # eps
    "turn-port-on-1": "/home/kubos/eps/eps-app/turn-port-on-1",
    "turn-port-on-2": "/home/kubos/eps/eps-app/turn-port-on-2",
    "turn-port-on-3": "/home/kubos/eps/eps-app/turn-port-on-3",
    "turn-port-off-1": "/home/kubos/eps/eps-app/turn-port-off-1",
    "turn-port-off-2": "/home/kubos/eps/eps-app/turn-port-off-2",
    "turn-port-off-3": "/home/kubos/eps/eps-app/turn-port-off-3",

    # adcs
    "set-adcs-idle": "/home/kubos/adcs/adcs-app/set-adcs-idle",
    "set-adcs-detumble": "/home/kubos/adcs/adcs-app/set-adcs-detumble",
    "set-adcs-pointing": "/home/kubos/adcs/adcs-app/set-adcs-pointing",
    "set-adcs-reset": "/home/kubos/adcs/adcs-app/set-adcs-reset",
    "set-adcs-on": "/home/kubos/adcs/adcs-app/set-adcs-on",
    "set-adcs-off": "/home/kubos/adcs/adcs-app/set-adcs-off"
}

modes = {
    "safe" : {
        "path": "/home/kubos/installer/modes/safe-mode.json",
        "name": "safe-mode",
        "mode": "safe"
    },
    "science" : {
        "path": "/home/kubos/installer/modes/science-mode.json",
        "name": "science-mode",
        "mode": "science"
    },
    "ini" : {
        "path": "/home/kubos/installer/modes/ini-mode.json",
        "name": "ini-mode",
        "mode": "ini"
    }
}

def main():

    logger = app_api.logging_setup("install-kubos")

    # else use default global config file
    SERVICES = app_api.Services("/etc/kubos-config.toml")

    print("\n")
    ############################ REMOVE MISSION MODES ######################################
    for mode, settings in modes.items():
        
        name = mode
        # send mutation to remove mode from scheduler
        request = '''
        mutation {
            removeMode(name: "%s") {
                success
                errors
            }
        }''' % (name)
        response = SERVICES.query(service="scheduler-service", query=request)

        # get results
        response = response["removeMode"]
        success = response["success"]
        errors = response["errors"]

        if success:
            logger.info("Removed mode named: {}.".format(name))
        else:
            logger.warning("Could not remove {} mode: {}.".format(name, errors))

    print("\n")
    ############################ CREATE 3 MISSION MODES ######################################
    for mode, settings in modes.items():
        
        #try:
        name = mode
        # send mutation to create mode in scheduler
        request = '''
        mutation {
            createMode(name: "%s") {
                success
                errors
            }
        }''' % (name)
        response = SERVICES.query(service="scheduler-service", query=request)

        # get results
        response = response["createMode"]
        success = response["success"]
        errors = response["errors"]

        if success:
            logger.info("Created empty mode named: {}.".format(name))
        else:
            # check if error is due to mode already existing
            if ("exists" in errors):
                logger.info("Already a mode named: {}.".format(name))
            else:
                logger.warning("Could not create {} mode: {}.".format(name, errors))

    print("\n")
    ################## DEREGISTER ALL APPLICATIONS WITH APPLICATIONS SERVICE #######################
    for app in apps.keys():
        # send mutation to deregister app (name is required, version is optional)
        request = '''
        mutation {
            uninstall(name: "%s", version: "1.0") {
                success,
                errors
            }
        }
        ''' % (app)
        response = SERVICES.query(service="app-service", query=request)

        # get results
        response = response["uninstall"]
        success = response["success"]
        errors = response["errors"]

        if success:
            logger.info("Deregistered app: {}".format(app))
        else:
            # check if error is due to no app existing in registry
            if ("not found" in errors):
                logger.info("No app named: {} found in registry.".format(app))
            else:
                logger.warning("Unable to deregister app {}: {}".format(app, errors))

    print("\n")
    ################## REGISTER APPLICATIONS WITH APPLICATIONS SERVICE #######################
    for app, path in apps.items():

        request = ''' mutation { register(path: "%s") { success, errors, entry { active, app { name, version } } } } ''' % (path)
        response = SERVICES.query(service="app-service", query=request)

        # get results
        response = response["register"]
        success = response["success"]
        errors = response["errors"]

        if success:
            entry = response["entry"]
            active = entry["active"]
            app = entry["app"]
            name = app["name"]
            version = app["version"]

            logger.info("Registered app name: {} path: {} version: {} active: {}.".format(name, path, version, active))
        else:
            # check if error is due to app already existing in registry
            if ("exists" in errors):
                logger.info("Already a registered app named: {}.".format(app))
            else:
                logger.warning("Could not register app {} at path {}: {}".format(app, path, errors))

    print("\n")
    ################# INSTALL REGISTERED APPS INTO SPECIFIC MISSION MODES #####################
    for mode, settings in modes.items():
        
        # add safe mode tasks/mission apps to safe mode
        path = settings['path']
        name = settings['name']
        mode = settings['mode']

        request = ''' mutation { importTaskList(path: "%s", name: "%s", mode: "%s") { success errors } } ''' % (path, name, mode)
        response = SERVICES.query(service="scheduler-service", query=request)

        # get results
        response = response["importTaskList"]
        success = response["success"]
        errors = response["errors"]

        if success:
            logger.info("Added task list {} at {} to mode {}.".format(name, path, mode))
        else:
            logger.warning("Could not add task list {} at {} to mode {}: {}.".format(name, path, mode, errors))

if __name__ == "__main__":
    main()