#!/bin/csh

set PYTHON_INSTALL="/awips2/python"
setenv AWIPS_PYTHON ${PYTHON_INSTALL}

if $?LD_LIBRARY_PATH then
   setenv LD_LIBRARY_PATH ${PYTHON_INSTALL}/lib:$LD_LIBRARY_PATH
else
   setenv LD_LIBRARY_PATH ${PYTHON_INSTALL}/lib
endif

# Activate the virtual environment if it is not already active
if ! $?VIRTUAL_ENV then
    if (! "$?prompt") then
        set prompt=""
    endif
    setenv VIRTUAL_ENV_DISABLE_PROMPT 1
    source ${PYTHON_INSTALL}/bin/activate.csh
    unsetenv VIRTUAL_ENV_DISABLE_PROMPT
endif
