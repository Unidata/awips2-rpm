#ifndef QPID_AMQP_MAPENCODER_H
#define QPID_AMQP_MAPENCODER_H

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
#include "MapHandler.h"
#include "Encoder.h"

namespace qpid {
namespace amqp {
struct Descriptor;

/**
 * Encode map like data
 */
class MapEncoder : public MapHandler, private Encoder
{
  public:
    MapEncoder(char* data, size_t size);
    void handleVoid(const CharSequence& key);
    void handleBool(const CharSequence& key, bool value);
    void handleUint8(const CharSequence& key, uint8_t value);
    void handleUint16(const CharSequence& key, uint16_t value);
    void handleUint32(const CharSequence& key, uint32_t value);
    void handleUint64(const CharSequence& key, uint64_t value);
    void handleInt8(const CharSequence& key, int8_t value);
    void handleInt16(const CharSequence& key, int16_t value);
    void handleInt32(const CharSequence& key, int32_t value);
    void handleInt64(const CharSequence& key, int64_t value);
    void handleFloat(const CharSequence& key, float value);
    void handleDouble(const CharSequence& key, double value);
    void handleString(const CharSequence& key, const CharSequence& value, const CharSequence& encoding);
    void writeMetaData(size_t size, size_t count, const Descriptor* descriptor=0);
    void writeMap8MetaData(uint8_t size, uint8_t count, const Descriptor* d=0);
    void writeMap32MetaData(uint32_t size, uint32_t count, const Descriptor* d=0);
  private:
};
}} // namespace qpid::amqp

#endif  /*!QPID_AMQP_MAPENCODER_H*/
