#!/bin/bash
#
# Script that starts the build. This runs inside the container 
# 
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Apr 20, 2021  8437      tgurney      Initial creation
#    Jun  4, 2021  8437      tgurney      Add rsync of home-data. Change
#                                         workspace dir to /root/workspace
#    Jun 10, 2021  8437      tgurney      Disallow execution as root.
#                                         Propagate the return value of the
#                                         build to the caller
#    Jun 30, 2021  8437      tgurney      Copy fixed sync_workspace.sh into
#                                         AWIPS2_build if necessary
#

if [[ $(id -u) -eq 0 ]]; then
    echo "Cannot run as root"
    exit 1
fi
set -o errexit
rsync --archive --verbose "$HOME/home-data/" "$HOME"
source "$HOME/env.sh"
export A2LIBS=true
set -o pipefail
if [[ "$NO_MODIFY_GIT_REPOS" == 1 ]]; then
    if ! grep -q NO_MODIFY_GIT_REPOS "$HOME/git/AWIPS2_build/build/common/sync_workspace.sh"; then
        cp -v "$HOME/sync_workspace.sh" "$HOME/git/AWIPS2_build/build/common/"
    fi
fi
bash "$HOME/workspace/git/AWIPS2_build/build/linux/build.sh" 2>&1 \
    | tee "$HOME/workspace/awips2-build-$(date +%Y%m%d_%H%M%S).log"
