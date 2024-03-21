#!/bin/bash
#
# Script that performs initialization steps when the container is first run.
# Currently this creates users and groups and sets permissions on directories
# inside the container. This stuff is done here instead of in the Dockerfile
# because the UIDs and GIDs are specified when the container is created.
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Jun 10, 2021  8437      tgurney      Initial creation
#    Nov 29, 2021  8536      dgilling     Add ldm user.
#    Jan 04, 2021  8404      njensen      Only add groups and users if they don't
#                                         exist
#

if [[ -f /root/initialize.done ]]; then
    exit 0
fi

if [[ "$(id -u)" -ne 0 ]]; then
    exit 1
fi

set -o errexit

getent group fxalpha &> /dev/null || groupadd fxalpha --gid $FXALPHA_GID
if [[ "$BUILDUSER_GID" != "$FXALPHA_GID" ]]; then
    getent group ${BUILDUSER} &> /dev/null || groupadd ${BUILDUSER} --gid $BUILDUSER_GID
fi
if [[ "$AWIPS_GID" != "$FXALPHA_GID" ]]; then
    getent group awips &> /dev/null || groupadd awips --gid $AWIPS_GID
fi
id -u awips &> /dev/null || useradd --comment 'AWIPS Local Account' --create-home \
        --home-dir /home/awips --uid $AWIPS_UID \
        --gid $AWIPS_GID --no-user-group --groups fxalpha awips
id -u ${BUILDUSER} &> /dev/null || useradd --comment 'Build User' --create-home \
        --home-dir /home/build --uid $BUILDUSER_UID \
        --gid $BUILDUSER_GID --no-user-group --groups fxalpha ${BUILDUSER}
id -u ldm &> /dev/null || useradd --comment 'LDM Service Account' --create-home \
        --home-dir /home/ldm --uid $LDMUSER_UID \
        --gid $LDMUSER_GID --no-user-group --groups fxalpha ldm
chown -R ${BUILDUSER}:fxalpha /build /awips2 /home/build

echo "${BUILDUSER} ALL=(ALL)   NOPASSWD: ALL" > /etc/sudoers.d/${BUILDUSER}

touch /root/initialize.done
