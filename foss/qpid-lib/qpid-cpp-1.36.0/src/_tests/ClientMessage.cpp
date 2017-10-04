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
#include <iostream>
#include "qpid/messaging/Message.h"

#include "unit_test.h"

using namespace qpid::messaging;

namespace qpid {
namespace tests {

QPID_AUTO_TEST_SUITE(ClientMessageSuite)

QPID_AUTO_TEST_CASE(testCopyConstructor)
{
    Message m("my-data");
    m.setSubject("my-subject");
    m.getProperties()["a"] = "ABC";
    Message c(m);
    BOOST_CHECK_EQUAL(m.getContent(), c.getContent());
    BOOST_CHECK_EQUAL(m.getSubject(), c.getSubject());
    BOOST_CHECK_EQUAL(m.getProperties()["a"], c.getProperties()["a"]);
}

QPID_AUTO_TEST_SUITE_END()

}} // namespace qpid::tests
