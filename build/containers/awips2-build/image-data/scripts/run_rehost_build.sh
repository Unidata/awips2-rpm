#!/bin/bash
#
# Script that starts the build. This runs inside the container 
# 
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Dec 17, 2021  8404      njensen      Copied from run_build.sh
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
bash "$HOME/workspace/git/AWIPS2_build/build/rehost/build_all_rehost.sh" 2>&1 \
    | tee "$HOME/workspace/rehost-build-$(date +%Y%m%d_%H%M%S).log"
