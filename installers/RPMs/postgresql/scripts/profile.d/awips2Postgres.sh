#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/postgresql ]; then
   # Determine Where awips2-postgresql Has Been Installed.
   POSTGRESQL_INSTALL="/awips2/postgresql"
   if [ "${POSTGRESQL_INSTALL}" = "" ]; then
      return
   fi

   # Determine if awips2-postgresql Is Already Part Of The Path.
   CHECK_PATH=`echo ${PATH} | grep ${POSTGRESQL_INSTALL}`
   if [ "${CHECK_PATH}" = "" ]; then
      # awips2-postgresql Is Not In The Path; Add It To The Path.
      export PATH=${POSTGRESQL_INSTALL}/bin:${PATH}
   fi
fi
