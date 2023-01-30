#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

if [ -d /awips2/yajsw ]; then
   YAJSW_INSTALL="/awips2/yajsw"
# Update The Environment
   export YAJSW_HOME=${YAJSW_INSTALL}
fi
