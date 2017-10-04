#ifndef QPID_SYS_SYSTEMINFO_H
#define QPID_SYS_SYSTEMINFO_H

/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 *
 */

#include "qpid/sys/IntegerTypes.h"
#include "qpid/Address.h"
#include "qpid/CommonImportExport.h"
#include <vector>

namespace qpid {
namespace sys {

/**
 * Retrieve information about the system we are running on.
 * Results may be dependent on OS/hardware.
 */
namespace SystemInfo {
/**
 * Estimate available concurrency, e.g. number of CPU cores.
 * -1 means estimate not available on this platform.
 */
QPID_COMMON_EXTERN long concurrency();

/**
 * Get the local host name and set it in the specified.
 * Returns false if it can't be obtained and sets errno to any error value.
 */
QPID_COMMON_EXTERN bool getLocalHostname (Address &address);

/**
 * Get the names of all the network interfaces connected to
 * this host.
 * @param names Receives the list of interface names
 */
QPID_COMMON_EXTERN void getInterfaceNames(std::vector<std::string>& names );

/**
 * Get strings for each of the IP addresses associated with a named network
 * interface.
 * If there is no interface of that name an empty list will be returned.
 *
 * @param interface The name of the network interface
 * @param addresses The list of the strings for the IP addresses are pushed on the back of this parameter
 *                  to get just the list you need to clear the vector before using it.
 * @return true if an interface of the correct name was found, false otherwise
 */
QPID_COMMON_EXTERN bool getInterfaceAddresses(const std::string& interface, std::vector<std::string>& addresses);

/**
 * Retrieve system identifiers and versions. This is information that can
 * generally be retrieved via POSIX uname().
 *
 * @param osName   Receives the OS name; e.g., GNU/Linux or Windows
 * @param nodeName Receives the nodename. This may or may not match the
 *                 set hostname from getLocalHostname().
 * @param release  Receives the OS release identifier.
 * @param version  Receives the OS release version (kernel, build, sp, etc.)
 * @param machine  Receives the hardware type.
 */
QPID_COMMON_EXTERN void getSystemId (std::string &osName,
                                     std::string &nodeName,
                                     std::string &release,
                                     std::string &version,
                                     std::string &machine);

/**
 * Get the process ID of the current process.
 */
QPID_COMMON_EXTERN uint32_t getProcessId();

/**
 * Get the process ID of the parent of the current process.
 */
QPID_COMMON_EXTERN uint32_t getParentProcessId();

/**
 * Get the name of the current process (i.e. the name of the executable)
 */
QPID_COMMON_EXTERN std::string getProcessName();

/**
 * Can thread related primitives be trusted during runtime house-cleaning?
 * (i.e. static destructors, atexit()).
 */
QPID_COMMON_EXTERN bool threadSafeShutdown();


}}} // namespace qpid::sys::SystemInfo

#endif  /*!QPID_SYS_SYSTEMINFO_H*/
