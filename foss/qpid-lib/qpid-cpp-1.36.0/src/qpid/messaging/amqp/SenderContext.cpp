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
#include "SenderContext.h"
#include "Transaction.h"
#include "EncodedMessage.h"
#include "PnData.h"
#include "util.h"
#include "qpid/messaging/AddressImpl.h"
#include "qpid/messaging/exceptions.h"
#include "qpid/Exception.h"
#include "qpid/amqp/descriptors.h"
#include "qpid/amqp/MapHandler.h"
#include "qpid/amqp/MessageEncoder.h"
#include "qpid/messaging/exceptions.h"
#include "qpid/messaging/Message.h"
#include "qpid/messaging/MessageImpl.h"
#include "qpid/log/Statement.h"
#include "config.h"
extern "C" {
#include <proton/engine.h>
}
#include <boost/shared_ptr.hpp>
#include <string.h>

namespace qpid {
namespace messaging {

MessageReleased::MessageReleased(const std::string& msg) : SendError(msg) {}

namespace amqp {

SenderOptions::SenderOptions(bool setToOnSend_, uint32_t maxDeliveryAttempts_, bool raiseRejected_, const qpid::sys::Duration& d)
    : setToOnSend(setToOnSend_), maxDeliveryAttempts(maxDeliveryAttempts_), raiseRejected(raiseRejected_), redeliveryTimeout(d) {}


//TODO: proper conversion to wide string for address
SenderContext::SenderContext(pn_session_t* session, const std::string& n,
                             const qpid::messaging::Address& a,
                             const SenderOptions& o,
                             const CoordinatorPtr& coord)
  : sender(pn_sender(session, n.c_str())),
    name(n),
    address(a),
    helper(address),
    nextId(0), capacity(50), unreliable(helper.isUnreliable()),
    options(o),
    transaction(coord)
{}

SenderContext::~SenderContext()
{
    if (!error && sender) pn_link_free(sender);
}

void SenderContext::close()
{
    error.raise();
    if (sender) pn_link_close(sender);
}

void SenderContext::setCapacity(uint32_t c)
{
    error.raise();
    if (c < deliveries.size()) throw qpid::messaging::SenderError("Desired capacity is less than unsettled message count!");
    capacity = c;
}

uint32_t SenderContext::getCapacity()
{
    return capacity;
}

uint32_t SenderContext::getUnsettled()
{
    error.raise();
    return processUnsettled(true/*always allow retrieval of unsettled count, even if link has failed*/);
}

const std::string& SenderContext::getName() const
{
    return name;
}

const std::string& SenderContext::getTarget() const
{
    return address.getName();
}

bool SenderContext::send(const qpid::messaging::Message& message, SenderContext::Delivery** out)
{
    error.raise();
    resend();//if there are any messages needing to be resent at the front of the queue, send them first
    if (processUnsettled(false) < capacity && pn_link_credit(sender)) {
        types::Variant state;
        if (transaction)
            state = transaction->getSendState();
        if (unreliable) {
            Delivery delivery(nextId++);
            delivery.encode(MessageImplAccess::get(message), address, options.setToOnSend);
            delivery.send(sender, unreliable, state);
            *out = 0;
            return true;
        } else {
            deliveries.push_back(Delivery(nextId++, options.maxDeliveryAttempts, options.redeliveryTimeout));
            try {
                Delivery& delivery = deliveries.back();
                delivery.encode(MessageImplAccess::get(message), address, options.setToOnSend);
                delivery.send(sender, unreliable, state);
                *out = &delivery;
                return true;
            } catch (const std::exception& e) {
                deliveries.pop_back();
                --nextId;
                throw SendError(e.what());
            }
        }
    } else {
        return false;
    }
}

void SenderContext::check()
{
    error.raise();
    if (pn_link_state(sender) & PN_REMOTE_CLOSED && !(pn_link_state(sender) & PN_LOCAL_CLOSED)) {
        std::string text = get_error_string(pn_link_remote_condition(sender), "Link detached by peer");
        pn_link_close(sender);
        throw qpid::messaging::LinkError(text);
    }
}

uint32_t SenderContext::processUnsettled(bool silent)
{
    error.raise();
    if (!silent) {
        check();
    }
    bool resend_required = false;
    //remove messages from front of deque once peer has confirmed receipt
    while (!deliveries.empty() && !(pn_link_state(sender) & PN_REMOTE_CLOSED)) {
        try {
            if (deliveries.front().delivered()) {
                deliveries.front().settle();
                deliveries.pop_front();
            } else {
                break;
            }
        } catch (const MessageReleased& e) {
            //mark it eligible for resending,
            deliveries.front().settleAndReset();
            //and move it to the back
            deliveries.push_back(deliveries.front());
            deliveries.pop_front();
            resend_required = true;
        } catch (const MessageRejected& e) {
            deliveries.front().settle();
            if (options.raiseRejected) {
                QPID_LOG(info, e.what());
                throw;
            } else {
                QPID_LOG(warning, e.what());
                deliveries.pop_front();
            }
        }
    }
    if (resend_required) resend();
    return deliveries.size();
}
namespace {
const std::string X_AMQP("x-amqp-");
const std::string X_AMQP_FIRST_ACQUIRER("x-amqp-first-acquirer");
const std::string X_AMQP_DELIVERY_COUNT("x-amqp-delivery-count");
const std::string X_AMQP_0_10_APP_ID("x-amqp-0-10.app-id");

class HeaderAdapter : public qpid::amqp::MessageEncoder::Header
{
  public:
    HeaderAdapter(const qpid::messaging::MessageImpl& impl) : msg(impl), headers(msg.getHeaders()) {}
    virtual bool isDurable() const
    {
        return msg.isDurable();
    }
    virtual uint8_t getPriority() const
    {
        return msg.getPriority();
    }
    virtual bool hasTtl() const
    {
        return msg.getTtl();
    }
    virtual uint32_t getTtl() const
    {
        return msg.getTtl();
    }
    virtual bool isFirstAcquirer() const
    {
        qpid::types::Variant::Map::const_iterator i = headers.find(X_AMQP_FIRST_ACQUIRER);
        if (i != headers.end()) {
            return i->second;
        } else {
            return false;
        }
    }
    virtual uint32_t getDeliveryCount() const
    {
        qpid::types::Variant::Map::const_iterator i = headers.find(X_AMQP_DELIVERY_COUNT);
        if (i != headers.end()) {
            return i->second;
        } else {
            return msg.isRedelivered() ? 1 : 0;
        }
    }
  private:
    const qpid::messaging::MessageImpl& msg;
    const qpid::types::Variant::Map& headers;
};
const std::string EMPTY;
const std::string FORWARD_SLASH("/");
const std::string X_AMQP_TO("x-amqp-to");
const std::string X_AMQP_CONTENT_ENCODING("x-amqp-content-encoding");
const std::string X_AMQP_CREATION_TIME("x-amqp-creation-time");
const std::string X_AMQP_ABSOLUTE_EXPIRY_TIME("x-amqp-absolute-expiry-time");
const std::string X_AMQP_GROUP_ID("x-amqp-group-id");
const std::string X_AMQP_GROUP_SEQUENCE("x-amqp-group-sequence");
const std::string X_AMQP_REPLY_TO_GROUP_ID("x-amqp-reply-to-group-id");
const std::string X_AMQP_MESSAGE_ANNOTATIONS("x-amqp-message-annotations");
const std::string X_AMQP_DELIVERY_ANNOTATIONS("x-amqp-delivery-annotations");

class PropertiesAdapter : public qpid::amqp::MessageEncoder::Properties
{
  public:
    PropertiesAdapter(const qpid::messaging::MessageImpl& impl, const std::string& s, const std::string& t) : msg(impl), headers(msg.getHeaders()), subject(s), to(t) {}
    bool hasMessageId() const
    {
        return getMessageId().size();
    }
    std::string getMessageId() const
    {
        return msg.getMessageId();
    }

    bool hasUserId() const
    {
        return getUserId().size();
    }

    std::string getUserId() const
    {
        return msg.getUserId();
    }

    bool hasTo() const
    {
        return hasHeader(X_AMQP_TO) || !to.empty();
    }

    std::string getTo() const
    {
        qpid::types::Variant::Map::const_iterator i = headers.find(X_AMQP_TO);
        if (i == headers.end()) return to;
        else return i->second;
    }

    bool hasSubject() const
    {
        return subject.size() || getSubject().size();
    }

    std::string getSubject() const
    {
        return subject.size() ? subject : msg.getSubject();
    }

    bool hasReplyTo() const
    {
        return msg.getReplyTo();
    }

    std::string getReplyTo() const
    {
        Address a = msg.getReplyTo();
        if (a.getSubject().size()) {
            return a.getName() + FORWARD_SLASH + a.getSubject();
        } else {
            return a.getName();
        }
    }

    bool hasCorrelationId() const
    {
        return getCorrelationId().size();
    }

    std::string getCorrelationId() const
    {
        return msg.getCorrelationId();
    }

    bool hasContentType() const
    {
        return getContentType().size();
    }

    std::string getContentType() const
    {
        return msg.getContentType();
    }

    bool hasContentEncoding() const
    {
        return hasHeader(X_AMQP_CONTENT_ENCODING);
    }

    std::string getContentEncoding() const
    {
        return headers.find(X_AMQP_CONTENT_ENCODING)->second;
    }

    bool hasAbsoluteExpiryTime() const
    {
        return hasHeader(X_AMQP_ABSOLUTE_EXPIRY_TIME);
    }

    int64_t getAbsoluteExpiryTime() const
    {
        return headers.find(X_AMQP_ABSOLUTE_EXPIRY_TIME)->second;
    }

    bool hasCreationTime() const
    {
        return hasHeader(X_AMQP_CREATION_TIME);
    }

    int64_t getCreationTime() const
    {
        return headers.find(X_AMQP_CREATION_TIME)->second;
    }

    bool hasGroupId() const
    {
        return hasHeader(X_AMQP_GROUP_ID);
    }

    std::string getGroupId() const
    {
        return headers.find(X_AMQP_GROUP_ID)->second;
    }

    bool hasGroupSequence() const
    {
        return hasHeader(X_AMQP_GROUP_SEQUENCE);
    }

    uint32_t getGroupSequence() const
    {
        return headers.find(X_AMQP_GROUP_SEQUENCE)->second;
    }

    bool hasReplyToGroupId() const
    {
        return hasHeader(X_AMQP_REPLY_TO_GROUP_ID);
    }

    std::string getReplyToGroupId() const
    {
        return headers.find(X_AMQP_REPLY_TO_GROUP_ID)->second;
    }
  private:
    const qpid::messaging::MessageImpl& msg;
    const qpid::types::Variant::Map& headers;
    const std::string subject;
    const std::string to;

    bool hasHeader(const std::string& key) const
    {
        return headers.find(key) != headers.end();
    }
};

bool startsWith(const std::string& input, const std::string& pattern)
{
    if (input.size() < pattern.size()) return false;
    for (std::string::const_iterator b = pattern.begin(), a = input.begin(); b != pattern.end(); ++b, ++a) {
        if (*a != *b) return false;
    }
    return true;
}
class ApplicationPropertiesAdapter : public qpid::amqp::MessageEncoder::ApplicationProperties
{
  public:
    ApplicationPropertiesAdapter(const qpid::types::Variant::Map& h) : headers(h) {}
    void handle(qpid::amqp::MapHandler& h) const
    {
        for (qpid::types::Variant::Map::const_iterator i = headers.begin(); i != headers.end(); ++i) {
            //strip out values with special keys as they are sent in standard fields
            if (!startsWith(i->first, X_AMQP) || i->first == X_AMQP_0_10_APP_ID) {
                qpid::amqp::CharSequence key(convert(i->first));
                switch (i->second.getType()) {
                  case qpid::types::VAR_VOID:
                    h.handleVoid(key);
                    break;
                  case qpid::types::VAR_BOOL:
                    h.handleBool(key, i->second);
                    break;
                  case qpid::types::VAR_UINT8:
                    h.handleUint8(key, i->second);
                    break;
                  case qpid::types::VAR_UINT16:
                    h.handleUint16(key, i->second);
                    break;
                  case qpid::types::VAR_UINT32:
                    h.handleUint32(key, i->second);
                    break;
                  case qpid::types::VAR_UINT64:
                    h.handleUint64(key, i->second);
                    break;
                  case qpid::types::VAR_INT8:
                    h.handleInt8(key, i->second);
                    break;
                  case qpid::types::VAR_INT16:
                    h.handleInt16(key, i->second);
                    break;
                  case qpid::types::VAR_INT32:
                    h.handleInt32(key, i->second);
                    break;
                  case qpid::types::VAR_INT64:
                    h.handleInt64(key, i->second);
                    break;
                  case qpid::types::VAR_FLOAT:
                    h.handleFloat(key, i->second);
                    break;
                  case qpid::types::VAR_DOUBLE:
                    h.handleDouble(key, i->second);
                    break;
                  case qpid::types::VAR_STRING:
                    h.handleString(key, convert(i->second), convert(i->second.getEncoding()));
                    break;
                  case qpid::types::VAR_UUID:
                    QPID_LOG(warning, "Skipping UUID  in application properties; not yet handled correctly.");
                    break;
                  case qpid::types::VAR_MAP:
                  case qpid::types::VAR_LIST:
                    QPID_LOG(warning, "Skipping nested list and map; not allowed in application properties.");
                    break;
                }
            }
        }
    }
  private:
    const qpid::types::Variant::Map& headers;

    static qpid::amqp::CharSequence convert(const std::string& in)
    {
        qpid::amqp::CharSequence out;
        out.data = in.data();
        out.size = in.size();
        return out;
    }
};

bool changedSubject(const qpid::messaging::MessageImpl& msg, const qpid::messaging::Address& address)
{
    return address.getSubject().size() && address.getSubject() != msg.getSubject();
}

}

namespace{
qpid::sys::AbsTime until(const qpid::sys::Duration& d)
{
    return d ? qpid::sys::AbsTime(qpid::sys::now(), d) : qpid::sys::FAR_FUTURE;
}
}

SenderContext::Delivery::Delivery(int32_t i, const uint32_t max_attempts_, const qpid::sys::Duration& max_time) :
    id(i), token(0), settled(false), attempts(0), max_attempts(max_attempts_),
    retry_until(until(max_time)) {}

void SenderContext::Delivery::reset()
{
    token = 0;
}

void SenderContext::Delivery::encode(const qpid::messaging::MessageImpl& msg, const qpid::messaging::Address& address, bool setToField)
{
    try {
        boost::shared_ptr<const EncodedMessage> original = msg.getEncoded();

        if (original && !changedSubject(msg, address)) { //still have the content as received, send at least the bare message unaltered
            //do we need to alter the header? are durable, priority, ttl, first-acquirer, delivery-count different from what was received?
            if (original->hasHeaderChanged(msg)) {
                //since as yet have no annotations, just write the revised header then the rest of the message as received
                encoded.resize(16/*max header size*/ + original->getBareMessage().size);
                qpid::amqp::MessageEncoder encoder(encoded.getData(), encoded.getSize());
                HeaderAdapter header(msg);
                encoder.writeHeader(header);
                ::memcpy(encoded.getData() + encoder.getPosition(), original->getBareMessage().data, original->getBareMessage().size);
            } else {
                //since as yet have no annotations, if the header hasn't
                //changed and we still have the original bare message, can
                //send the entire content as is
                encoded.resize(original->getSize());
                ::memcpy(encoded.getData(), original->getData(), original->getSize());
            }
        } else {
            HeaderAdapter header(msg);
            PropertiesAdapter properties(msg, address.getSubject(), setToField ? address.getName() : EMPTY);
            ApplicationPropertiesAdapter applicationProperties(msg.getHeaders());
            //compute size:
            size_t contentSize = qpid::amqp::MessageEncoder::getEncodedSize(header)
                + qpid::amqp::MessageEncoder::getEncodedSize(properties)
                + qpid::amqp::MessageEncoder::getEncodedSize(applicationProperties);
            if (msg.getContent().isVoid()) {
                contentSize += qpid::amqp::MessageEncoder::getEncodedSizeForContent(msg.getBytes());
            } else {
                contentSize += qpid::amqp::MessageEncoder::getEncodedSizeForValue(msg.getContent()) + 3/*descriptor*/;
            }
            encoded.resize(contentSize);
            QPID_LOG(debug, "Sending message, buffer is " << encoded.getSize() << " bytes")
                qpid::amqp::MessageEncoder encoder(encoded.getData(), encoded.getSize());
            //write header:
            encoder.writeHeader(header);
            //write delivery-annotations, write message-annotations (none yet supported)
            //write properties
            encoder.writeProperties(properties);
            //write application-properties
            encoder.writeApplicationProperties(applicationProperties);
            //write body
            if (!msg.getContent().isVoid()) {
                //write as AmqpValue
                encoder.writeValue(msg.getContent(), &qpid::amqp::message::AMQP_VALUE);
            } else if (msg.getBytes().size()) {
                encoder.writeBinary(msg.getBytes(), &qpid::amqp::message::DATA);//structured content not yet directly supported
            }
            if (encoder.getPosition() < encoded.getSize()) {
                QPID_LOG(debug, "Trimming buffer from " << encoded.getSize() << " to " << encoder.getPosition());
                encoded.trim(encoder.getPosition());
            }
            //write footer (no annotations yet supported)
        }
    } catch (const qpid::Exception& e) {
        throw SendError(e.what());
    }
}

void SenderContext::Delivery::send(pn_link_t* sender, bool unreliable, const types::Variant& state)
{
    ++attempts;
    pn_delivery_tag_t tag;
    tag.size = sizeof(id);
#ifdef NO_PROTON_DELIVERY_TAG_T
    tag.start = reinterpret_cast<const char*>(&id);
#else
    tag.bytes = reinterpret_cast<const char*>(&id);
#endif
    token = pn_delivery(sender, tag);
    if (!state.isVoid()) {      // Add transaction state
        PnData data(pn_disposition_data(pn_delivery_local(token)));
        data.put(state);
        pn_delivery_update(token, qpid::amqp::transaction::TRANSACTIONAL_STATE_CODE);
    }
    pn_link_send(sender, encoded.getData(), encoded.getSize());
    if (unreliable) {
        settle();
    }
    pn_link_advance(sender);
}

bool SenderContext::Delivery::sent() const
{
    return settled || token;
}
bool SenderContext::Delivery::delivered()
{
    if (settled) {
        return true;
    } else if (token && (pn_delivery_remote_state(token) || pn_delivery_settled(token))) {
        if (delivery_refused()) {
            throw MessageRejected(Msg() << "delivery " << id << " refused: " << getStatus());
        } else if (not_delivered()) {
            if (max_attempts && (attempts >= max_attempts)) {
                throw MessageRejected(Msg() << "delivery " << id << " cannot be delivered after " << attempts << " attempts");
            } else if (qpid::sys::now() > retry_until) {
                throw MessageRejected(Msg() << "delivery " << id << " cannot be delivered, timed out after " << attempts << " attempts");
            } else {
                std::string status = getStatus();
                if (max_attempts) {
                    QPID_LOG(info, "delivery " << id << " failed attempt " << attempts << " of " << max_attempts << ": " << status);
                } else {
                    QPID_LOG(info, "delivery " << id << " was not successful: " << status);
                }
                throw MessageReleased(Msg() << "delivery " << id << " was not successful: " << status);
            }
        } else if (!accepted()) {
            QPID_LOG(info, "delivery " << id << " was not accepted by peer");
        }
        return true;
    } else {
        return false;
    }
}
std::string SenderContext::Delivery::getStatus()
{
    if (rejected()) {
        pn_disposition_t* d = token ? pn_delivery_remote(token) : 0;
        if (d) {
            pn_condition_t* c = pn_disposition_condition(d);
            if (c && pn_condition_is_set(c)) {
                return Msg() << pn_condition_get_name(c) << ": " << pn_condition_get_description(c);
            }
        }
        return "rejected";
    } else if (released()) {
        return "released";
    } else if (delivery_refused()) {
        return "undeliverable-here";
    } else if (not_delivered()) {
        return "delivery-failed";
    } else if (modified()) {
        return "modified";
    }
    return "";
}
bool SenderContext::Delivery::accepted()
{
    return token && pn_delivery_remote_state(token) == PN_ACCEPTED;
}
bool SenderContext::Delivery::rejected()
{
    return token && pn_delivery_remote_state(token) == PN_REJECTED;
}
bool SenderContext::Delivery::released()
{
    return token && pn_delivery_remote_state(token) == PN_RELEASED;
}
bool SenderContext::Delivery::modified()
{
    return token && pn_delivery_remote_state(token) == PN_MODIFIED;
}
bool SenderContext::Delivery::delivery_refused()
{
    if (modified()) {
        pn_disposition_t* d = token ? pn_delivery_remote(token) : 0;
        return d && pn_disposition_is_undeliverable(d);
    } else {
        return rejected();
    }
}
bool SenderContext::Delivery::not_delivered()
{
    if (modified()) {
        pn_disposition_t* d = token ? pn_delivery_remote(token) : 0;
        return d && !pn_disposition_is_undeliverable(d);
    } else {
        return released();
    }
}

std::string SenderContext::Delivery::error()
{
    pn_condition_t *condition = token ? pn_disposition_condition(pn_delivery_remote(token)) : 0;
    return (condition && pn_condition_is_set(condition)) ?
        Msg() << get_error_string(condition, std::string(), std::string()) :
        std::string();
}

void SenderContext::Delivery::settle()
{
    if (!settled) {
        pn_delivery_settle(token);
        token = 0; // can no longer use the delivery
        settled = true;
    }
}
void SenderContext::Delivery::settleAndReset()
{
    //settle current delivery:
    settle();
    //but treat message as unsent:
    settled = false;
}
void SenderContext::verify()
{
    error.raise();
    pn_terminus_t* target = pn_link_remote_target(sender);
    if (!helper.isNameNull() && !pn_terminus_get_address(target)) {
        std::string msg("No such target : ");
        msg += getTarget();
        QPID_LOG(debug, msg);
        throw qpid::messaging::NotFound(msg);
    } else if (AddressImpl::isTemporary(address)) {
        address.setName(pn_terminus_get_address(target));
        QPID_LOG(debug, "Dynamic target name set to " << address.getName());
    }

    helper.checkAssertion(target, AddressHelper::FOR_SENDER);
}

void SenderContext::configure()
{
    error.raise();
    if (sender) configure(pn_link_target(sender));
}

void SenderContext::configure(pn_terminus_t* target)
{
    error.raise();
    helper.configure(sender, target, AddressHelper::FOR_SENDER);
    std::string option;
    if (helper.getLinkSource(option)) {
        pn_terminus_set_address(pn_link_source(sender), option.c_str());
    } else {
        pn_terminus_set_address(pn_link_source(sender), pn_terminus_get_address(pn_link_target(sender)));
    }
}

bool SenderContext::settled()
{
    error.raise();
    return processUnsettled(false) == 0;
}

bool SenderContext::closed()
{
    if (sender) {
        return pn_link_state(sender) & PN_LOCAL_CLOSED;
    } else {
        return true;
    }
}

Address SenderContext::getAddress() const
{
    return address;
}


void SenderContext::reset(pn_session_t* session)
{
    sender = session ? pn_sender(session, name.c_str()) : 0;
    if (sender) configure();
    for (Deliveries::iterator i = deliveries.begin(); i != deliveries.end(); ++i)
        i->reset();
}

void SenderContext::resend()
{
    for (Deliveries::iterator i = deliveries.begin(); i != deliveries.end() && !i->sent(); ++i) {
        i->send(sender, false/*only resend reliable transfers*/);
    }
}

void SenderContext::cleanup()
{
    if (!error && sender) {
        error = new LinkError("sender no longer valid");
        pn_link_free(sender);
        sender = 0;

    }
}

}}} // namespace qpid::messaging::amqp
