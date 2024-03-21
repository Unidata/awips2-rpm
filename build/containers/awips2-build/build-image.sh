#!/bin/bash
#
# Helper script that starts a new build container
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    May 19, 2021  8437      tgurney      Initial creation
#    Jun 10, 2021  8437      tgurney      Combine all Dockerfiles into one.
#                                         Add proxy, os, and img build args
#    Jun 30, 2021  8437      tgurney      Replace Docker CentOS 8 image with
#                                         CentOS Stream image.
#                                         Fix proxy settings
#    Jul 28, 2021  8437      tgurney      Change CentOS 8 to Rocky 8
#

scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$scriptdir"

usage="Usage: $0 [image-type]
Available image types are:
rocky8
rhel8"

if [[ "$1" == "--help" || "$1" == "" ]]; then
    echo "$usage"
    exit 0
fi

os=$1
img=""
if [[ "$os" == "rocky8" ]]; then img="docker.io/rockylinux/rockylinux:8"; fi
if [[ "$os" == "rhel8" ]]; then img="registry.access.redhat.com/ubi8/ubi:latest"; fi
if [[ "$img" == "" ]]; then
    echo "$0: \"$os\" is not a valid image type"
    echo "$usage"
    exit 1
fi

sudo --preserve-env=http_proxy,https_proxy,ftp_proxy,no_proxy \
    podman build \
    --network host \
    --tag awips2-build-"$1" \
    --build-arg os=$os \
    --build-arg img=$img \
    --build-arg HTTP_PROXY="${HTTP_PROXY}" \
    --build-arg http_proxy="${http_proxy}" \
    --build-arg HTTPS_PROXY="${HTTPS_PROXY}" \
    --build-arg https_proxy="${https_proxy}" \
    --build-arg FTP_PROXY="${FTP_PROXY}" \
    --build-arg ftp_proxy="${ftp_proxy}" \
    --build-arg NO_PROXY="${NO_PROXY}" \
    --build-arg no_proxy="${no_proxy}" \
    .
