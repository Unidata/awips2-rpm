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
#include "MessagingFixture.h"
#include "unit_test.h"
#include "test_tools.h"
#include "qpid/messaging/Address.h"
#include "qpid/messaging/Connection.h"
#include "qpid/messaging/Message.h"
#include "qpid/messaging/Receiver.h"
#include "qpid/messaging/Sender.h"
#include "qpid/messaging/Session.h"
#include "qpid/client/Connection.h"
#include "qpid/client/Session.h"
#include "qpid/framing/ExchangeQueryResult.h"
#include "qpid/framing/reply_exceptions.h"
#include "qpid/framing/Uuid.h"
#include "qpid/sys/Time.h"
#include <boost/assign.hpp>
#include <boost/format.hpp>
#include <string>
#include <vector>

namespace qpid {
namespace tests {

QPID_AUTO_TEST_SUITE(MessagingSessionTests)

using namespace qpid::messaging;
using namespace qpid::types;
using namespace qpid;
using qpid::broker::BrokerOptions;
using qpid::framing::Uuid;


QPID_AUTO_TEST_CASE(testSimpleSendReceive)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out("test-message");
    out.setSubject("test-subject");
    sender.send(out);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(Duration::SECOND * 5);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
    BOOST_CHECK_EQUAL(in.getSubject(), out.getSubject());
}

QPID_AUTO_TEST_CASE(testSyncSendReceive)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out("test-message");
    sender.send(out, true);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(Duration::IMMEDIATE);
    fix.session.acknowledge(true);
    BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
}

QPID_AUTO_TEST_CASE(testSendReceiveHeaders)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out("test-message");
    for (uint i = 0; i < 10; ++i) {
        out.getProperties()["a"] = i;
        out.setProperty("b", i + 100);
        sender.send(out);
    }
    uint8_t v1(255u);
    int8_t v2(-120);
    out.getProperties()["c"] = v1;
    out.getProperties()["d"] = v2;
    sender.send(out);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in;
    for (uint i = 0; i < 10; ++i) {
        BOOST_CHECK(receiver.fetch(in, Duration::SECOND * 5));
        BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
        BOOST_CHECK_EQUAL(in.getProperties()["a"].asUint32(), i);
        BOOST_CHECK_EQUAL(in.getProperties()["b"].asUint32(), i + 100);
        fix.session.acknowledge();
    }
    BOOST_CHECK(receiver.fetch(in, Duration::SECOND * 5));
    Variant& c = in.getProperties()["c"];
    BOOST_CHECK_EQUAL(c.getType(), VAR_UINT8);
    BOOST_CHECK_EQUAL(c.asUint8(), v1);
    Variant& d = in.getProperties()["d"];
    BOOST_CHECK_EQUAL(d.getType(), VAR_INT8);
    BOOST_CHECK_EQUAL(d.asInt8(), v2);
}

QPID_AUTO_TEST_CASE(testSenderError)
{
    MessagingFixture fix;
    ScopedSuppressLogging sl;
    BOOST_CHECK_THROW(fix.session.createSender("NonExistentAddress"), qpid::messaging::NotFound);
    fix.session = fix.connection.createSession();
    BOOST_CHECK_THROW(fix.session.createSender("NonExistentAddress; {create:receiver}"),
                      qpid::messaging::NotFound);
}

QPID_AUTO_TEST_CASE(testReceiverError)
{
    MessagingFixture fix;
    ScopedSuppressLogging sl;
    BOOST_CHECK_THROW(fix.session.createReceiver("NonExistentAddress"), qpid::messaging::NotFound);
    fix.session = fix.connection.createSession();
    BOOST_CHECK_THROW(fix.session.createReceiver("NonExistentAddress; {create:sender}"),
                      qpid::messaging::NotFound);
}

QPID_AUTO_TEST_CASE(testSimpleTopic)
{
    TopicFixture fix;

    Sender sender = fix.session.createSender(fix.topic);
    Message msg("one");
    sender.send(msg);
    Receiver sub1 = fix.session.createReceiver(fix.topic);
    sub1.setCapacity(10u);
    msg.setContent("two");
    sender.send(msg);
    Receiver sub2 = fix.session.createReceiver(fix.topic);
    sub2.setCapacity(10u);
    msg.setContent("three");
    sender.send(msg);
    Receiver sub3 = fix.session.createReceiver(fix.topic);
    sub3.setCapacity(10u);
    msg.setContent("four");
    sender.send(msg);
    BOOST_CHECK_EQUAL(fetch(sub2, 2), boost::assign::list_of<std::string>("three")("four"));
    sub2.close();

    msg.setContent("five");
    sender.send(msg);
    BOOST_CHECK_EQUAL(fetch(sub1, 4), boost::assign::list_of<std::string>("two")("three")("four")("five"));
    BOOST_CHECK_EQUAL(fetch(sub3, 2), boost::assign::list_of<std::string>("four")("five"));
    Message in;
    BOOST_CHECK(!sub2.fetch(in, Duration::IMMEDIATE));//TODO: or should this raise an error?


    //TODO: check pending messages...
}

QPID_AUTO_TEST_CASE(testNextReceiver)
{
    MultiQueueFixture fix;

    for (uint i = 0; i < fix.queues.size(); i++) {
        Receiver r = fix.session.createReceiver(fix.queues[i]);
        r.setCapacity(10u);
    }

    for (uint i = 0; i < fix.queues.size(); i++) {
        Sender s = fix.session.createSender(fix.queues[i]);
        Message msg((boost::format("Message_%1%") % (i+1)).str());
        s.send(msg);
    }

    for (uint i = 0; i < fix.queues.size(); i++) {
        Message msg;
        BOOST_CHECK(fix.session.nextReceiver().fetch(msg, Duration::SECOND));
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("Message_%1%") % (i+1)).str());
    }
}

QPID_AUTO_TEST_CASE(testMapMessage)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out;
    Variant::Map content;
    content["abc"] = "def";
    content["pi"] = 3.14f;
    Variant utf8("A utf 8 string");
    utf8.setEncoding("utf8");
    content["utf8"] = utf8;
    Variant utf16("\x00\x61\x00\x62\x00\x63");
    utf16.setEncoding("utf16");
    content["utf16"] = utf16;
    encode(content, out);
    sender.send(out);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(5 * Duration::SECOND);
    Variant::Map view;
    decode(in, view);
    BOOST_CHECK_EQUAL(view["abc"].asString(), "def");
    BOOST_CHECK_EQUAL(view["pi"].asFloat(), 3.14f);
    BOOST_CHECK_EQUAL(view["utf8"].asString(), utf8.asString());
    BOOST_CHECK_EQUAL(view["utf8"].getEncoding(), utf8.getEncoding());
    BOOST_CHECK_EQUAL(view["utf16"].asString(), utf16.asString());
    BOOST_CHECK_EQUAL(view["utf16"].getEncoding(), utf16.getEncoding());
    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testMapMessageWithInitial)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out;
    Variant::Map imap;
    imap["abc"] = "def";
    imap["pi"] = 3.14f;
    encode(imap, out);
    sender.send(out);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(5 * Duration::SECOND);
    Variant::Map view;
    decode(in, view);
    BOOST_CHECK_EQUAL(view["abc"].asString(), "def");
    BOOST_CHECK_EQUAL(view["pi"].asFloat(), 3.14f);
    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testListMessage)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out;
    Variant::List content;
    content.push_back(Variant("abc"));
    content.push_back(Variant(1234));
    content.push_back(Variant("def"));
    content.push_back(Variant(56.789));
    encode(content, out);
    sender.send(out);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(5 * Duration::SECOND);
    Variant::List view;
    decode(in, view);
    BOOST_CHECK_EQUAL(view.size(), content.size());
    BOOST_CHECK_EQUAL(view.front().asString(), "abc");
    BOOST_CHECK_EQUAL(view.back().asDouble(), 56.789);

    Variant::List::const_iterator i = view.begin();
    BOOST_CHECK(i != view.end());
    BOOST_CHECK_EQUAL(i->asString(), "abc");
    BOOST_CHECK(++i != view.end());
    BOOST_CHECK_EQUAL(i->asInt64(), 1234);
    BOOST_CHECK(++i != view.end());
    BOOST_CHECK_EQUAL(i->asString(), "def");
    BOOST_CHECK(++i != view.end());
    BOOST_CHECK_EQUAL(i->asDouble(), 56.789);
    BOOST_CHECK(++i == view.end());

    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testListMessageWithInitial)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out;
    Variant::List ilist;
    ilist.push_back(Variant("abc"));
    ilist.push_back(Variant(1234));
    ilist.push_back(Variant("def"));
    ilist.push_back(Variant(56.789));
    encode(ilist, out);
    sender.send(out);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(5 * Duration::SECOND);
    Variant::List view;
    decode(in, view);
    BOOST_CHECK_EQUAL(view.size(), ilist.size());
    BOOST_CHECK_EQUAL(view.front().asString(), "abc");
    BOOST_CHECK_EQUAL(view.back().asDouble(), 56.789);

    Variant::List::const_iterator i = view.begin();
    BOOST_CHECK(i != view.end());
    BOOST_CHECK_EQUAL(i->asString(), "abc");
    BOOST_CHECK(++i != view.end());
    BOOST_CHECK_EQUAL(i->asInt64(), 1234);
    BOOST_CHECK(++i != view.end());
    BOOST_CHECK_EQUAL(i->asString(), "def");
    BOOST_CHECK(++i != view.end());
    BOOST_CHECK_EQUAL(i->asDouble(), 56.789);
    BOOST_CHECK(++i == view.end());

    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testReject)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message m1("reject-me");
    sender.send(m1);
    Message m2("accept-me");
    sender.send(m2);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(5 * Duration::SECOND);
    BOOST_CHECK_EQUAL(in.getContent(), m1.getContent());
    fix.session.reject(in);
    in = receiver.fetch(5 * Duration::SECOND);
    BOOST_CHECK_EQUAL(in.getContent(), m2.getContent());
    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testAvailable)
{
    MultiQueueFixture fix;

    Receiver r1 = fix.session.createReceiver(fix.queues[0]);
    r1.setCapacity(100);

    Receiver r2 = fix.session.createReceiver(fix.queues[1]);
    r2.setCapacity(100);

    Sender s1 = fix.session.createSender(fix.queues[0]);
    Sender s2 = fix.session.createSender(fix.queues[1]);

    for (uint i = 0; i < 10; ++i) {
        s1.send(Message((boost::format("A_%1%") % (i+1)).str()));
    }
    for (uint i = 0; i < 5; ++i) {
        s2.send(Message((boost::format("B_%1%") % (i+1)).str()));
    }
    qpid::sys::sleep(1);//is there any avoid an arbitrary sleep while waiting for messages to be dispatched?
    for (uint i = 0; i < 5; ++i) {
        BOOST_CHECK_EQUAL(fix.session.getReceivable(), 15u - 2*i);
        BOOST_CHECK_EQUAL(r1.getAvailable(), 10u - i);
        BOOST_CHECK_EQUAL(r1.fetch().getContent(), (boost::format("A_%1%") % (i+1)).str());
        BOOST_CHECK_EQUAL(r2.getAvailable(), 5u - i);
        BOOST_CHECK_EQUAL(r2.fetch().getContent(), (boost::format("B_%1%") % (i+1)).str());
        fix.session.acknowledge();
    }
    for (uint i = 5; i < 10; ++i) {
        BOOST_CHECK_EQUAL(fix.session.getReceivable(), 10u - i);
        BOOST_CHECK_EQUAL(r1.getAvailable(), 10u - i);
        BOOST_CHECK_EQUAL(r1.fetch().getContent(), (boost::format("A_%1%") % (i+1)).str());
    }
}

QPID_AUTO_TEST_CASE(testUnsettledAcks)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    for (uint i = 0; i < 10; ++i) {
        sender.send(Message((boost::format("Message_%1%") % (i+1)).str()));
    }
    Receiver receiver = fix.session.createReceiver(fix.queue);
    for (uint i = 0; i < 10; ++i) {
        BOOST_CHECK_EQUAL(receiver.fetch().getContent(), (boost::format("Message_%1%") % (i+1)).str());
    }
    BOOST_CHECK_EQUAL(fix.session.getUnsettledAcks(), 0u);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(fix.session.getUnsettledAcks(), 10u);
    fix.session.sync();
    BOOST_CHECK_EQUAL(fix.session.getUnsettledAcks(), 0u);
}

QPID_AUTO_TEST_CASE(testUnsettledSend)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    send(sender, 10);
    //Note: this test relies on 'inside knowledge' of the sender
    //implementation and the fact that the simple test case makes it
    //possible to predict when completion information will be sent to
    //the client. TODO: is there a better way of testing this?
    BOOST_CHECK_EQUAL(sender.getUnsettled(), 10u);
    fix.session.sync();
    BOOST_CHECK_EQUAL(sender.getUnsettled(), 0u);

    Receiver receiver = fix.session.createReceiver(fix.queue);
    receive(receiver, 10);
    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testBrowse)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    send(sender, 10);
    Receiver browser1 = fix.session.createReceiver(fix.queue + "; {mode:browse}");
    receive(browser1, 10);
    Receiver browser2 = fix.session.createReceiver(fix.queue + "; {mode:browse}");
    receive(browser2, 10);
    Receiver releaser1 = fix.session.createReceiver(fix.queue);
    Message m1 = releaser1.fetch(messaging::Duration::SECOND*5);
    BOOST_CHECK(!m1.getRedelivered());
    fix.session.release(m1);
    Receiver releaser2 = fix.session.createReceiver(fix.queue);
    Message m2 = releaser2.fetch(messaging::Duration::SECOND*5);
    BOOST_CHECK(m2.getRedelivered());
    fix.session.release(m2);
    Receiver consumer = fix.session.createReceiver(fix.queue);
    receive(consumer, 10);
    fix.session.acknowledge();
}

struct QueueCreatePolicyFixture : public MessagingFixture
{
    qpid::messaging::Address address;

    QueueCreatePolicyFixture(const std::string& a) : address(a) {}

    void test()
    {
        ping(address);
        BOOST_CHECK(admin.checkQueueExists(address.getName()));
    }

    ~QueueCreatePolicyFixture()
    {
        admin.deleteQueue(address.getName());
    }
};

QPID_AUTO_TEST_CASE(testCreatePolicyQueueAlways)
{
    QueueCreatePolicyFixture fix("#; {create:always, node:{type:queue}}");
    fix.test();
}

QPID_AUTO_TEST_CASE(testCreatePolicyQueueReceiver)
{
    QueueCreatePolicyFixture fix("#; {create:receiver, node:{type:queue}}");
    Receiver r = fix.session.createReceiver(fix.address);
    fix.test();
    r.close();
}

QPID_AUTO_TEST_CASE(testCreatePolicyQueueSender)
{
    QueueCreatePolicyFixture fix("#; {create:sender, node:{type:queue}}");
    Sender s = fix.session.createSender(fix.address);
    fix.test();
    s.close();
}

struct ExchangeCreatePolicyFixture : public MessagingFixture
{
    qpid::messaging::Address address;
    const std::string exchangeType;

    ExchangeCreatePolicyFixture(const std::string& a, const std::string& t) :
        address(a), exchangeType(t) {}

    void test()
    {
        ping(address);
        std::string actualType;
        BOOST_CHECK(admin.checkExchangeExists(address.getName(), actualType));
        BOOST_CHECK_EQUAL(exchangeType, actualType);
    }

    ~ExchangeCreatePolicyFixture()
    {
        admin.deleteExchange(address.getName());
    }
};

QPID_AUTO_TEST_CASE(testCreatePolicyTopic)
{
    ExchangeCreatePolicyFixture fix("#; {create:always, node:{type:topic}}",
                                  "topic");
    fix.test();
}

QPID_AUTO_TEST_CASE(testCreatePolicyTopicReceiverFanout)
{
    ExchangeCreatePolicyFixture fix("#/my-subject; {create:receiver, node:{type:topic, x-declare:{type:fanout}}}", "fanout");
    Receiver r = fix.session.createReceiver(fix.address);
    fix.test();
    r.close();
}

QPID_AUTO_TEST_CASE(testCreatePolicyTopicSenderDirect)
{
    ExchangeCreatePolicyFixture fix("#/my-subject; {create:sender, node:{type:topic, x-declare:{type:direct}}}", "direct");
    Sender s = fix.session.createSender(fix.address);
    fix.test();
    s.close();
}

struct DeletePolicyFixture : public MessagingFixture
{
    enum Mode {RECEIVER, SENDER, ALWAYS, NEVER};

    std::string getPolicy(Mode mode)
    {
        switch (mode) {
          case SENDER:
            return "{delete:sender}";
          case RECEIVER:
            return "{delete:receiver}";
          case ALWAYS:
            return "{delete:always}";
          case NEVER:
            return "{delete:never}";
        }
        return "";
    }

    void testAll()
    {
        test(RECEIVER);
        test(SENDER);
        test(ALWAYS);
        test(NEVER);
    }

    virtual ~DeletePolicyFixture() {}
    virtual void create(const qpid::messaging::Address&) = 0;
    virtual void destroy(const qpid::messaging::Address&) = 0;
    virtual bool exists(const qpid::messaging::Address&) = 0;

    void test(Mode mode)
    {
        qpid::messaging::Address address("testqueue#; " + getPolicy(mode));
        create(address);

        Sender s = session.createSender(address);
        Receiver r = session.createReceiver(address);
        switch (mode) {
          case RECEIVER:
            s.close();
            BOOST_CHECK(exists(address));
            r.close();
            BOOST_CHECK(!exists(address));
            break;
          case SENDER:
            r.close();
            BOOST_CHECK(exists(address));
            s.close();
            BOOST_CHECK(!exists(address));
            break;
          case ALWAYS:
            s.close();
            BOOST_CHECK(!exists(address));
            break;
          case NEVER:
            r.close();
            BOOST_CHECK(exists(address));
            s.close();
            BOOST_CHECK(exists(address));
            destroy(address);
        }
    }
};

struct QueueDeletePolicyFixture : DeletePolicyFixture
{
    void create(const qpid::messaging::Address& address)
    {
        admin.createQueue(address.getName());
    }
    void destroy(const qpid::messaging::Address& address)
    {
        admin.deleteQueue(address.getName());
    }
    bool exists(const qpid::messaging::Address& address)
    {
        return admin.checkQueueExists(address.getName());
    }
};

struct ExchangeDeletePolicyFixture : DeletePolicyFixture
{
    const std::string exchangeType;
    ExchangeDeletePolicyFixture(const std::string type = "topic") : exchangeType(type) {}

    void create(const qpid::messaging::Address& address)
    {
        admin.createExchange(address.getName(), exchangeType);
    }
    void destroy(const qpid::messaging::Address& address)
    {
        admin.deleteExchange(address.getName());
    }
    bool exists(const qpid::messaging::Address& address)
    {
        std::string actualType;
        return admin.checkExchangeExists(address.getName(), actualType) && actualType == exchangeType;
    }
};

QPID_AUTO_TEST_CASE(testDeletePolicyQueue)
{
    QueueDeletePolicyFixture fix;
    fix.testAll();
}

QPID_AUTO_TEST_CASE(testDeletePolicyExchange)
{
    ExchangeDeletePolicyFixture fix;
    fix.testAll();
}

QPID_AUTO_TEST_CASE(testAssertPolicyQueue)
{
    MessagingFixture fix;
    std::string a1 = "q; {create:always, assert:always, node:{type:queue, durable:false, x-declare:{arguments:{qpid.max-count:100}}}}";
    Sender s1 = fix.session.createSender(a1);
    s1.close();
    Receiver r1 = fix.session.createReceiver(a1);
    r1.close();

    std::string a2 = "q; {assert:receiver, node:{durable:true, x-declare:{arguments:{qpid.max-count:100}}}}";
    Sender s2 = fix.session.createSender(a2);
    s2.close();
    BOOST_CHECK_THROW(fix.session.createReceiver(a2), qpid::messaging::AssertionFailed);

    std::string a3 = "q; {assert:sender, node:{x-declare:{arguments:{qpid.max-count:99}}}}";
    BOOST_CHECK_THROW(fix.session.createSender(a3), qpid::messaging::AssertionFailed);
    Receiver r3 = fix.session.createReceiver(a3);
    r3.close();

    fix.admin.deleteQueue("q");
}

QPID_AUTO_TEST_CASE(testAssertExchangeOption)
{
    MessagingFixture fix;
    std::string a1 = "e; {create:always, assert:always, node:{type:topic, x-declare:{type:direct, arguments:{qpid.msg_sequence:True}}}}";
    Sender s1 = fix.session.createSender(a1);
    s1.close();
    Receiver r1 = fix.session.createReceiver(a1);
    r1.close();

    std::string a2 = "e; {assert:receiver, node:{type:topic, x-declare:{type:fanout, arguments:{qpid.msg_sequence:True}}}}";
    Sender s2 = fix.session.createSender(a2);
    s2.close();
    BOOST_CHECK_THROW(fix.session.createReceiver(a2), qpid::messaging::AssertionFailed);

    std::string a3 = "e; {assert:sender, node:{x-declare:{arguments:{qpid.msg_sequence:False}}}}";
    BOOST_CHECK_THROW(fix.session.createSender(a3), qpid::messaging::AssertionFailed);
    Receiver r3 = fix.session.createReceiver(a3);
    r3.close();

    fix.admin.deleteExchange("e");
}

QPID_AUTO_TEST_CASE(testGetSender)
{
    QueueFixture fix;
    std::string name = fix.session.createSender(fix.queue).getName();
    Sender sender = fix.session.getSender(name);
    BOOST_CHECK_EQUAL(name, sender.getName());
    Message out(Uuid(true).str());
    sender.send(out);
    Message in;
    BOOST_CHECK(fix.session.createReceiver(fix.queue).fetch(in));
    BOOST_CHECK_EQUAL(out.getContent(), in.getContent());
    BOOST_CHECK_THROW(fix.session.getSender("UnknownSender"), qpid::messaging::KeyError);
}

QPID_AUTO_TEST_CASE(testGetReceiver)
{
    QueueFixture fix;
    std::string name = fix.session.createReceiver(fix.queue).getName();
    Receiver receiver = fix.session.getReceiver(name);
    BOOST_CHECK_EQUAL(name, receiver.getName());
    Message out(Uuid(true).str());
    fix.session.createSender(fix.queue).send(out);
    Message in;
    BOOST_CHECK(receiver.fetch(in));
    BOOST_CHECK_EQUAL(out.getContent(), in.getContent());
    BOOST_CHECK_THROW(fix.session.getReceiver("UnknownReceiver"), qpid::messaging::KeyError);
}

QPID_AUTO_TEST_CASE(testGetSessionFromConnection)
{
    QueueFixture fix;
    fix.connection.createSession("my-session");
    Session session = fix.connection.getSession("my-session");
    Message out(Uuid(true).str());
    session.createSender(fix.queue).send(out);
    Message in;
    BOOST_CHECK(session.createReceiver(fix.queue).fetch(in));
    BOOST_CHECK_EQUAL(out.getContent(), in.getContent());
    BOOST_CHECK_THROW(fix.connection.getSession("UnknownSession"), qpid::messaging::KeyError);
}

QPID_AUTO_TEST_CASE(testGetConnectionFromSession)
{
    QueueFixture fix;
    Message out(Uuid(true).str());
    Sender sender = fix.session.createSender(fix.queue);
    sender.send(out);
    Message in;
    sender.getSession().getConnection().createSession("incoming");
    BOOST_CHECK(fix.connection.getSession("incoming").createReceiver(fix.queue).fetch(in));
    BOOST_CHECK_EQUAL(out.getContent(), in.getContent());
}

QPID_AUTO_TEST_CASE(testTx)
{
    QueueFixture fix;
    Session ssn1 = fix.connection.createTransactionalSession();
    Session ssn2 = fix.connection.createTransactionalSession();
    Sender sender1 = ssn1.createSender(fix.queue);
    Sender sender2 = ssn2.createSender(fix.queue);
    Receiver receiver1 = ssn1.createReceiver(fix.queue);
    Receiver receiver2 = ssn2.createReceiver(fix.queue);
    Message in;

    send(sender1, 5, 1, "A");
    send(sender2, 5, 1, "B");
    ssn2.commit();
    receive(receiver1, 5, 1, "B");//(only those from sender2 should be received)
    BOOST_CHECK(!receiver1.fetch(in, Duration::IMMEDIATE));//check there are no more messages
    ssn1.rollback();
    receive(receiver2, 5, 1, "B");
    BOOST_CHECK(!receiver2.fetch(in, Duration::IMMEDIATE));//check there are no more messages
    ssn2.rollback();
    receive(receiver1, 5, 1, "B");
    BOOST_CHECK(!receiver1.fetch(in, Duration::IMMEDIATE));//check there are no more messages
    ssn1.commit();
    //check neither receiver gets any more messages:
    BOOST_CHECK(!receiver1.fetch(in, Duration::IMMEDIATE));
    BOOST_CHECK(!receiver2.fetch(in, Duration::IMMEDIATE));
}

QPID_AUTO_TEST_CASE(testRelease)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out("test-message");
    sender.send(out, true);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message m1 = receiver.fetch(Duration::IMMEDIATE);
    fix.session.release(m1);
    Message m2 = receiver.fetch(Duration::SECOND * 1);
    BOOST_CHECK_EQUAL(m1.getContent(), out.getContent());
    BOOST_CHECK_EQUAL(m1.getContent(), m2.getContent());
    BOOST_CHECK(m2.getRedelivered());
    fix.session.acknowledge(true);
}

QPID_AUTO_TEST_CASE(testOptionVerification)
{
    MessagingFixture fix;
    fix.session.createReceiver("my-queue; {create: always, assert: always, delete: always, node: {type: queue, durable: false, x-declare: {arguments: {a: b}}, x-bindings: [{exchange: amq.fanout}]}, link: {name: abc, durable: false, reliability: exactly-once, x-subscribe: {arguments:{a:b}}, x-bindings:[{exchange: amq.fanout}]}, mode: browse}");
    BOOST_CHECK_THROW(fix.session.createReceiver("my-queue; {invalid-option:blah}"), qpid::messaging::AddressError);
}

QPID_AUTO_TEST_CASE(testReceiveSpecialProperties)
{
    QueueFixture fix;

    qpid::client::Message out;
    out.getDeliveryProperties().setRoutingKey(fix.queue);
    out.getMessageProperties().setAppId("my-app-id");
    out.getMessageProperties().setMessageId(qpid::framing::Uuid(true));
    out.getMessageProperties().setContentEncoding("my-content-encoding");
    fix.admin.send(out);

    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(Duration::SECOND * 5);
    BOOST_CHECK_EQUAL(in.getProperties()["x-amqp-0-10.routing-key"].asString(), out.getDeliveryProperties().getRoutingKey());
    BOOST_CHECK_EQUAL(in.getProperties()["x-amqp-0-10.app-id"].asString(), out.getMessageProperties().getAppId());
    BOOST_CHECK_EQUAL(in.getProperties()["x-amqp-0-10.content-encoding"].asString(), out.getMessageProperties().getContentEncoding());
    BOOST_CHECK_EQUAL(in.getMessageId(), out.getMessageProperties().getMessageId().str());
    fix.session.acknowledge(true);
}

QPID_AUTO_TEST_CASE(testSendSpecialProperties)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out("test-message");
    std::string appId = "my-app-id";
    std::string contentEncoding = "my-content-encoding";
    out.getProperties()["x-amqp-0-10.app-id"] = appId;
    out.getProperties()["x-amqp-0-10.content-encoding"] = contentEncoding;
    out.setMessageId(qpid::framing::Uuid(true).str());
    sender.send(out, true);

    qpid::client::LocalQueue q;
    qpid::client::SubscriptionManager subs(fix.admin.session);
    qpid::client::Subscription s = subs.subscribe(q, fix.queue);
    qpid::client::Message in = q.get();
    s.cancel();
    fix.admin.session.sync();

    BOOST_CHECK_EQUAL(in.getMessageProperties().getAppId(), appId);
    BOOST_CHECK_EQUAL(in.getMessageProperties().getContentEncoding(), contentEncoding);
    BOOST_CHECK_EQUAL(in.getMessageProperties().getMessageId().str(), out.getMessageId());
}

QPID_AUTO_TEST_CASE(testExclusiveSubscriber)
{
    QueueFixture fix;
    std::string address = (boost::format("%1%; { link: { x-subscribe : { exclusive:true } } }") % fix.queue).str();
    Receiver receiver = fix.session.createReceiver(address);
    ScopedSuppressLogging sl;
    try {
        fix.session.createReceiver(address);
        fix.session.sync();
        BOOST_FAIL("Expected exception.");
    } catch (const MessagingException& /*e*/) {}
}


QPID_AUTO_TEST_CASE(testExclusiveQueueSubscriberAndBrowser)
{
    MessagingFixture fix;

    std::string address =       "exclusive-queue; { create: receiver, node : { x-declare : { auto-delete: true, exclusive: true } } }";
    std::string browseAddress = "exclusive-queue; { mode: browse }";

    Receiver receiver = fix.session.createReceiver(address);
    fix.session.sync();

    Connection c2 = fix.newConnection();
    c2.open();
    Session s2 = c2.createSession();

    BOOST_CHECK_NO_THROW(Receiver browser = s2.createReceiver(browseAddress));
    c2.close();
}


QPID_AUTO_TEST_CASE(testDeleteQueueWithUnackedMessages)
{
    MessagingFixture fix;
    const uint capacity = 5;

    Sender sender = fix.session.createSender("test.ex;{create:always,node:{type:topic}}");
	Receiver receiver2 = fix.session.createReceiver("alternate.ex;{create:always,node:{type:topic}}");
	Receiver receiver1 = fix.session.createReceiver("test.q;{create:always, delete:always,node:{type:queue, x-declare:{alternate-exchange:alternate.ex}},link:{x-bindings:[{exchange:test.ex,queue:test.q,key:#}]}}");

	receiver1.setCapacity(capacity);
	receiver2.setCapacity(capacity*2);

    Message out("test-message");
    for (uint i = 0; i < capacity*2; ++i) {
        sender.send(out);
    }

	receiver1.close();

    // Make sure all pending messages were sent to the alternate
    // exchange when the queue was deleted.
    Message in;
    for (uint i = 0; i < capacity*2; ++i) {
        in = receiver2.fetch(Duration::SECOND * 5);
        BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
    }
}

QPID_AUTO_TEST_CASE(testAuthenticatedUsername)
{
    MessagingFixture fix;
    Connection connection = fix.newConnection();
    connection.setOption("sasl-mechanism", "PLAIN");
    connection.setOption("username", "test-user");
    connection.setOption("password", "ignored");
    connection.open();
    BOOST_CHECK_EQUAL(connection.getAuthenticatedUsername(), std::string("test-user"));
}

QPID_AUTO_TEST_CASE(testExceptionOnClosedConnection)
{
    MessagingFixture fix;
    fix.connection.close();
    BOOST_CHECK_THROW(fix.connection.createSession(), MessagingException);
    Connection connection("blah");
    BOOST_CHECK_THROW(connection.createSession(), MessagingException);
}

QPID_AUTO_TEST_CASE(testAcknowledge)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    const uint count(20);
    for (uint i = 0; i < count; ++i) {
        sender.send(Message((boost::format("Message_%1%") % (i+1)).str()));
    }

    Session other = fix.connection.createSession();
    Receiver receiver = other.createReceiver(fix.queue);
    std::vector<Message> messages;
    for (uint i = 0; i < count; ++i) {
        Message msg = receiver.fetch();
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("Message_%1%") % (i+1)).str());
        messages.push_back(msg);
    }
    const uint batch(10); //acknowledge first 10 messages only
    for (uint i = 0; i < batch; ++i) {
        other.acknowledge(messages[i]);
    }
    messages.clear();
    other.sync();
    other.close();

    other = fix.connection.createSession();
    receiver = other.createReceiver(fix.queue);
    for (uint i = 0; i < (count-batch); ++i) {
        Message msg = receiver.fetch();
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("Message_%1%") % (i+1+batch)).str());
        if (i % 2) other.acknowledge(msg); //acknowledge every other message
    }
    other.sync();
    other.close();

    //check unacknowledged messages are still enqueued
    other = fix.connection.createSession();
    receiver = other.createReceiver(fix.queue);
    for (uint i = 0; i < ((count-batch)/2); ++i) {
        Message msg = receiver.fetch();
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("Message_%1%") % ((i*2)+1+batch)).str());
    }
    other.acknowledge();//acknowledge all messages
    other.sync();
    other.close();

    Message m;
    //check queue is empty
    BOOST_CHECK(!fix.session.createReceiver(fix.queue).fetch(m, Duration::IMMEDIATE));
}

QPID_AUTO_TEST_CASE(testQmfCreateAndDelete)
{
    MessagingFixture fix(BrokerOptions(), true/*enable management*/);
    MethodInvoker control(fix.session);
    control.createQueue("my-queue");
    control.createExchange("my-exchange", "topic");
    control.bind("my-exchange", "my-queue", "subject1");

    Sender sender = fix.session.createSender("my-exchange");
    Receiver receiver = fix.session.createReceiver("my-queue");
    Message out;
    out.setSubject("subject1");
    out.setContent("one");
    sender.send(out);
    Message in;
    BOOST_CHECK(receiver.fetch(in, Duration::SECOND*5));
    BOOST_CHECK_EQUAL(out.getContent(), in.getContent());
    control.unbind("my-exchange", "my-queue", "subject1");
    control.bind("my-exchange", "my-queue", "subject2");

    out.setContent("two");
    sender.send(out);//should be dropped

    out.setSubject("subject2");
    out.setContent("three");
    sender.send(out);//should not be dropped

    BOOST_CHECK(receiver.fetch(in, Duration::SECOND*5));
    BOOST_CHECK_EQUAL(out.getContent(), in.getContent());
    BOOST_CHECK(!receiver.fetch(in, Duration::IMMEDIATE));
    sender.close();
    receiver.close();

    control.deleteExchange("my-exchange");
    messaging::Session other = fix.connection.createSession();
    {
    ScopedSuppressLogging sl;
    BOOST_CHECK_THROW(other.createSender("my-exchange"), qpid::messaging::NotFound);
    }
    control.deleteQueue("my-queue");
    other = fix.connection.createSession();
    {
    ScopedSuppressLogging sl;
    BOOST_CHECK_THROW(other.createReceiver("my-queue"), qpid::messaging::NotFound);
    }
}

QPID_AUTO_TEST_CASE(testRejectAndCredit)
{
    //Ensure credit is restored on completing rejected messages
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Receiver receiver = fix.session.createReceiver(fix.queue);

    const uint count(10);
    receiver.setCapacity(count);
    for (uint i = 0; i < count; i++) {
        sender.send(Message((boost::format("Message_%1%") % (i+1)).str()));
    }

    Message in;
    for (uint i = 0; i < count; ++i) {
        if (receiver.fetch(in, Duration::SECOND)) {
            BOOST_CHECK_EQUAL(in.getContent(), (boost::format("Message_%1%") % (i+1)).str());
            fix.session.reject(in);
        } else {
            BOOST_FAIL((boost::format("Message_%1% not received as expected") % (i+1)).str());
            break;
        }
    }
    //send another batch of messages
    for (uint i = 0; i < count; i++) {
        sender.send(Message((boost::format("Message_%1%") % (i+count)).str()));
    }

    for (uint i = 0; i < count; ++i) {
        if (receiver.fetch(in, Duration::SECOND)) {
            BOOST_CHECK_EQUAL(in.getContent(), (boost::format("Message_%1%") % (i+count)).str());
        } else {
            BOOST_FAIL((boost::format("Message_%1% not received as expected") % (i+count)).str());
            break;
        }
    }
    fix.session.acknowledge();
    receiver.close();
    sender.close();
}

QPID_AUTO_TEST_CASE(testTtlForever)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out("I want to live forever!");
    out.setTtl(Duration::FOREVER);
    sender.send(out, true);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(Duration::IMMEDIATE);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
    BOOST_CHECK(in.getTtl() == Duration::FOREVER);
}

QPID_AUTO_TEST_CASE(testExclusiveTopicSubscriber)
{
    TopicFixture fix;
    std::string address = (boost::format("%1%; { link: { name: 'my-subscription', x-declare: { auto-delete: true, exclusive: true }}}") % fix.topic).str();
    Sender sender = fix.session.createSender(fix.topic);
    Receiver receiver1 = fix.session.createReceiver(address);
    {
        ScopedSuppressLogging sl;
    try {
        fix.session.createReceiver(address);
        fix.session.sync();
        BOOST_FAIL("Expected exception.");
    } catch (const MessagingException& /*e*/) {}
    }
}

QPID_AUTO_TEST_CASE(testNonExclusiveSubscriber)
{
    TopicFixture fix;
    std::string address = (boost::format("%1%; {node:{type:topic}, link:{name:'my-subscription', x-declare:{auto-delete:true, exclusive:false}}}") % fix.topic).str();
    Receiver receiver1 = fix.session.createReceiver(address);
    Receiver receiver2 = fix.session.createReceiver(address);
    Sender sender = fix.session.createSender(fix.topic);
    sender.send(Message("one"), true);
    Message in = receiver1.fetch(Duration::IMMEDIATE);
    BOOST_CHECK_EQUAL(in.getContent(), std::string("one"));
    sender.send(Message("two"), true);
    in = receiver2.fetch(Duration::IMMEDIATE);
    BOOST_CHECK_EQUAL(in.getContent(), std::string("two"));
    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testAcknowledgeUpTo)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    const uint count(20);
    for (uint i = 0; i < count; ++i) {
        sender.send(Message((boost::format("Message_%1%") % (i+1)).str()));
    }

    Session other = fix.connection.createSession();
    Receiver receiver = other.createReceiver(fix.queue);
    std::vector<Message> messages;
    for (uint i = 0; i < count; ++i) {
        Message msg = receiver.fetch();
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("Message_%1%") % (i+1)).str());
        messages.push_back(msg);
    }
    const uint batch = 10;
    other.acknowledgeUpTo(messages[batch-1]);//acknowledge first 10 messages only

    messages.clear();
    other.sync();
    other.close();

    other = fix.connection.createSession();
    receiver = other.createReceiver(fix.queue);
    Message msg;
    for (uint i = 0; i < (count-batch); ++i) {
        msg = receiver.fetch();
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("Message_%1%") % (i+1+batch)).str());
    }
    other.acknowledgeUpTo(msg);
    other.sync();
    other.close();

    Message m;
    //check queue is empty
    BOOST_CHECK(!fix.session.createReceiver(fix.queue).fetch(m, Duration::IMMEDIATE));
}

QPID_AUTO_TEST_CASE(testCreateBindingsOnStandardExchange)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender((boost::format("amq.direct; {create:always, node:{type:topic, x-bindings:[{queue:%1%, key:my-subject}]}}") % fix.queue).str());
    Message out("test-message");
    out.setSubject("my-subject");
    sender.send(out);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(Duration::SECOND * 5);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
    BOOST_CHECK_EQUAL(in.getSubject(), out.getSubject());
}

QPID_AUTO_TEST_CASE(testUnsubscribeOnClose)
{
    MessagingFixture fix;
    Sender sender = fix.session.createSender("my-exchange/my-subject; {create: always, delete:sender, node:{type:topic, x-declare:{alternate-exchange:amq.fanout}}}");
    Receiver receiver = fix.session.createReceiver("my-exchange/my-subject");
    Receiver deadletters = fix.session.createReceiver("amq.fanout");

    sender.send(Message("first"));
    Message in = receiver.fetch(Duration::SECOND);
    BOOST_CHECK_EQUAL(in.getContent(), std::string("first"));
    fix.session.acknowledge();
    receiver.close();
    sender.send(Message("second"));
    in = deadletters.fetch(Duration::SECOND);
    BOOST_CHECK_EQUAL(in.getContent(), std::string("second"));
    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testHeadersExchange)
{
    MessagingFixture fix;
    //use both quoted and unquoted values
    Receiver receiver = fix.session.createReceiver("amq.match; {link:{x-bindings:[{arguments:{x-match:all,qpid.subject:'abc',my-property:abc}}]}}");
    Sender sender = fix.session.createSender("amq.match");
    Message out("test-message");
    out.setSubject("abc");
    Variant& property = out.getProperties()["my-property"];
    property = "abc";
    property.setEncoding("utf8");
    sender.send(out, true);
    Message in;
    if (receiver.fetch(in, Duration::SECOND)) {
        fix.session.acknowledge();
        BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
    } else {
        BOOST_FAIL("Message did not match as expected!");
    }
}

QPID_AUTO_TEST_CASE(testLargeRoutingKey)
{
    MessagingFixture fix;
    std::string address = "amq.direct/" + std::string(300, 'x');//routing/binding key can be at most 225 chars in 0-10
    BOOST_CHECK_THROW(fix.session.createReceiver(address), qpid::messaging::MessagingException);
}

QPID_AUTO_TEST_CASE(testAlternateExchangeInLinkDeclare)
{
    MessagingFixture fix;
    Sender s = fix.session.createSender("amq.direct/key");
    Receiver r1 = fix.session.createReceiver("amq.direct/key;{link:{x-declare:{alternate-exchange:'amq.fanout'}}}");
    Receiver r2 = fix.session.createReceiver("amq.fanout");

    for (uint i = 0; i < 10; ++i) {
        s.send(Message((boost::format("Message_%1%") % (i+1)).str()), true);
    }
    r1.close();//orphans all messages in subscription queue, which should then be routed through alternate exchange
    for (uint i = 0; i < 10; ++i) {
        Message received;
        BOOST_CHECK(r2.fetch(received, Duration::SECOND));
        BOOST_CHECK_EQUAL(received.getContent(), (boost::format("Message_%1%") % (i+1)).str());
    }
}

QPID_AUTO_TEST_CASE(testBrowseOnly)
{
    /* Set up a queue browse-only, and try to receive
       the same messages twice with two different receivers. 
       This works because the browse-only queue does not
       allow message acquisition. */

    QueueFixture fix;
    std::string addr = "q; {create:always, node:{type:queue, durable:false, x-declare:{arguments:{qpid.browse-only:1}}}}";
    Sender sender = fix.session.createSender(addr);
    Message out("test-message");

    int count = 10;
    for ( int i = 0; i < count; ++ i ) {
        sender.send(out);
    }

    Message m;

    Receiver receiver_1 = fix.session.createReceiver(addr);
    for ( int i = 0; i < count; ++ i ) {
      BOOST_CHECK(receiver_1.fetch(m, Duration::SECOND));
    }

    Receiver receiver_2 = fix.session.createReceiver(addr);
    for ( int i = 0; i < count; ++ i ) {
      BOOST_CHECK(receiver_2.fetch(m, Duration::SECOND));
    }

    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testLinkBindingCleanup)
{
    MessagingFixture fix;

    Sender sender = fix.session.createSender("test.ex;{create:always,node:{type:topic}}");

    Connection connection = fix.newConnection();
    connection.open();

    Session session(connection.createSession());
    Receiver receiver1 = session.createReceiver("test.q;{create:always, node:{type:queue, x-bindings:[{exchange:test.ex,queue:test.q,key:#,arguments:{x-scope:session}}]}}");
    Receiver receiver2 = fix.session.createReceiver("test.q;{create:never, delete:always}");
    connection.close();

    sender.send(Message("test-message"), true);

    // The session-scoped binding should be removed when receiver1's network connection is lost
    Message in;
    BOOST_CHECK(!receiver2.fetch(in, Duration::IMMEDIATE));
}

namespace {
struct Fetcher : public qpid::sys::Runnable {
    Receiver receiver;
    Message message;
    bool result;
    qpid::messaging::Duration timeout;
    bool timedOut;

    Fetcher(Receiver r) : receiver(r), result(false), timeout(Duration::SECOND*10), timedOut(false) {}
    void run()
    {
        qpid::sys::AbsTime start(qpid::sys::now());
        try {
            result = receiver.fetch(message, timeout);
        } catch (const MessagingException&) {}
        qpid::sys::Duration timeTaken(start, qpid::sys::now());
        timedOut = (uint64_t) timeTaken >= timeout.getMilliseconds() * qpid::sys::TIME_MSEC;
    }
};
}

QPID_AUTO_TEST_CASE(testConcurrentFetch)
{
    MessagingFixture fix;
    Sender sender = fix.session.createSender("my-test-queue;{create:always, node : { x-declare : { auto-delete: true}}}");
    Receiver receiver = fix.session.createReceiver("my-test-queue");
    Fetcher fetcher(fix.session.createReceiver("amq.fanout"));
    qpid::sys::Thread runner(fetcher);
    Message out("test-message");
    for (int i = 0; i < 10; i++) {//try several times to make sure
        sender.send(out, true);
        //since the message is now on the queue, it should take less than the timeout to actually fetch it
        qpid::sys::AbsTime start = qpid::sys::AbsTime::now();
        Message in;
        BOOST_CHECK(receiver.fetch(in, qpid::messaging::Duration::SECOND*2));
        qpid::sys::Duration time(start, qpid::sys::AbsTime::now());
        BOOST_CHECK(time < qpid::sys::TIME_SEC*2);
        if (time >= qpid::sys::TIME_SEC*2) break;//if we failed, no need to keep testing
    }
    fix.session.createSender("amq.fanout").send(out);
    runner.join();
    BOOST_CHECK(fetcher.result);
}

QPID_AUTO_TEST_CASE(testSimpleRequestResponse)
{
    QueueFixture fix;
    //create receiver on temp queue for responses (using shorthand for temp queue)
    Receiver r1 = fix.session.createReceiver("#");
    //send request
    Sender s1 = fix.session.createSender(fix.queue);
    Message original("test-message");
    original.setSubject("test-subject");
    original.setReplyTo(r1.getAddress());
    s1.send(original);

    //receive request and send response
    Receiver r2 = fix.session.createReceiver(fix.queue);
    Message m = r2.fetch(Duration::SECOND * 5);
    Sender s2 = fix.session.createSender(m.getReplyTo());
    s2.send(m);
    m = r1.fetch(Duration::SECOND * 5);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(m.getContent(), original.getContent());
    BOOST_CHECK_EQUAL(m.getSubject(), original.getSubject());
}

QPID_AUTO_TEST_CASE(testSelfDestructQueue)
{
    MessagingFixture fix;
    Session other = fix.connection.createSession();
    Receiver r1 = other.createReceiver("amq.fanout; {link:{reliability:at-least-once, x-declare:{arguments:{qpid.max_count:10,qpid.policy_type:self-destruct}}}}");
    Receiver r2 = fix.session.createReceiver("amq.fanout");
    //send request
    Sender s = fix.session.createSender("amq.fanout");
    for (uint i = 0; i < 20; ++i) {
        s.send(Message((boost::format("MSG_%1%") % (i+1)).str()));
    }
    try {
        ScopedSuppressLogging sl;
        for (uint i = 0; i < 20; ++i) {
            r1.fetch(Duration::SECOND);
        }
        BOOST_FAIL("Expected exception.");
    } catch (const qpid::messaging::MessagingException&) {
    }

    for (uint i = 0; i < 20; ++i) {
        BOOST_CHECK_EQUAL(r2.fetch(Duration::SECOND).getContent(), (boost::format("MSG_%1%") % (i+1)).str());
    }
}

QPID_AUTO_TEST_CASE(testReroutingRingQueue)
{
    MessagingFixture fix;
    Receiver r1 = fix.session.createReceiver("my-queue; {create:always, node:{x-declare:{alternate-exchange:amq.fanout, auto-delete:True, arguments:{qpid.max_count:10,qpid.policy_type:ring}}}}");
    Receiver r2 = fix.session.createReceiver("amq.fanout");

    Sender s = fix.session.createSender("my-queue");
    for (uint i = 0; i < 20; ++i) {
        s.send(Message((boost::format("MSG_%1%") % (i+1)).str()));
    }
    for (uint i = 10; i < 20; ++i) {
        BOOST_CHECK_EQUAL(r1.fetch(Duration::SECOND).getContent(), (boost::format("MSG_%1%") % (i+1)).str());
    }
    for (uint i = 0; i < 10; ++i) {
        BOOST_CHECK_EQUAL(r2.fetch(Duration::SECOND).getContent(), (boost::format("MSG_%1%") % (i+1)).str());
    }
}

QPID_AUTO_TEST_CASE(testReleaseOnPriorityQueue)
{
    MessagingFixture fix;
    std::string queue("queue; {create:always, node:{x-declare:{auto-delete:True, arguments:{qpid.priorities:10}}}}");
    std::string text("my message");
    Sender sender = fix.session.createSender(queue);
    sender.send(Message(text));
    Receiver receiver = fix.session.createReceiver(queue);
    Message msg;
    for (uint i = 0; i < 10; ++i) {
        if (receiver.fetch(msg, Duration::SECOND)) {
            BOOST_CHECK_EQUAL(msg.getContent(), text);
            fix.session.release(msg);
        } else {
            BOOST_FAIL("Released message not redelivered as expected.");
        }
    }
    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testRollbackWithFullPrefetch)
{
    QueueFixture fix;
    std::string first("first");
    std::string second("second");
    Sender sender = fix.session.createSender(fix.queue);
    for (uint i = 0; i < 10; ++i) {
        sender.send(Message((boost::format("MSG_%1%") % (i+1)).str()));
    }
    Session txsession = fix.connection.createTransactionalSession();
    Receiver receiver = txsession.createReceiver(fix.queue);
    receiver.setCapacity(9);
    Message msg;
    for (uint i = 0; i < 10; ++i) {
        if (receiver.fetch(msg, Duration::SECOND)) {
            BOOST_CHECK_EQUAL(msg.getContent(), std::string("MSG_1"));
            txsession.rollback();
        } else {
            BOOST_FAIL("Released message not redelivered as expected.");
            break;
        }
    }
    txsession.acknowledge();
    txsession.commit();
}

QPID_AUTO_TEST_CASE(testCloseAndConcurrentFetch)
{
    QueueFixture fix;
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Fetcher fetcher(receiver);
    qpid::sys::Thread runner(fetcher);
    qpid::sys::usleep(500);
    receiver.close();
    runner.join();
    BOOST_CHECK(!fetcher.timedOut);
}

QPID_AUTO_TEST_CASE(testCloseAndMultipleConcurrentFetches)
{
    QueueFixture fix;
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Receiver receiver2 = fix.session.createReceiver("amq.fanout");
    Receiver receiver3 = fix.session.createReceiver("amq.fanout");
    Fetcher fetcher(receiver);
    Fetcher fetcher2(receiver2);
    Fetcher fetcher3(receiver3);
    qpid::sys::Thread runner(fetcher);
    qpid::sys::Thread runner2(fetcher2);
    qpid::sys::Thread runner3(fetcher3);
    qpid::sys::usleep(500);
    receiver.close();
    Message message("Test");
    fix.session.createSender("amq.fanout").send(message);
    runner2.join();
    BOOST_CHECK(fetcher2.result);
    BOOST_CHECK_EQUAL(fetcher2.message.getContent(), message.getContent());
    runner3.join();
    BOOST_CHECK(fetcher3.result);
    BOOST_CHECK_EQUAL(fetcher3.message.getContent(), message.getContent());
    runner.join();
    BOOST_CHECK(!fetcher.timedOut);
}

QPID_AUTO_TEST_CASE(testSessionCheckError)
{
    MessagingFixture fix;
    Session session = fix.connection.createSession();
    Sender sender = session.createSender("q; {create:always, node:{x-declare:{auto-delete:True, arguments:{qpid.max_count:1}}}}");
    ScopedSuppressLogging sl;
    for (uint i = 0; i < 2; ++i) {
        sender.send(Message((boost::format("A_%1%") % (i+1)).str()));
    }
    try {
        while (true) session.checkError();
    } catch (const qpid::types::Exception&) {
        //this is ok
    } catch (const qpid::Exception&) {
        BOOST_FAIL("Wrong exception type thrown");
    }
}

QPID_AUTO_TEST_CASE(testImmediateNextReceiver)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out("test message");
    sender.send(out);
    fix.session.createReceiver(fix.queue).setCapacity(1);
    Receiver next;
    qpid::sys::AbsTime start = qpid::sys::now();
    try {
        while (!fix.session.nextReceiver(next, qpid::messaging::Duration::IMMEDIATE)) {
            qpid::sys::Duration running(start, qpid::sys::now());
            if (running > 5*qpid::sys::TIME_SEC) {
                throw qpid::types::Exception("Timed out spinning on nextReceiver(IMMEDIATE)");
            }
            qpid::sys::usleep(1); // for valgrind
        }
        Message in;
        BOOST_CHECK(next.fetch(in, qpid::messaging::Duration::IMMEDIATE));
        BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
        next.close();
    } catch (const std::exception& e) {
        BOOST_FAIL(e.what());
    }
}

QPID_AUTO_TEST_CASE(testImmediateNextReceiverNoMessage)
{
    QueueFixture fix;
    Receiver r = fix.session.createReceiver(fix.queue);
    r.setCapacity(1);
    Receiver next;
    try {
        BOOST_CHECK(!fix.session.nextReceiver(next, qpid::messaging::Duration::IMMEDIATE));
        r.close();
    } catch (const std::exception& e) {
        BOOST_FAIL(e.what());
    }
}

QPID_AUTO_TEST_CASE(testResendEmpty)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out("test-message");
    sender.send(out);
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(Duration::SECOND * 5);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
    //set content on received message to empty string and resend
    in.setContent("");
    sender.send(in);
    in = receiver.fetch(Duration::SECOND * 5);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(in.getContent(), std::string());
}

QPID_AUTO_TEST_CASE(testResendMapAsString)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    Message out;
    qpid::types::Variant::Map content;
    content["foo"] = "bar";
    encode(content, out);
    sender.send(out);

    Receiver receiver = fix.session.createReceiver(fix.queue);
    Message in = receiver.fetch(Duration::SECOND * 5);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(in.getContent(), out.getContent());
    //change content and resend
    std::string newContent("something random");
    in.setContent(newContent);
    in.setContentType(std::string());//it is no longer a map
    sender.send(in);
    in = receiver.fetch(Duration::SECOND * 5);
    fix.session.acknowledge();
    BOOST_CHECK_EQUAL(in.getContent(), newContent);
}

QPID_AUTO_TEST_CASE(testClientExpiration)
{
    QueueFixture fix;
    Receiver receiver = fix.session.createReceiver(fix.queue);
    receiver.setCapacity(5);
    Sender sender = fix.session.createSender(fix.queue);
    for (uint i = 0; i < 5000; ++i) {
        Message msg((boost::format("a_%1%") % (i+1)).str());
	msg.setSubject("a");
	msg.setTtl(Duration(10));
        sender.send(msg);
    }
    for (uint i = 0; i < 50; ++i) {
        Message msg((boost::format("b_%1%") % (i+1)).str());
	msg.setSubject("b");
        sender.send(msg);
    }
    Message received;
    bool done = false;
    uint b_count = 0;
    while (!done && receiver.fetch(received, Duration::IMMEDIATE)) {
        if (received.getSubject() == "b") {
            b_count++;
        }
        done = received.getContent() == "b_50";
        fix.session.acknowledge();
    }
    BOOST_CHECK_EQUAL(b_count, 50u);
}

QPID_AUTO_TEST_CASE(testClientExpirationNoPrefetch)
{
    QueueFixture fix;
    Receiver receiver = fix.session.createReceiver(fix.queue);
    receiver.setCapacity(0);
    Sender sender = fix.session.createSender(fix.queue);
    for (uint i = 0; i < 50000; ++i) {
        Message msg((boost::format("a_%1%") % (i+1)).str());
	msg.setSubject("a");
	msg.setTtl(Duration(15));
        sender.send(msg);
    }
    for (uint i = 0; i < 50; ++i) {
        Message msg((boost::format("b_%1%") % (i+1)).str());
	msg.setSubject("b");
        sender.send(msg);
    }
    Message received;
    bool done = false;
    uint b_count = 0;
    while (!done && receiver.fetch(received, Duration::FOREVER)) {
        if (received.getSubject() == "b") {
            b_count++;
        }
        done = received.getContent() == "b_50";
        fix.session.acknowledge();
    }
    BOOST_CHECK_EQUAL(b_count, 50u);
}

QPID_AUTO_TEST_CASE(testExpiredPrefetchOnClose)
{
    QueueFixture fix;
    Receiver receiver = fix.session.createReceiver(fix.queue);
    Session other = fix.connection.createSession();
    Receiver receiver2 = other.createReceiver("amq.fanout");
    receiver.setCapacity(500);
    Sender sender = fix.session.createSender(fix.queue);
    for (uint i = 0; i < 500; ++i) {
        Message msg((boost::format("a_%1%") % (i+1)).str());
	msg.setSubject("a");
	msg.setTtl(Duration(5));
        sender.send(msg);
    }
    Sender sender2 = other.createSender("amq.fanout");
    sender2.send(Message("done"));
    BOOST_CHECK_EQUAL(receiver2.fetch().getContent(), "done");
    qpid::sys::usleep(qpid::sys::TIME_MSEC*5);//sorry Alan, I can't see any way to avoid a sleep; need to ensure messages in prefetch have expired 
    receiver.close();
}

QPID_AUTO_TEST_CASE(testPriorityRingEviction)
{
    MessagingFixture fix;
    std::string queue("queue; {create:always, node:{x-declare:{auto-delete:True, arguments:{qpid.priorities:10, qpid.max_count:5, qpid.policy_type:ring}}}}");
    Sender sender = fix.session.createSender(queue);
    Receiver receiver = fix.session.createReceiver(queue);
    std::vector<Message> acquired;
    for (uint i = 0; i < 5; ++i) {
        Message msg((boost::format("msg_%1%") % (i+1)).str());
        sender.send(msg);
    }
    //fetch but don't acknowledge messages, leaving them in acquired state
    for (uint i = 0; i < 5; ++i) {
        Message msg;
        BOOST_CHECK(receiver.fetch(msg, Duration::IMMEDIATE));
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("msg_%1%") % (i+1)).str());
        acquired.push_back(msg);
    }
    //send 5 more messages to the queue, which should cause all the
    //acquired messages to be dropped
    for (uint i = 5; i < 10; ++i) {
        Message msg((boost::format("msg_%1%") % (i+1)).str());
        sender.send(msg);
    }
    //now release the acquired messages, which should have been evicted...
    for (std::vector<Message>::iterator i = acquired.begin(); i != acquired.end(); ++i) {
        fix.session.release(*i);
    }
    acquired.clear();
    //and check that the newest five are received
    for (uint i = 5; i < 10; ++i) {
        Message msg;
        BOOST_CHECK(receiver.fetch(msg, Duration::IMMEDIATE));
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("msg_%1%") % (i+1)).str());
        acquired.push_back(msg);
    }
    Message msg;
    BOOST_CHECK(!receiver.fetch(msg, Duration::IMMEDIATE));
}

QPID_AUTO_TEST_CASE(testReleaseResetsCursor)
{
    QueueFixture fix;
    Sender sender = fix.session.createSender(fix.queue);
    send(sender, 10);
    Receiver r1 = fix.session.createReceiver(fix.queue);
    Receiver r2 = fix.session.createReceiver(fix.queue);
    Message m1;
    BOOST_CHECK(r1.fetch(m1, Duration::IMMEDIATE));
    BOOST_CHECK_EQUAL(m1.getContent(), "Message_1");
    for (uint i = 1; i < 10; i++) {
        Message msg;
        BOOST_CHECK(r2.fetch(msg, Duration::IMMEDIATE));
        BOOST_CHECK_EQUAL(msg.getContent(), (boost::format("Message_%1%") % (i+1)).str());
    }
    fix.session.release(m1);
    Message msg;
    BOOST_CHECK(r2.fetch(msg, Duration::IMMEDIATE));
    BOOST_CHECK_EQUAL(msg.getContent(), "Message_1");
    fix.session.acknowledge();
}

QPID_AUTO_TEST_CASE(testReleaseResetsCursorForLVQ)
{
    MessagingFixture fix;
    std::string queue("queue; {create:always, node:{x-declare:{auto-delete:True, arguments:{qpid.last_value_queue_key:qpid.subject}}}}");
    Sender sender = fix.session.createSender(queue);
    sender.send(Message("please release me"));
    Receiver r1 = fix.session.createReceiver(queue);
    Receiver r2 = fix.session.createReceiver(queue);
    Message m1;
    Message m2;
    BOOST_CHECK(r1.fetch(m1, Duration::IMMEDIATE));
    BOOST_CHECK_EQUAL(m1.getContent(), "please release me");
    BOOST_CHECK(!r2.fetch(m2, Duration::IMMEDIATE));
    fix.session.release(m1);
    BOOST_CHECK(r2.fetch(m2, Duration::SECOND*5));
    BOOST_CHECK_EQUAL(m2.getContent(), "please release me");
    fix.session.acknowledge();
}

QPID_AUTO_TEST_SUITE_END()

}} // namespace qpid::tests
