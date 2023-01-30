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
# Sep 10, 2018	6448     dlovely     Added netCDF and HDF5
# Apr 25, 2019	7812     dgilling    Added setuptools_scm.
# Apr 30, 2019	7824     dgilling    Added pkgconfig.
# Apr 30, 2019	7825     dgilling    Added Cython
# May 06, 2019	7842     dgilling    Added cftime.
# May 09, 2019	7829     dgilling    Added cycler, kiwisolver, subprocess32 and backports.functools_lru_cache.
# May 17, 2019  7830     dgilling    Added cheroot, contextlib2, jaraco.functools, more-itertools, portend, 
#                                    setuptools_scm_git_archive, tempora and zc.lockfile.
# Jun 17, 2019  7837     dgilling    Added funcsigs, mock, numpexpr and pbr.
# Apr 03, 2020  8128     randerso    Removed subprocess32 

if [ -z "${1}" ]; then
   echo "USAGE: $0 <PYTHON DIR STRING>"
else
   VERSION=${1}
   PYTHON=${VERSION%%-*}

   # We don't actually use the library nose anymore but we need this placeholder here not to break the build scripts
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

   VERSION=${VERSION##$PYPARSING-}
   NETCDF=${VERSION%%-*}

   VERSION=${VERSION##$NETCDF-}
   HDF5=${VERSION%%-*}

   VERSION=${VERSION##$HDF5-}
   SETUPTOOLS_SCM=${VERSION%%-*}

   VERSION=${VERSION##$SETUPTOOLS_SCM-}
   PKGCONFIG=${VERSION%%-*}

   VERSION=${VERSION##$PKGCONFIG-}
   CYTHON=${VERSION%%-*}

   VERSION=${VERSION##$CYTHON-}
   CFTIME=${VERSION%%-*}

   VERSION=${VERSION##$CFTIME-}
   CYCLER=${VERSION%%-*}

   VERSION=${VERSION##$CYCLER-}
   KIWISOLVER=${VERSION%%-*}

   VERSION=${VERSION##$KIWISOLVER-}
   
   # We don't actually use the library subprocess32 anymore but we need this placeholder here not to break the build scripts
   SUBPROCESS32=${VERSION%%-*}

   VERSION=${VERSION##$SUBPROCESS32-}
   BACKPORTS_LRU_CACHE=${VERSION%%-*}

   VERSION=${VERSION##$BACKPORTS_LRU_CACHE-}
   CHEROOT=${VERSION%%-*}

   VERSION=${VERSION##$CHEROOT-}
   CONTEXTLIB2=${VERSION%%-*}

   VERSION=${VERSION##$CONTEXTLIB2-}
   JARACO_FUNCTOOLS=${VERSION%%-*}

   VERSION=${VERSION##$JARACO_FUNCTOOLS-}
   MORE_ITERTOOLS=${VERSION%%-*}

   VERSION=${VERSION##$MORE_ITERTOOLS-}
   PORTEND=${VERSION%%-*}

   VERSION=${VERSION##$PORTEND-}
   SETUPTOOLS_SCM_GIT=${VERSION%%-*}

   VERSION=${VERSION##$SETUPTOOLS_SCM_GIT-}
   TEMPORA=${VERSION%%-*}

   VERSION=${VERSION##$TEMPORA-}
   ZC_LOCKFILE=${VERSION%%-*}

   VERSION=${VERSION##$ZC_LOCKFILE-}
   SHAPELY=${VERSION%%-*}

   VERSION=${VERSION##$SHAPELY-}
   MATPLOTLIB=${VERSION%%-*}

   VERSION=${VERSION##$MATPLOTLIB-}
   FUNCSIGS=${VERSION%%-*}

   VERSION=${VERSION##$FUNCSIGS-}
   MOCK=${VERSION%%-*}

   VERSION=${VERSION##$MOCK-}
   NUMEXPR=${VERSION%%-*}

   VERSION=${VERSION##$NUMEXPR-}
   PBR=${VERSION%%-*}

   VERSION=${VERSION##$PBR-}
   PYGOBJECT=${VERSION%%-*}

   VERSION=${VERSION##$PYGOBJECT-}
   PYCAIRO=${VERSION%%-*}

   FORMAT=" %-10s %8s\n"
   printf "\n"
   printf "$FORMAT" PACKAGE VERSION
   printf "=====================\n"
   printf "$FORMAT" Python $PYTHON
   printf "$FORMAT" Numpy $NUMPY
   printf "$FORMAT" Setuptools $SETUPTOOLS
   printf "$FORMAT" Setuptools_SCM $SETUPTOOLS_SCM
   printf "$FORMAT" Thrift $THRIFT
   printf "$FORMAT" H5py $H5PY
   printf "$FORMAT" Dateutil $DATEUTIL
   printf "$FORMAT" Pytz $PYTZ
   printf "$FORMAT" Six $SIX
   printf "$FORMAT" Pyparsing $PYPARSING
   printf "$FORMAT" netCDF $NETCDF
   printf "$FORMAT" HDF5 $HDF5
   printf "$FORMAT" pkgconfig $PKGCONFIG
   printf "$FORMAT" Cython $CYTHON
   printf "$FORMAT" cftime $CFTIME
   printf "$FORMAT" Cycler $CYCLER
   printf "$FORMAT" kiwisolver $KIWISOLVER
   printf "$FORMAT" backports.functools_lru_cache $BACKPORTS_LRU_CACHE
   printf "$FORMAT" Cheroot $CHEROOT
   printf "$FORMAT" contextlib2 $CONTEXTLIB2
   printf "$FORMAT" jaraco.functools $JARACO_FUNCTOOLS
   printf "$FORMAT" more-itertools $MORE_ITERTOOLS
   printf "$FORMAT" portend $PORTEND
   printf "$FORMAT" setuptools_scm_git_archive $SETUPTOOLS_SCM_GIT
   printf "$FORMAT" tempora $TEMPORA
   printf "$FORMAT" zc.lockfile $ZC_LOCKFILE
   printf "$FORMAT" shapely $SHAPELY
   printf "$FORMAT" matplotlib $MATPLOTLIB
   printf "$FORMAT" funcsigs $FUNCSIGS
   printf "$FORMAT" mock $MOCK
   printf "$FORMAT" NumExpr $NUMEXPR
   printf "$FORMAT" PBR $NUMEXPR
   printf "$FORMAT" pygobject $PYGOBJECT
   printf "$FORMAT" pycairo $PYCAIRO
   printf "\n"
fi

exit 


