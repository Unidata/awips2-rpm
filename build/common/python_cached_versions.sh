#!/bin/bash

#
# This script will print out the version of each Python package
# that is installed into a cached directory.
#
# SCRIPT HISTORY
#
# Date          Ticket#  Engineer    Description
# ------------- -------- ----------- -----------------------------
# Mar 10, 2016  4734     dlovely     Initial creation

if [ -z "${1}" ]; then
   echo "USAGE: $0 <PYTHON DIR STRING>"
else
   VERSION=${1}
   PYTHON=${VERSION%%-*}

   VERSION=${VERSION##$PYTHON-}
   NOSE=${VERSION%%-*}

   VERSION=${VERSION##$NOSE-}
   NUMPY=${VERSION%%-*}

   VERSION=${VERSION##$NUMPY-}
   SETUPTOOLS=${VERSION%%-*}

   VERSION=${VERSION##$SETUPTOOLS-}
   THRIFT=${VERSION%%-*}

   VERSION=${VERSION##$THRIFT-}
   H5PY=${VERSION%%-*}

   VERSION=${VERSION##$H5PY-}
   DATEUTIL=${VERSION%%-*}

   VERSION=${VERSION##$DATEUTIL-}
   PYTZ=${VERSION%%-*}

   VERSION=${VERSION##$PYTZ-}
   SIX=${VERSION%%-*}

   VERSION=${VERSION##$SIX-}
   PYPARSING=${VERSION%%-*}

   FORMAT=" %-10s %8s\n"
   printf "\n"
   printf "$FORMAT" PACKAGE VERSION
   printf "=====================\n"
   printf "$FORMAT" Python $PYTHON
   printf "$FORMAT" Nose $NOSE
   printf "$FORMAT" Numpy $NUMPY
   printf "$FORMAT" Setuptools $SETUPTOOLS
   printf "$FORMAT" Thrift $THRIFT
   printf "$FORMAT" H5py $H5PY
   printf "$FORMAT" Dateutil $DATEUTIL
   printf "$FORMAT" Pytz $PYTZ
   printf "$FORMAT" Six $SIX
   printf "$FORMAT" Pyparsing $PYPARSING
   printf "\n"
fi

exit 0

