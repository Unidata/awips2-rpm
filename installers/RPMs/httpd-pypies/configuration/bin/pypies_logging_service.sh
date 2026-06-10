#!/bin/bash
# Script used by httpd-pypies.service to start and stop
#   the pypies logging service.
. /etc/rc.d/init.d/functions

PYPIES_LOGGING_CMD="${PYTHON_INSTALL}/bin/python -u ${PYTHON_INSTALL}/lib/python3.11/site-packages/pypies/logging/logProcess.py"

startLogging() {
    source /awips2/etc/environment
    echo -n $"Starting logging service:"
    nohup su awips -c "$PYPIES_LOGGING_CMD > /tmp/pypiesLoggingService.log 2>&1" > /dev/null &
    RC=$?
    # TODO: need better checks to ensure that the logging service actually keeps
    #       running after startup.
    RC=$?
    if [ ${RC} -ne 0 ]; then
        failure
    else
        success
    fi
    return $?
}

stopLogging() {
    echo -n $"Stopping logging service:"
    # Stop the logging process
    for pid in `ps aux | grep [l]ogProcess.py | awk '{print $2}'`;
        do
            kill -9 ${pid}
            RC=$?
            if [ ${RC} -ne 0 ]; then
                failure
                return $?
            fi
        done
    success
    return $?
}

RETVAL=0

case $1 in
    start)
        startLogging
        RETVAL=$?
        ;;
    stop)
        stopLogging
        RETVAL=$?
        ;;
    *)
        echo "Usage: $0 {start|stop}..." 1>&2
        exit 1
        ;;
esac

exit $RETVAL
