#!/usr/bin/env python3

"""
Mission application that turns off a output port on EPS module.
"""

__author__ = "Jon Grebe"
__version__ = "0.1.0"
__license__ = "MIT"

import app_api
import argparse
import sys

def main():

    logger = app_api.logging_setup("turn-port-off")

    # parse arguments for config file and run type
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', '-r', nargs=1)
    parser.add_argument('--config', '-c', nargs=1)
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    if args.config is not None:
        # use user config file if specified in command line
        SERVICES = app_api.Services(args.config[0])
    else:
        # else use default global config file
        SERVICES = app_api.Services("/etc/kubos-config.toml")

    # run app onboot or oncommand logic
    if args.run is not None:
        if args.run[0] == 'OnBoot':
            on_boot(logger, SERVICES)
        elif args.run[0] == 'OnCommand':
            on_command(logger, SERVICES, args.port)
    else:
        on_command(logger, SERVICES, args.port)

# logic run for application on OBC boot
def on_boot(logger, SERVICES):
    pass

# logic run when commanded by OBC
def on_command(logger, SERVICES, port):
    
    # send mutation to turn off EPS port
    request = '''
    mutation {
        controlPort(controlPortInput: {
                    power: OFF
                    port: PORT%d })
        {
        errors
        success
        }
    }
    ''' % (port)
    response = SERVICES.query(service="eps-service", query=request)

    # get results
    result = response["controlPort"]
    success = result["success"]
    errors = result["errors"]

    # check results
    if success:
        logger.info("Turned off port {}.".format(port))
    else:
        logger.warn("Uable to turn off port {}: {}.".format(port, errors))

if __name__ == "__main__":
    main()
