#!/usr/bin/env python3

"""
Create mode in scheduler.
"""

__author__ = "Jon Grebe"
__version__ = "0.1.0"
__license__ = "MIT"

import app_api
import argparse
import sys

def main():

    logger = app_api.logging_setup("create-mode")

    # parse arguments for config file and run type
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', '-r', nargs=1)
    parser.add_argument('--config', '-c', nargs=1)
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
            on_command(logger, SERVICES)
    else:
        on_command(logger, SERVICES)

# logic run for application on OBC boot
def on_boot(logger, SERVICES):
    pass

# logic run when commanded by OBC
def on_command(logger, SERVICES):
    name = str(input("Enter mode name: "))

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
        logger.warning("Could not create {} mode: {}.".format(name, errors))


if __name__ == "__main__":
    main()
