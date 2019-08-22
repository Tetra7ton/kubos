#!/usr/bin/env python3

"""
Main file for adcs application
"""

__author__ = "Jon Grebe"
__version__ = "0.1.0"
__license__ = "MIT"

import app_api
import argparse
import sys

def on_boot(logger):

    print("OnBoot logic")

'''
code to setup/initialize adcs subsystem
'''

def on_command(logger):

    print("OnCommand logic")

    request = '''
    mutation {
        update(updateInput: {time: 1.0
                        gpsLock: [1.0,2.0]})
        {
        errors
        success
        }
    }
    '''
    response = SERVICES.query(service="adcs-service", query=request)
    print(response)

'''
code for sending/receiving commands/telemetry from adcs subsystem
'''

def main():

    logger = app_api.logging_setup("adcs-app")

    parser = argparse.ArgumentParser()

    parser.add_argument('--run', '-r', nargs=1)
    parser.add_argument('--config', '-c', nargs=1)
    parser.add_argument('cmd_args', nargs='*')

    args = parser.parse_args()

    if args.config is not None:
        global SERVICES
        SERVICES = app_api.Services(args.config[0])
    else:
        SERVICES = app_api.Services()

    if args.run is not None:
        if args.run[0] == 'OnBoot':
            on_boot(logger)
        elif args.run[0] == 'OnCommand':
            on_command(logger)
    else:
        on_command(logger)

if __name__ == "__main__":
    main()
