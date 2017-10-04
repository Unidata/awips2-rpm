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
#include "qpid/messaging/Address.h"
#include "qpid/types/Variant.h"

#include "unit_test.h"

using namespace qpid::messaging;
using namespace qpid::types;

namespace qpid {
namespace tests {

QPID_AUTO_TEST_SUITE(AddressSuite)

QPID_AUTO_TEST_CASE(testParseNameOnly)
{
    Address address("my-topic");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());
}

QPID_AUTO_TEST_CASE(testParseSubject)
{
    Address address("my-topic/my-subject");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());
    BOOST_CHECK_EQUAL(std::string("my-subject"), address.getSubject());
}

QPID_AUTO_TEST_CASE(testParseOptions)
{
    Address address("my-topic; {a:bc, x:101, y:'a string'}");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());

    BOOST_CHECK_EQUAL(std::string("bc"), address.getOptions()["a"]);
    BOOST_CHECK_EQUAL(101, static_cast<int>(address.getOptions()["x"]));
    BOOST_CHECK_EQUAL(std::string("a string"), address.getOptions()["y"]);

    // Test asString() and asInt64() once here

    BOOST_CHECK_EQUAL(std::string("bc"), address.getOptions()["a"].asString());
    BOOST_CHECK_EQUAL(static_cast<uint16_t>(101), address.getOptions()["x"].asInt64());
    BOOST_CHECK_EQUAL(std::string("a string"), address.getOptions()["y"].asString());
}

QPID_AUTO_TEST_CASE(testParseSubjectAndOptions)
{
    Address address("my-topic/my-subject; {a:bc, x:101, y:'a string'}");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());
    BOOST_CHECK_EQUAL(std::string("my-subject"), address.getSubject());

    BOOST_CHECK_EQUAL(std::string("bc"), address.getOptions()["a"]);
    BOOST_CHECK_EQUAL(101, static_cast<int>(address.getOptions()["x"]));
    BOOST_CHECK_EQUAL(std::string("a string"), address.getOptions()["y"]);
}

QPID_AUTO_TEST_CASE(testParseNestedOptions)
{
    Address address("my-topic; {a:{p:202, q:'another string'}, x:101, y:'a string'}");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());
    BOOST_CHECK_EQUAL(202, static_cast<int>(address.getOptions()["a"].asMap()["p"]));
    BOOST_CHECK_EQUAL(std::string("another string"), address.getOptions()["a"].asMap()["q"]);
    BOOST_CHECK_EQUAL(std::string("a string"), address.getOptions()["y"]);
}

QPID_AUTO_TEST_CASE(testParseOptionsWithList)
{
    Address address("my-topic; {a:[202, 'another string'], x:101}");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());
    Variant::List& list = address.getOptions()["a"].asList();
    Variant::List::const_iterator i = list.begin();
    BOOST_CHECK(i != list.end());
    BOOST_CHECK_EQUAL((uint16_t) 202, i->asInt64());
    BOOST_CHECK(++i != list.end());
    BOOST_CHECK_EQUAL(std::string("another string"), i->asString());
    BOOST_CHECK_EQUAL((uint16_t) 101, address.getOptions()["x"].asInt64());
}

QPID_AUTO_TEST_CASE(testParseOptionsWithEmptyList)
{
    Address address("my-topic; {a:[], x:101}");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());
    Variant::List& list = address.getOptions()["a"].asList();
    BOOST_CHECK_EQUAL(list.size(), (size_t) 0);
    BOOST_CHECK_EQUAL((uint16_t) 101, address.getOptions()["x"].asInt64());
}

QPID_AUTO_TEST_CASE(testParseOptionsWithEmptyMap)
{
    Address address("my-topic; {a:{}, x:101}");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());
    Variant::Map& map = address.getOptions()["a"].asMap();
    BOOST_CHECK_EQUAL(map.size(), (size_t) 0);
    BOOST_CHECK_EQUAL((uint16_t) 101, address.getOptions()["x"].asInt64());
}

QPID_AUTO_TEST_CASE(testParseQuotedNameAndSubject)
{
    Address address("'my topic with / in it'/'my subject with ; in it'");
    BOOST_CHECK_EQUAL(std::string("my topic with / in it"), address.getName());
    BOOST_CHECK_EQUAL(std::string("my subject with ; in it"), address.getSubject());
}

QPID_AUTO_TEST_CASE(testParseOptionsWithEmptyStringAsValue)
{
    Address address("my-topic; {a:'', x:101}");
    BOOST_CHECK_EQUAL(std::string("my-topic"), address.getName());
    Variant a = address.getOptions()["a"];
    BOOST_CHECK_EQUAL(VAR_STRING, a.getType());
    std::string aVal = a;
    BOOST_CHECK(aVal.size() == 0);
    BOOST_CHECK_EQUAL((uint16_t) 101, address.getOptions()["x"].asInt64());
}

QPID_AUTO_TEST_SUITE_END()

}}
