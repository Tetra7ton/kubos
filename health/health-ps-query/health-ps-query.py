#!/usr/bin/env python3

"""
Mission application that pings the payload subsystem to check for successful connection.
"""

__author__ = "Jon Grebe"
__version__ = "0.1.0"
__license__ = "MIT"

import app_api
import argparse
import sys

def main():

    logger = app_api.logging_setup("payload-ping")

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
        SERVICES = app_api.Services()

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
    logger.info("Starting nominal operation for payload subsystem...")

    '''
    {
        ps(pids: [Int!] = null): [
            {
                pid: Int!       - process ID
                uid: Int        - user ID who created the process
                gid: Int        - group ID who created the process
                usr: String     - username associated with UID
                grp: String     - group name associated with the GID
                state: String   - single character indicating process state (refer to ps state code manual)
                ppid: Int       - process ID of process which started the process
                mem: Int        - virtual memory of process (bytes)
                rss: Int        - current number of pages process has in real memory
                threads: Int    - number of threads in process
                cmd: String     - full command used to execute the process (defaults to filename)
            }
        ]
    }
    '''

    # pinging payload subsystem

    request = ''' 
    {
        ps(pids: [30972]) {
            pid,
            state,
            ppid,
            threads,
            cmd
        }
    }
    '''
    response = SERVICES.query(service="monitor-service", query=request)

    # get results
    print(response)
    result = response["ps"][0]
    pid = result["pid"]
    state = result["state"]
    ppid = result["ppid"]
    threads = result["threads"]
    cmd = result["cmd"]

    logger.info("Got the following information about PID:{} | State:{} | CMD:{} | Threads:{}".format(pid,state,cmd,threads))

if __name__ == "__main__":
    main()
