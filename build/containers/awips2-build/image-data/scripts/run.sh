#!/bin/bash
#
# Script that initializes the container and switches to the non-root user.
# Either starts a shell (while in debug mode), or starts the build immediately
# and returns the result of the build (0=success, nonzero=failed).
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Apr 20, 2021  8437      tgurney      Initial creation
#    Jul 14, 2021  8437      tgurney      Use sudo to switch to non-root user.
#                                         Preserve proxy variables. Don't start
#                                         build automatically if running in
#                                         debug mode.
#    Jan 24, 2022  8746      lsingh       Removed conflicting --login arg from 
#                                         sudo command.
#

set -o xtrace
[[ "$(id -u)" -eq 0 ]] || exit 1
/root/scripts/initialize.sh || exit 1
set +o xtrace
sucmd="sudo --user ${BUILDUSER} --preserve-env=http_proxy,https_proxy,ftp_proxy,no_proxy"
if [[ "$DEBUG_AWIPS_BUILD" == "" ]]; then
    $sucmd /home/build/run_build.sh
    exit $?
else
    $sucmd /bin/bash
fi
