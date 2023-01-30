#!/bin/bash

# where to indicate to watchdog that the specified service is manually shutdown
watchdog_status=/tmp/watchdog_status

date_cmd ()
{
    echo `date -u '+%F %T,%3N'`
}

# arg1 - service action
# arg2 - service name
# arg3 - uptime to allow before assuming bad service
# arg4 (optional) - used for additional service line information (i.e. "edex_camel")
service_action ()
{
    check_for_bypass $2

    if [ $? -eq 0 ]; then
        local service_string=`build_service_line $@`

        if [ "$1" == "status" ]; then
            /usr/sbin/service $service_string 2>/dev/null | /usr/bin/grep -Eq "is running|active \(running\)"
        else
            echo "INFO `date_cmd` attempting to $1 $2"
            /usr/sbin/service $service_string 2>/dev/null
        fi

        check_for_uptime $? $2 $3

        return $?
    fi

    return 0
}

build_service_line ()
{
    if [ $# -eq 3 ]; then
        # {service} {action}
        echo "$2 $1"
    else
        # {extra service arg} {action} {service}
        echo "$4 $1 $2"
    fi
}

# arg1 - return value of service command
# arg2 - service name
# arg2 - uptime to check
check_for_uptime ()
{
    if [ $1 -ne 0 ]; then
        # Allow 1 minute after startup for services to start.
        #   Is this enough? Should we make it 3 minutes? 5 minutes?
        upt=`cat /proc/uptime | cut -d'.' -f1`
        if [ "$upt" -gt "${3:-60}" ]; then
            echo "WARN `date_cmd` $2 is not running..."
            return 1
        fi
    fi
    return 0
}

check_for_bypass ()
{
    if [ -f $watchdog_status/$1 ]; then
        echo "INFO `date_cmd` $1 is manually shutdown; skipping tests"
        return 1
    fi
    return 0
}

bypass_watchdog ()
{
    if [ ! -d "$watchdog_status" ]; then
        mkdir --parents "$watchdog_status"
        chown awips:fxalpha "$watchdog_status"
    fi
    touch "$watchdog_status/$1"
}

remove_watchdog_bypass ()
{
    rm --force "$watchdog_status/$1"
}
