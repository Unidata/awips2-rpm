#!/bin/bash
#
# Script that initializes the container and switches to the non-root user.
# Either starts a shell (while in debug mode), or starts the build immediately
# and returns the result of the build (0=success, nonzero=failed).
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Dec 17, 2021  8404      njensen      Copied from run.sh
#

set -o xtrace
[[ "$(id -u)" -eq 0 ]] || exit 1
/root/scripts/initialize.sh || exit 1
set +o xtrace
sucmd="sudo --login --preserve-env=http_proxy,https_proxy,ftp_proxy,no_proxy"
if [[ "$DEBUG_AWIPS_BUILD" == "" ]]; then
    $sucmd --user ${BUILDUSER} '/home/build/run_rehost_build.sh'
    exit $?
else
    $sucmd --user ${BUILDUSER} '/bin/bash'
fi
