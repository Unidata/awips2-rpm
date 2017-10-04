/*
 *
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

#include "qpid/broker/BrokerOptions.h"
#include <stdlib.h>
#include <windows.h>

namespace qpid {
namespace broker {

const std::string BrokerOptions::DEFAULT_DATA_DIR_LOCATION("\\TEMP");
const std::string BrokerOptions::DEFAULT_DATA_DIR_NAME("\\QPIDD.DATA");
const std::string BrokerOptions::DEFAULT_PAGED_QUEUE_DIR("\\PQ");

std::string
BrokerOptions::getHome() {
    std::string home;
#ifdef _MSC_VER
    char home_c[MAX_PATH+1];
    size_t unused;
    if (0 == getenv_s (&unused, home_c, sizeof(home_c), "HOME"))
        home += home_c;
#else
    char *home_c = getenv("HOME");
    if (home_c)
        home += home_c;
#endif
    return home;
}

}}   // namespace qpid::broker
