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
#include "qpid/messaging/Receiver.h"
#include "qpid/messaging/Address.h"
#include "qpid/messaging/Message.h"
#include "qpid/messaging/MessageImpl.h"
#include "qpid/messaging/ReceiverImpl.h"
#include "qpid/messaging/Session.h"
#include "qpid/messaging/PrivateImplRef.h"

namespace qpid {
namespace messaging {

// Explicitly instantiate Handle superclass
template class Handle<ReceiverImpl>;

typedef PrivateImplRef<qpid::messaging::Receiver> PI;

Receiver::Receiver(ReceiverImpl* impl) { PI::ctor(*this, impl); }
Receiver::Receiver(const Receiver& s) : Handle<ReceiverImpl>() { PI::copy(*this, s); }
Receiver::~Receiver() { PI::dtor(*this); }
Receiver& Receiver::operator=(const Receiver& s) { return PI::assign(*this, s); }
bool Receiver::get(Message& message, Duration timeout)
{
    MessageImplAccess::get(message).clear();
    return impl->get(message, timeout);
}
Message Receiver::get(Duration timeout) { return impl->get(timeout); }
bool Receiver::fetch(Message& message, Duration timeout)
{
    MessageImplAccess::get(message).clear();
    return impl->fetch(message, timeout);
}
Message Receiver::fetch(Duration timeout) { return impl->fetch(timeout); }
void Receiver::setCapacity(uint32_t c) { impl->setCapacity(c); }
uint32_t Receiver::getCapacity() { return impl->getCapacity(); }
uint32_t Receiver::getAvailable() { return impl->getAvailable(); }
uint32_t Receiver::getUnsettled() { return impl->getUnsettled(); }
void Receiver::close() { impl->close(); }
const std::string& Receiver::getName() const { return impl->getName(); }
Session Receiver::getSession() const { return impl->getSession(); }
bool Receiver::isClosed() const { return impl->isClosed(); }
Address Receiver::getAddress() const { return impl->getAddress(); }
}} // namespace qpid::messaging
