#!/bin/bash
#
# Script to set up build directories for AWIPS II RHEL 8 build container
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Apr 20, 2021  8437      tgurney      Initial creation
#    May 19, 2021  8437      tgurney      Narrow the scope of the script to
#                                         only set up build directories
#    Jun  4, 2021  8437      tgurney      Allow specifying a working directory
#    Jun 10, 2021  8437      tgurney      Remove workspace directory
#

if [[ "$#" > 1 || "$1" == '--help' ]]; then
    echo "usage: $0 [builddirs]"
    echo "Sets up build directories for the AWIPS II build container"
    echo "builddirs defaults to \$HOME/builddirs"
    exit 1
fi

builddirs="$1"
if [[ "$builddirs" == "" ]]; then
    builddirs="$HOME/builddirs"
fi

# AWIPS2_build is the minimum necessary repo to do any kind of build.
AWIPS2_build="$builddirs/git/AWIPS2_build"

if [[ ! -d "${AWIPS2_build}" ]]; then
    echo "ERROR: ${AWIPS2_build} does not exist"
    echo "Put all git repos in $builddirs/git (you can use a symlink)"
    exit 1
fi

mkdir --parents --verbose "$builddirs/home-data" || exit 1
if [[ ! -f "$builddirs/home-data/env.sh" ]]; then
    cp --verbose "$(dirname "$0")/env-devdefault.sh" "$builddirs/home-data/env.sh" || exit 1
fi
