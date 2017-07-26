#!/usr/bin/env python3
from yaml import load
from subprocess import check_output
from sys import exit, argv
import argparse

## data
msg={
    "error_cmd": "ERROR: can't run the lxc command",
    "no_running": "CRITICAL: the container don't running",
    "ok_running": "OK, container is running",
    "miss_running": "ERROR: the container don't exist"
}

state={
    "unknown": 3,
    "critical": 2,
    "warning": 1,
    "ok": 0
}
## parse args
def set_state():
    state=True
parser = argparse.ArgumentParser(description="""nagios plugin for check LXD containers""")

subparsers = parser.add_subparsers()

parser_state = subparsers.add_parser('state',
                                     help='''Check the state of the container and generate
                                     CRITICAL state if not running''')
parser_state.set_defaults(func=set_state)
parser_procs = subparsers.add_parser('procs',
                                     help='''Check processes of the container
                                     and generates WARNING or CRITICAL states if
                                     the number is outside of the required threshold ranges.
                                     ex: check_lxd procs -w 12-14 -c 12-20''')

parser_procs.add_argument("-c", "--critical", nargs=1, required=True,
                          help='''range of processes for state CRITICAL
                          min-max''', type=str)

parser_procs.add_argument("-w", "--warning", nargs=1, required=True,
                          help='''range of processes for state WARNING
                          min-max''', type=str)

parser_mem = subparsers.add_parser('mem',
                                     help='''Check the amount of memory used by the container
                                     and generates WARNING or CRITICAL states if
                                     the number is higher of the threshold defined in MB.
                                     ex: check_lxd mem -w 1024 -c 2048''')

parser_mem.add_argument("-c", "--critical", nargs=1, required=True,
                          help='''amount of memory in MB for state CRITICAL''', type=int)

parser_mem.add_argument("-w", "--warning", nargs=1, required=True,
                          help='''amount of memory in MB for state WARNING''', type=int)

parser.add_argument("container_name",
                        help='''container name to check, mandatory''',
                        type=str, nargs=1)
args = parser.parse_args()
container_name = args.container_name[0]

## logic

def return_state(state, msg=""):
    print(msg)
    exit(state)

def get_containers_data():
    # return dict of contaners info.
    try:
        result = check_output(["lxc", "list", "--format", "yaml"])
    except Exception as error:
        return_state(state['critical'], msg['error_cmd'])
    return load(result)

def find_container(container_name):
    containers_data = get_containers_data()
    for item in containers_data:
        if item['container']['name'] == container_name:
            return item
    return_state(state['unknown'], msg['miss_running'])

def check_container_state(container_data):
        if container_data['container']['status'].lower() != "running":
            return_state(state['critical'], msg['no_running'])
        else:
            return_state(state['ok'], msg['ok_running'])

def check_container_mem(container_data):
    pass

def check_container_procs(container_data):
    pass

print(args)
if state:
    container_data = find_container(container_name)
    check_container_state(container_data)
