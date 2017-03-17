#!/bin/bash

# The Postgresql install adds a configuration file to /etc/ld.so.conf.d/.  After ldconfig is run, the cache at /etc/ld.so.cache includes Postgresql libraries.
# /usr/lib64 is added to LD_LIBRARY_PATH to reference system libraries first
if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   export LD_LIBRARY_PATH=/usr/lib64:$LD_LIBRARY_PATH
   return;
fi

if [ -d /awips2/postgresql ]; then
   # Determine Where awips2-postgresql Has Been Installed.
   POSTGRESQL_INSTALL="/awips2/postgresql"
   if [ "${POSTGRESQL_INSTALL}" = "" ]; then
      return
   fi

   # Update The Environment.
   # Determine if awips2-postgresql is Already On LD_LIBRARY_PATH
   CHECK_PATH=`echo ${LD_LIBRARY_PATH} | grep ${POSTGRESQL_INSTALL}`
   if [ "${CHECK_PATH}" = "" ]; then
      # awips2-postgresql Is Not On LD_LIBRARY_PATH; Add It.
      export LD_LIBRARY_PATH=${POSTGRESQL_INSTALL}/lib:${POSTGRESQL_INSTALL}/lib32:${LD_LIBRARY_PATH}
   fi

   # Determine if awips2-postgresql Is Already Part Of The Path.
   CHECK_PATH=`echo ${PATH} | grep ${POSTGRESQL_INSTALL}`
   if [ "${CHECK_PATH}" = "" ]; then
      # awips2-postgresql Is Not In The Path; Add It To The Path.
      export PATH=${POSTGRESQL_INSTALL}/bin:${PATH}
   fi
fi
