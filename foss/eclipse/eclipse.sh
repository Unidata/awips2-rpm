# usage:
# eclipse.sh [args]    -- launches eclipse using specified command line args
# eclipse.sh           -- launches Eclipse with default command line args

dir=${0%/*}
if [ "${dir}" = "$0" ]; then
   dir="."
fi

PYTHON_INSTALL="/awips2/python"
JAVA_INSTALL="/awips2/java"
ANT_INSTALL="/awips2/ant"
ECLIPSE_INSTALL="/awips2/eclipse"
cd ${dir}

# grab the CL argument; if none set a reasonable default
if [ $# -ne 0 ]; then
   # there are arguments, convert them into a string
   args=${1}
   shift 1
   for a in $@; do
      args="${args} ${a}"
   done
else
   # set a reasonable default for performance
   args='-clean -vmargs -Xms512m -Xmx4G'
fi

# setup environment variables
export JAVA_HOME=${JAVA_INSTALL}
export ANT_HOME=${ANT_INSTALL}

. /etc/profile.d/awips2.sh

# update path type variables
export LD_PRELOAD=${PYTHON_INSTALL}/lib/libpython2.7.so
export LD_LIBRARY_PATH=${PYTHON_INSTALL}/lib:$LD_LIBRARY_PATH:/usr/local/lib
export PATH=${ECLIPSE_INSTALL}:${PYTHON_INSTALL}/bin:${JAVA_INSTALL}/bin:$PATH
echo ""
echo "export LD_PRELOAD=$LD_PRELOAD"
echo ""
echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
echo ""
echo "export PATH=$PATH"
echo ""
# determine if cave has been installed for TMCP_HOME
rpm -q awips2-cave > /dev/null 2>&1
if [ $? -ne 0 ]; then
   CAVE_INSTALL="/awips2/cave"
   export TMCP_HOME=${CAVE_INSTALL}/caveEnvironment
else
   echo "WARNING: awips2-cave is not installed; so, TMCP_HOME will not be set."
fi

echo "./eclipse ${args} &"
nohup ./eclipse ${args} > /dev/null 2>&1 &
echo ""
echo "Successful Eclipse Startup ..."
exit 0
