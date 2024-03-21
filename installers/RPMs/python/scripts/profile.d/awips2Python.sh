#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi


if [ -d /awips2/python ]; then
   AWIPS_PYTHON=/awips2/python
   if [[ "$LD_LIBRARY_PATH" == "" ]]; then
       export LD_LIBRARY_PATH="/awips2/python/lib"
   else
       export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/awips2/python/lib"
   fi
   # Activate the virtual environment if it is not already active
   if [ -z "${VIRTUAL_ENV}" ]; then
       VIRTUAL_ENV_DISABLE_PROMPT=1 source "${AWIPS_PYTHON}"/bin/activate
   fi
fi
