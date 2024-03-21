#!/bin/bash

#
# Some of the rehost builds require installation of external packages that were
# not provided by RedHat. Therefore these packages are provided by AWIPS 2 and
# must be installed for the rehost builds to complete successfully. This script
# must be run from inside the build container.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Dec 09, 2021  8404     njensen     Initial creation
# Feb 01, 2022  8763     njensen     Added netcdf-fortran
# May 18, 2023  2033895  tgurney     Add qpid proton
# Jun  6, 2023  2035792  tgurney     Add --noplugins --cacheonly
#                                    to yum for speed
#


if [[ -z "${RPMS_DIR}" ]]; then
    echo "Environment variables RPMS_DIR must be set to the directory containing the release of the RPMs you wish to install"
    exit 1
fi

install_package() {
    for file in "$@" ; do
        sudo yum --noplugins --cacheonly -y --disablerepo=* install "$file" || exit 1
    done
}

install_package "${RPMS_DIR}"/noarch/awips2-ant-*.noarch.rpm

# install both netcdf and netcdf-devel
install_package "${RPMS_DIR}"/i386/awips2-netcdf-*.i386.rpm

install_package "${RPMS_DIR}"/i686/awips2-netcdf-cxx-*.i686.rpm

install_package "${RPMS_DIR}"/i686/awips2-netcdf-fortran*.i686.rpm

install_package "${RPMS_DIR}"/i686/awips2-udunits-*.i686.rpm

# needed for msas-laps
install_package "${RPMS_DIR}"/i686/awips2-expect-libs*.i686.rpm

# needed for notification which is needed for rehost-adapt
install_package "${RPMS_DIR}"/x86_64/awips2-thrift-*.x86_64.rpm

# needed for netcdf which is needed by rehost-adapt
install_package "${RPMS_DIR}"/x86_64/awips2-hdf5-*.x86_64.rpm

# needed for rehost-adapt
install_package "${RPMS_DIR}"/x86_64/awips2-notification-*.x86_64.rpm

# needed for rehost-adapt
install_package "${RPMS_DIR}"/x86_64/awips2-netcdf-*.x86_64.rpm

# for rehost-wfoa
# exclude awips2-qpid-proton-python
install_package "${RPMS_DIR}"/x86_64/awips2-qpid-proton-[0-9]*.x86_64.rpm
install_package "${RPMS_DIR}"/i386/awips2-qpid-proton-[0-9]*.i386.rpm
