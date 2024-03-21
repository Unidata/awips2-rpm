#!/bin/bash -x

#
# This script moves the build artifacts to a staging area and
# creates a RPM Repo using the baselined comps.xml file.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -------------------------------------------
# Mar 10, 2016  4734     dlovely     Initial import from awipscm
# Feb 25, 2021  8377     dlovely     Added support to find and copy RPMs
#                                    from AWIPS2_build to the staging dir.
# Nov 03, 2021  8697     randerso    Copy comps.xml to the repository so the
#                                    purge script can rebuild the repository
#                                    after purging old versions
# May 17, 2022  8799     dgilling    Delete unnecessary 32-bit version of 
#                                    awips2-python-thrift RPM before sync.
## 

TARGET_DIR=$1
sudo mkdir -p $TARGET_DIR

source ${WORKSPACE}/git/AWIPS2_build/build/common/version_release.sh

## FIXME: Find a way to prevent the build from generating a 32-bit version of 
## awips2-python-thrift, so we don't have to delete it here to prevent it from being
## synced to the new repo
sudo rm --force --verbose ${WORKSPACE}/rpmbuild/RPMS/i386/awips2-python-thrift*.rpm

#sync updated rpms
sudo rsync -avz --progress --delete ${WORKSPACE}/rpmbuild/RPMS/ $TARGET_DIR/v$AWIPSII_RELEASE/
if [ $? -ne 0 ]; then
   exit 1
fi

#Find and sync RPMs in AWIPS2_build
sudo mkdir -p $TARGET_DIR/v$AWIPSII_RELEASE/x86_64/ $TARGET_DIR/v$AWIPSII_RELEASE/noarch/
sudo find ${WORKSPACE}/git/AWIPS2_build/ -path */RPMs/*.x86_64.rpm -exec cp {} $TARGET_DIR/v$AWIPSII_RELEASE/x86_64/ \;
sudo find ${WORKSPACE}/git/AWIPS2_build/ -path */RPMs/*.noarch.rpm -exec cp {} $TARGET_DIR/v$AWIPSII_RELEASE/noarch/ \;

if [ -d ${WORKSPACE}/eclipse-repo ]; then
   ls -1 ${WORKSPACE}/eclipse-repo/* > /dev/null 2>&1
   if [ $? -eq 0 ]; then
      sudo mkdir -p $TARGET_DIR/v$AWIPSII_RELEASE/cave
      sudo cp -v ${WORKSPACE}/eclipse-repo/* $TARGET_DIR/v$AWIPSII_RELEASE/cave/
   fi
fi

pushd . > /dev/null
cd $TARGET_DIR
if [ -h latest ]; then
   sudo rm -fv latest
fi

sudo cp ${WORKSPACE}/git/AWIPS2_build/installers/Linux/comps.xml $TARGET_DIR/v$AWIPSII_RELEASE
time sudo /usr/bin/createrepo -c cachedir -g ${WORKSPACE}/git/AWIPS2_build/installers/Linux/comps.xml --workers=20 . --no-database
if [ $? -ne 0 ]; then
   exit 1
fi

sudo ln -sf v$AWIPSII_RELEASE latest

popd > /dev/null

