#ifndef QPID_CLIENT_AMQP0_10_MESSAGESINK_H
#define QPID_CLIENT_AMQP0_10_MESSAGESINK_H

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
#include <string>
#include "qpid/client/AsyncSession.h"

namespace qpid {

namespace messaging {
class Message;
}

namespace client {
namespace amqp0_10 {

class OutgoingMessage;

/**
 *
 */
class MessageSink
{
  public:
    virtual ~MessageSink() {}
    virtual void declare(qpid::client::AsyncSession& session, const std::string& name) = 0;
    virtual void send(qpid::client::AsyncSession& session, const std::string& name, OutgoingMessage& message) = 0;
    virtual void cancel(qpid::client::AsyncSession& session, const std::string& name) = 0;
  private:
};
}}} // namespace qpid::client::amqp0_10

#endif  /*!QPID_CLIENT_AMQP0_10_MESSAGESINK_H*/
