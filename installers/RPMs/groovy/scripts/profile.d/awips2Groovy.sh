#!/bin/bash

if [ $(id -u) -eq 0 -a ! -v A2LIBS ]; then
   return;
fi

export GROOVY_HOME=/awips2/groovy
export PATH=${GROOVY_HOME}/bin:${PATH}
