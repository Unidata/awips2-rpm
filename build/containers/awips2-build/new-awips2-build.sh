#!/bin/bash
#
# Helper script that starts a new build container
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Apr 20, 2021  8437      tgurney      Initial creation
#    May 19, 2021  8437      tgurney      Remove support for "detached mode".
#                                         Add support for multiple images
#    Jun  4, 2021  8437      tgurney      Allow specifying a working directory
#    Jun 10, 2021  8437      tgurney      Add proxy and uid/gid env variables
#    Jun 30, 2021  8437      tgurney      Fix proxy settings
#    Jul 14, 2021  8437      tgurney      Remove unused env variables
#    Nov 29, 2021  8563      dgilling     Add variable for ldm user id.
#    Dec 21, 2021  8404      njensen      Reworked options and added rehost option
#

usage() {
    echo "Usage: $0 [-r] [-b builddirs] <image-type>"
    echo
    echo "Start a new AWIPS II build container."
    echo "Optional -r argument indicates rehost build"
    echo "Optional -b for builddirs argument defaults to \$HOME/builddirs"
    echo "Available values for image-type are:"
    sudo podman images | grep -Eo 'localhost/awips2-build-\w+' | cut -d'/' -f2 | cut -d'-' -f3
    exit 0
}

scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$scriptdir"

while getopts "rb:" option; do
    case "${option}" in
        r)
            # rehost flag is on
            runscript="/root/scripts/run_rehost.sh"
            ;;
        b)
            # use the supplied builddirs
            builddirs=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

# remove options to get positional arguments indexed correctly
shift $((OPTIND-1))

if [[ "$1" == '--help' || "$1" == "" ]]; then
    usage
fi

imagetype=$1
if [[ "$builddirs" == "" ]]; then
    builddirs="$HOME/builddirs"
fi

if [[ "$runscript" == "" ]]; then
    runscript="/root/scripts/run.sh"
fi

export BUILDUSER="$(whoami)"
export AWIPS_UID="$(id -u awips)"
export AWIPS_GID="$(id -g awips)"
export BUILDUSER_UID="$(id -u)"
export BUILDUSER_GID="$(id -g)"
export LDMUSER_UID="$(id -u ldm)"
export LDMUSER_GID="$(id -g ldm)"
export FXALPHA_GID="$(getent group fxalpha | cut -d':' -f3)"

set -o xtrace

sudo --preserve-env=https_proxy,http_proxy,ftp_proxy,no_proxy \
    podman run -it \
    -e DEBUG_AWIPS_BUILD=1 \
    -e BUILDUSER="$BUILDUSER" \
    -e AWIPS_UID="$AWIPS_UID" \
    -e AWIPS_GID="$AWIPS_GID" \
    -e BUILDUSER_UID="$BUILDUSER_UID" \
    -e BUILDUSER_GID="$BUILDUSER_GID" \
    -e LDMUSER_UID="$LDMUSER_UID" \
    -e LDMUSER_GID="$LDMUSER_GID" \
    -e FXALPHA_GID="$FXALPHA_GID" \
    -e http_proxy="$http_proxy" \
    -e https_proxy="$https_proxy" \
    -e ftp_proxy="$ftp_proxy" \
    -e no_proxy="$no_proxy" \
    --hostname=build-container \
    --net=host \
    -v "$builddirs"/git/:/home/build/git \
    -v "$builddirs"/home-data/:/home/build/home-data \
    -v /dev/log:/dev/log \
    -v /install:/install \
    "localhost/awips2-build-$imagetype" \
    ${runscript}
