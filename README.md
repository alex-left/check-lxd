
# check-lxd
nagios plugin for check lxd containers

## Description
Check the status of the containers from lxd server, without configure containers itself.
Generate standard status codes for use it with a nagios-like monitoring server.

## Requirements
Python3 with standard libraries. Must be executed by user of lxd group.
for example, in nagios, you can add the default nrpe user to lxd group:
```
sudo usermod -a -G nagios lxd
```

## Install
Put the script in path of your convenience.

#### nrpe

For example, in your nagios server, you can create a service with nrpe for use this check:

```
define service{
        use                             generic-service,graphed-service
        host_name                       lxd-server
        service_description             mycontainer_status
        check_command                   check_nrpe!check_mycontainer
        }
```

and in your nrpe.cfg in lxd server:

```
command[check_mycontainer]=/usr/lib/nagios/plugins/custom/check_lxd state mycontainer
```

## Usage

usage: check_lxd.py [-h] option [thresholds] container_name

### options

**state** - Check the state of the container and generate CRITICAL state if not running

example:
```
check_lxd state mycontainer
```

**run** - Run a custom command into container.

example:

```
check_lxd run -c "/bin/bash /home/foo/foo.sh"

```

**procs** - Check processes of the container and generates WARNINGor CRITICAL states if the number is outside of the
required threshold ranges.

example:

```
check_lxd procs -w 12-14 -c 12-20

```


**mem** - Check the amount of memory used by the container and
generates WARNING or CRITICAL states if the number is
higher of the threshold defined in MB.

example:
```
check_lxd mem -w 1024 -c 2048
```

optional arguments:
  -h, --help            show this help message and exit

## TO DO
- connect to externals lxd servers through https
- other checks: network, disk, custom devices...
