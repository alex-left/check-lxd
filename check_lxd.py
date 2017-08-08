#!/usr/bin/env python3

from subprocess import check_output, CalledProcessError
from yaml import load
import argparse

# data
state = {
    "unknown": 3,
    "critical": 2,
    "warning": 1,
    "ok": 0
}

# Logic
def parser_args():
    parser = argparse.ArgumentParser(
        description="""nagios plugin for check LXD containers""")

    subparsers = parser.add_subparsers(dest='command')
    parser_state = subparsers.add_parser('state',
                                        help='''Check the state of the container and generate
                                        CRITICAL state if not running''')

    parser_run = subparsers.add_parser('run',
                                       help='''run a command into container''')

    parser_run.add_argument("cmd", nargs=1, type=str,
                            help='''Run a custom command into container, remember close it in quotes.
                            example: check_lxd run -c "/bin/bash /home/foo/foo.sh"''')

    parser_procs = subparsers.add_parser('procs',
                                        help='''Check processes of the container
                                        and generates WARNING or CRITICAL states if
                                        the number is outside of the required threshold ranges.
                                        ex: check_lxd procs -w 12-14 -c 12-20''')


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

    return parser.parse_args()

def return_state(state, msg=""):
    print(msg)
    exit(state)

def get_containers_data():
    # return dict of contaners info.
    try:
        result = check_output(["lxc", "list", "--format", "yaml"])
    except Exception as error:
        return_state(state['critical'], "ERROR: can't run the lxc command")
    return load(result)


def find_container(container_name):
    containers_data = get_containers_data()
    for item in containers_data:
        if item['container']['name'] == container_name:
            return item
    return_state(state['unknown'], "ERROR: the container %s don't exist" % container_name)


def check_container_state(container_data):
        if container_data['container']['status'].lower() != "running":
            return_state(
                state['critical'], "CRITICAL: the container %s don't running" % container_data)
        else:
            return_state(
                state['ok'], "OK: the container %s is running" % container_data)

def check_container_mem(container_data, critical, warning):
    used_mem = int(container_data['state']['memory']['usage'] / 1048576)
    if used_mem > critical[0]:
        return_state(
            ['critical'], "CRITICAL, the container consumes %dM of RAM, over %dM" % (used_mem, critical[0]))
    if used_mem > warning[0]:
        return_state(
            state['warning'], "WARNING, the container consumes %dM of RAM, over %dM" % (used_mem, warning[0]))
    return_state(
        state['ok'], "OK, the container consumes %dM of RAM, under thresholds" % used_mem)

def check_container_procs(container_data, critical, warning):
    try:
        critical = critical[0].split("-")
        warning = warning[0].split("-")
        assert ( len(critical) == 2 and len(warning) == 2 )
        for item in range(2):
            critical[item] = int(critical[item])
            warning[item] = int(warning[item])
    except Exception as error:
        print("ERROR: wrong arguments", error)
        exit(state['unknown'])
    used_procs = container_data['state']['processes']
    if used_procs < critical[0] or used_procs > critical[1]:
        return_state(
            state['critical'], "CRITICAL, the container has %d procs, is out of range: %d - %ds" % (used_procs, critical[0], critical[1]))
    if used_procs < warning[0] or used_procs > warning[1]:
        return_state(
            state['warning'], "WARNING, the container has %d procs, is out of range: %d - %d" % (used_procs, warning[0], warning[1]))
    else:
        return_state(
            state['ok'], "OK, the container has %d procs, under thresholds" % used_procs)


def run_in_container(container_name, cmd):
    try:
        res = check_output("lxc exec " + container_name + " -- " + cmd, shell=True)
        return_state(state["ok"], str(res.decode()))
    except CalledProcessError as ret:
        if ret.returncode == 1:
            return_state(state["warning"], str(ret.output.decode()))
        elif ret.returncode == 2:
            return_state(state["critical"], str(ret.output.decode()))
        else:
            return_state(state["unknown"], "Code status: %d, msg: %s" % (ret.returncode, str(ret.output.decode())))

# Main
args = parser_args()
container_name = args.container_name[0]
container_data = find_container(container_name)

if args.command == 'state':
    check_container_state(container_data)
if args.command == 'mem':
    check_container_mem(container_data, args.critical, args.warning)
if args.command == 'procs':
    check_container_procs(container_data, args.critical, args.warning)
if args.command == 'run':
        run_in_container(container_name, args.cmd[0])
