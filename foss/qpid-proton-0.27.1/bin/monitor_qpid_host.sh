#!/bin/bash
#===============================================================================
#
# Check running state and running statistics of QPID.
#
# DESCRIPTION
#
#   Collects various metrics and states of QPID and stores information under
#   /data/fxa/qpid
#
#   This script usually runs only from cron.
#
# BEHAVIOR
#
#   * No STDOUT/STDERR will appear in a terminal if script runs nominally.
#   * All STDOUT is forwarded to logs in /data/fxa/qpid
#   * /data/fxa/qpid/monitor_qpid_host.${date}.log should contain minimal
#     information unless errors were generated during execution.
#
# CHANGELOG
#
#   [v2.0] - 16 April 2021 - Bradley.McCune
#
#     Added
#     * Help prompt via `-h` command-line option to help document script use.
#     * `logCommand` reuses logic to run a command and forward the ouptut to a
#       file
#     * `runAndWait` reuses logic to run a command in the background and wait an
#       allotted amount of time for that process to complete.
#     * Documentation blocks in code
#     * Version number available via the `-V` option
#     * A couple simple echo statements have been added to the monitor_qpid_host
#       log to illustrate general actions being taken by the script.
#
#     Changed
#     * Replaced `jps | grep QPBRKR` with `pgrep -f QPBRKR`
#     * Standardized line spacing and general script syntax
#     * `nas` references updates to `nfs` to match HCI infrastructure changes
#     * `platformName` updated to parse longer FQDN hostname
#     * All log files older than 2 day will be gzipped to prevent them from
#       hogging too much disk space.
#       - Gzipped logs have a new `.1.gz` suffix to reduce naming conflicts on
#         weekly rollovers
#     * Changed `setupEnv` to `packLogFiles` since nothing about the environment
#       is touched in that function.
#
#     Removed
#     * Unused `qpidConn*` variables in `captureQpidStats`
#     * Unnecessary `echo >` log initialization.
#
#   [v1.0] - 20 July 2012 - kpj
#     Added
#     * Initial script
#
#===============================================================================

# Source environment files
. /awips2/etc/environment

# CONSTANTS
readonly LOG_DIRECTORY=/data/fxa/qpid
readonly NFS_HOST=nfs
readonly NFS_VOLUME=dataFXA
readonly VERSION=v2.0

# Globals
today=$(date +%A)
yesterday=$(date --date="yesterday" +%A)
logName=$(basename $0 .sh).${today}.log
yesterdayLogName=${logName/${today}/${yesterday}}
logFiles=(
  ${logName}
  ${today}-captureQpidHeapInfo.out
  ${today}-ipvsadm.out
  ${today}-lsof_qpid.out
  ${today}-netstat.out
  ${today}-qpid-stat.out
)
platformName=$(hostname | cut -d'-' -f2 | cut -d'.' -f1)

function _usage() {
  cat << EOF

Usage: sudo $0 [options]

Description:

  Log QPID running state and statistics at /data/fxa/qpid

  This script is usually executed from the CPV cron, but it can be run
  manually, as well.

  :Note: No output will appear in the terminal if script completes nominally.
    See log files for details.

Options:
  -h  This help prompt.
  -V  Print the version number and exit.

EOF
}

# Parse command-line options and print Help or Versioning
function _cli() {
  while getopts ":hV" OPTION; do
    case ${OPTION} in
      h) _usage
         exit 0
         ;;
      V) echo ${VERSION}
         exit 0
         ;;
      *) echoFail "No arguments expected by this script"
         _usage
         exit 1
         ;;
    esac
  done
}

function cleanup() {
  if [[ "${hadToMount}" ]]; then
    umount /data/fxa
  fi
}

function echoDate() {
  echo -ne "|-- $(date +"%Y%m%d %H:%M:%S")"
}

function echoFail() {
  echoDate && "\tERROR:\t$1"
}

# Run a command and forward the output to a log file.  Log any failures with
# running the command.
function logCommand() {
  local logFile="$1"
  local cmd="${@:2}"

  ${cmd} >> ${logFile} 2>&1
  echo "" >> ${logFile}

  if [[ $? -ne 0 ]]; then
    echoFail "Issue running [${cmd}]\n\tSee ${logFile} for details"
    return 1
  fi
}

# Compress logs last modified > 2 days ago
function packLogFiles() {
  echo "Compressing previous log files . . ."
  find ${LOG_DIRECTORY} \
    -mindepth 1 -maxdepth 1 \
    -mtime +1 \( -name "*.log" -o -name "*.out" \) \
    -exec gzip -v --force --suffix ".1.gz" {} \;
}

function printSectionHeader() {
  echo -ne "\n| START $(echoDate)----------------------------------------------------------------|\n"
}

# Return any PIDs of running QPID Brokers
function qpidPid() {
  pgrep -f "java.*-DPNAME=QPBRKR"
}

# Log any open file descriptors tied to a running qpidd
function runLsof() {
  local logFile="${LOG_DIRECTORY}/${today}-lsof_qpid.out"
  local returnCode=0

  printSectionHeader >> ${logFile}
  logCommand ${logFile} lsof -Pns -p ${runningQpidPid}
  (( returnCode+=$? ))

  return ${returnCode}
}

# Log a bunch of stats from qpidd
function captureQpidStat() {
  local logFile="${LOG_DIRECTORY}/${today}-qpid-stat.out"
  local returnCode=0
 
  printSectionHeader >> ${logFile}

  numQpidConnections=$(qpid-stat -c cpv1 | tail -n +4 | wc -l)
  echo -e "Total Number of QPID Connections: ${numQpidConnections}\n" >> ${logFile}

  local -A qpidStatsArgs=(
    [Brokers]="-b"
    [Connections]="-c"
    [Sessions]="-s"
    [Exchanges]="-e"
    [Queues]="-q -Smsg"
  )

  for arg in ${!qpidStatsArgs[@]}; do
    logCommand ${logFile} qpid-stat ${qpidStatsArgs[${arg}]} cpv1
    (( returnCode+=$? ))
  done

  return ${returnCode}
}

# Log any listening/established ports tied to qpidd
function captureNetstat() {
  local logFile="${LOG_DIRECTORY}/${today}-netstat.out"
  local returnCode=0

  printSectionHeader >> ${logFile}
  logCommand ${logFile} "netstat -tunape | grep :5672"
  (( returnCode+=$? ))

  return ${returnCode}
}

# Log the IPVS routing table and connections
function captureIpvs() {
  local logFile="${LOG_DIRECTORY}/${today}-ipvsadm.out"
  local returnCode=0

  printSectionHeader >> ${logFile}

  local -A ipvsArgs=(
    [Routes]="--list"
    [Stats]="--list --stats"
    [Connections]="--list --connection --sort"
  )

  for arg in ${!ipvsArgs[@]}; do
    logCommand ${logFile} ipvsadm ${ipvsArgs[${arg}]}
    (( returnCode+=$? ))
  done

  return ${returnCode}
}

# Log the memory statistics for qpidd
function captureQpidHeapInfo() {
  local logFile=${LOG_DIRECTORY}/${today}-$FUNCNAME.out
  local returnCode=0

  printSectionHeader >> ${logFile}

  if ! ps -p ${runningQpidPid} > /dev/null; then
    echoFail "Can no longer find previously running qpidd PID [${runningQpidPid}]: $(qpidPid)"
    return 1
  fi

  cat << HEAP >> ${logFile}
Found qpidd on PID ${runningQpidPid}

Forcing GC and getting remaining histogram......................................
$(su -l awips -c "jmap -histo:live ${runningQpidPid}")

Getting HEAP usage..............................................................
$(jhsdb jmap --heap --pid ${runningQpidPid})

Getting Garbage Collection Information..........................................
$(jstat -gcutil ${runningQpidPid} 1000 10)

HEAP
}

# Run a function, pass it into the background, and wait `timeout` seconds for
# it to complete.  If the process fails to finish before that time, the process
# is killed, and an error is generated.
function runAndWait() {
  local functionName="$1"
  local timeout="$2"
  local binaryToLog="$3"

  ${functionName} &
  local pid=$!
  _cnt=0
  while ps -p ${pid} > /dev/null; do
    sleep 1
    (( _cnt+=1 ))
    if [[ ${_cnt} -ge ${timeout} ]]; then
      echoFail "${binaryToLog} running for more than ${timeout} seconds, killing"
      kill -9 ${pid}
    fi
  done

  if ! wait ${pid}; then
    echoFail "Grabbing output of ${binaryToLog} on qpidd failed"
  fi
}

function main() {
  printSectionHeader
  packLogFiles

  if ! grep /data/fxa /proc/mounts | grep nfs 2>&1 > /dev/null; then
    # /data/fxa isn't an nfs mount
    if mount ${NFS_HOST}:${NFS_VOLUME} /data/fxa; then
      hadToMount=true
    else
      echoFail "Couldn't mount /data/fxa and that is where the log goes!"
      exit 1
    fi
  fi

  # now check write permission
  if [[ ! -d ${LOG_DIRECTORY} ]]; then
    if ! mkdir -p ${LOG_DIRECTORY} > /dev/null 2>&1; then
      echoFail "Couldn't create ${LOG_DIRECTORY}"
      exit 1
    fi
  fi

  if ! touch ${LOG_DIRECTORY}/testfile > /dev/null 2>&1; then
    echoFail "No write permissions to ${LOG_DIRECTORY}"
    exit 1
  else
    rm ${LOG_DIRECTORY}/testfile
  fi

  runningQpidPid=$(qpidPid)
  if [[ -z ${runningQpidPid} ]]; then
    echoFail "No running qpidd brokers could be found."
    exit 1
  fi

  echo "Collecting QPID information . . ."
  runAndWait runLsof 10 lsof
  runAndWait captureQpidStat 30 qpid-stat
  runAndWait captureQpidHeapInfo 60 "java-heap"
  runAndWait captureNetstat 10 netstat
  runAndWait captureIpvs 20 ipvsadm

  echo "Data collection complete and logged at ${LOG_DIRECTORY}."
} >> ${LOG_DIRECTORY}/${logName} 2>&1

_cli "$@"
main
