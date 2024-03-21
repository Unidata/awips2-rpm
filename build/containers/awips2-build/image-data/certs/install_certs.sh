#!/bin/bash
#
#    Date          Ticket#   Engineer     Description
#    ------------  --------  -----------  -------------------------------------
#    Aug 03, 2022  8794      sharbison    Initial copy of build container
#                                         scripts from dev_rhel8, to be
#                                         converted to rhel7.
#

cd /root/certs
for ext in pem der cer; do
    if ls *.${ext} >/dev/null; then
        cp -v *.$ext /etc/pki/ca-trust/source/anchors
    fi
done
update-ca-trust extract
