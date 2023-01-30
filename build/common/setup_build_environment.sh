#!/bin/bash -x

#
# Sets updates the environment variables for the build.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial import from awipscm

source ${WORKSPACE}/git/AWIPS2_build/build/common/version_release.sh

# Rewrite the rpm environment setup script.
cd ${WORKSPACE}/baseline/rpms/build/${_architecture}

if [ $? -ne 0 ]; then
   exit 1
fi
if [ -f buildEnvironment.sh ]; then
   /bin/rm buildEnvironment.sh
fi

/bin/touch buildEnvironment.sh
/bin/echo "#!/bin/bash" >> buildEnvironment.sh
/bin/echo "" >> buildEnvironment.sh
/bin/echo "export AWIPSII_VERSION=\"${AWIPSII_VERSION}\"" >> buildEnvironment.sh
/bin/echo "export AWIPSII_RELEASE=\"${AWIPSII_RELEASE}\"" >> buildEnvironment.sh
/bin/echo "" >> buildEnvironment.sh
/bin/echo "export AWIPSII_TOP_DIR=\"${WORKSPACE}/rpmbuild\"" >> buildEnvironment.sh
/bin/echo "export WORKSPACE=\"${WORKSPACE}/baseline\"" >> buildEnvironment.sh
/bin/echo "export UFRAME_ECLIPSE=\"/awips2/eclipse/\"" >> buildEnvironment.sh
/bin/echo "export AWIPSII_STATIC_FILES=\"${WORKSPACE}/git/AWIPS2_static\"" >> buildEnvironment.sh
/bin/echo "export AWIPSII_BUILD_ROOT=\"/tmp/$JOB_NAME/awips-component\"" >> buildEnvironment.sh
/bin/echo "export AWIPSII_BUILD_SITE=\"${AWIPSII_BUILD_SITE}\"" >> buildEnvironment.sh
/bin/echo "export REPO_DEST=\"${WORKSPACE}/eclipse-repo\"" >> buildEnvironment.sh

if [ -d ${WORKSPACE}/eclipse-repo ]; then
   /bin/rm -rf ${WORKSPACE}/eclipse-repo
fi
mkdir -p ${WORKSPACE}/eclipse-repo

echo "Setup ${WORKSPACE}/baseline/rpms/build/${_architecture}/buildEnvironment.sh"

cat ${WORKSPACE}/baseline/rpms/build/${_architecture}/buildEnvironment.sh

