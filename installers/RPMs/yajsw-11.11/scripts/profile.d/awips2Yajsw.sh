#!/bin/bash

if [ -d /awips2/yajsw ]; then
   YAJSW_INSTALL="/awips2/yajsw"
# Update The Environment
   export YAJSW_HOME=${YAJSW_INSTALL}

   if [ `arch` == 'x86_64' ]; then
      export LD_LIBRARY_PATH=/awips2/yajsw/lib/core/jna/com/sun/jna/linux-amd64:$LD_LIBRARY_PATH
   fi

fi
