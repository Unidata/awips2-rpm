#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/psql ]; then
   # Determine Where awips2-psql Has Been Installed.
   PSQL_INSTALL="/awips2/psql"

   # Determine If awips2-psql Is Already Part Of The Path.
   CHECK_PATH=`echo ${PATH} | grep ${PSQL_INSTALL}`
   if [ "${CHECK_PATH}" = "" ]; then
      # awips2-psql Is Not In The Path; Add It To The Path.
      export PATH=${PSQL_INSTALL}/bin:${PATH}
   fi
fi
