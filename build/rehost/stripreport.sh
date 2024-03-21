#!/bin/sh

set -x

# HISTORY
-$$atejpk
# Mon Aug  9 13:21:46 EDT 2002	James Kepler
#	Only strip "not stripped" files
# Mon Aug 12 13:21:46 EDT 2002	James Kepler
#	Skip chmo & strip if list is null
# Mon Mar 10 15:30:46 EST 2003	James Kepler
#	Make Linux echo compatable with MINUSe
#	Add vi date command
# Tue Feb 10 16:58:00 EST 2004 Goran Zalar
#	Add -l option for symbolic links
# Wed Dec 15 07:18:00 CST 2021 Nate Jensen
#       Received from AWIPS SS CM

# VARIABLES
ERROR=""
STRIP=""
TARGET=""
NOTSTRIP=""
FILE=""
LINE=""
TYPE="f"
if [ `uname` = "Linux" ]
then
	MINUSe="-e"
	SYMLINK="-L"
else
	MINUSe=""
	SYMLINK=""
fi

# PROCESS PARAMETERS
while [ $# != 0 ]
do
	case ${1} in
		-l)	TYPE="l" ;;
		-s)	STRIP="y" ;;
		-help)	ERROR="${ERROR} \r" ;;
		-*)	ERROR="${ERROR}ERROR: Invalid option, ${1} \n" ;;
		*)	TARGET="$@"; break ;;
	esac
	shift
done

# ERROR CHECKING
if [ "${TARGET}" = "" ]
then
	ERROR="${ERROR}ERROR: No target files nor directories \n"
fi
if [ "${ERROR}" != "" ]
then
	echo ${MINUSe} "${ERROR}
		\rUsage: `basename $0` [-l] [-s] FILE... DIR...
		\r\t-l option, follow links, default is ordinary files 
		\r\t-s option, Strip the files, default is list only
		\r\tFILE... DIR... Files or directories to list or strip \n"
	exit 1
fi

# MAIN
date
pwd
echo ${MINUSe} "BEFORE STRIPPING:"
for FILE in $(find ${TARGET} -type ${TYPE})
do
	LINE=$(file ${SYMLINK} ${FILE} | grep "not stripped")
	if [ $? = 0 ]
	then
		echo ${MINUSe} ${LINE}
		NOTSTRIPPED="${NOTSTRIPPED} ${FILE}"
	fi
done
if [ "${STRIP}" = "y" ]
then
	if [ "${NOTSTRIPPED}" != "" ]
	then
		echo ${MINUSe} "\nAFTER STRIPPING:"
		chmod +w ${NOTSTRIPPED}
		strip ${NOTSTRIPPED}
	else
		echo ${MINUSe} "\tNo files to strip\n\nAFTER STRIPPING:"
	fi
	find ${TARGET} -type ${TYPE} -exec file ${SYMLINK} {} \; | grep "not stripped"
fi
