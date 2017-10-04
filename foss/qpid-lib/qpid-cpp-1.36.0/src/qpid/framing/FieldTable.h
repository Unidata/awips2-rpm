#ifndef _FieldTable_
#define _FieldTable_

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

#include "qpid/framing/amqp_types.h"
#include "qpid/sys/Mutex.h"

#include <boost/shared_ptr.hpp>
#include <boost/shared_array.hpp>

#include <iosfwd>
#include <map>

#include "qpid/CommonImportExport.h"

namespace qpid {
    /**
     * The framing namespace contains classes that are used to create,
     * send and receive the basic packets from which AMQP is built.
     */
namespace framing {

class Array;
class FieldValue;
class Buffer;

/**
 * A set of name-value pairs. (See the AMQP spec for more details on
 * AMQP field tables).
 *
 * \ingroup clientapi
 */
class FieldTable
{
  public:
    typedef boost::shared_ptr<FieldValue> ValuePtr;
    typedef std::map<std::string, ValuePtr> ValueMap;
    typedef ValueMap::iterator iterator;
    typedef ValueMap::const_iterator const_iterator;
    typedef ValueMap::const_reference const_reference;
    typedef ValueMap::reference reference;
    typedef ValueMap::value_type value_type;

    QPID_COMMON_EXTERN FieldTable();
    QPID_COMMON_EXTERN FieldTable(const FieldTable&);
    QPID_COMMON_EXTERN FieldTable& operator=(const FieldTable&);
    // Compiler default destructor fine
    QPID_COMMON_EXTERN uint32_t encodedSize() const;
    QPID_COMMON_EXTERN void encode(Buffer& buffer) const;
    QPID_COMMON_EXTERN void decode(Buffer& buffer);

    QPID_COMMON_EXTERN int count() const;
    QPID_COMMON_INLINE_EXTERN size_t size() const { return values.size(); }
    QPID_COMMON_INLINE_EXTERN bool empty() { return size() == 0; }
    QPID_COMMON_EXTERN void set(const std::string& name, const ValuePtr& value);
    QPID_COMMON_EXTERN ValuePtr get(const std::string& name) const;
    QPID_COMMON_INLINE_EXTERN bool isSet(const std::string& name) const { return get(name).get() != 0; }

    QPID_COMMON_EXTERN void setString(const std::string& name, const std::string& value);
    QPID_COMMON_EXTERN void setInt(const std::string& name, const int value);
    QPID_COMMON_EXTERN void setInt64(const std::string& name, const int64_t value);
    QPID_COMMON_EXTERN void setTimestamp(const std::string& name, const uint64_t value);
    QPID_COMMON_EXTERN void setUInt64(const std::string& name, const uint64_t value);
    QPID_COMMON_EXTERN void setTable(const std::string& name, const FieldTable& value);
    QPID_COMMON_EXTERN void setArray(const std::string& name, const Array& value);
    QPID_COMMON_EXTERN void setFloat(const std::string& name, const float value);
    QPID_COMMON_EXTERN void setDouble(const std::string& name, const double value);
    //void setDecimal(string& name, xxx& value);

    QPID_COMMON_EXTERN int getAsInt(const std::string& name) const;
    QPID_COMMON_EXTERN uint64_t getAsUInt64(const std::string& name) const;
    QPID_COMMON_EXTERN int64_t getAsInt64(const std::string& name) const;
    QPID_COMMON_EXTERN std::string getAsString(const std::string& name) const;

    QPID_COMMON_EXTERN bool getTable(const std::string& name, FieldTable& value) const;
    QPID_COMMON_EXTERN bool getArray(const std::string& name, Array& value) const;
    QPID_COMMON_EXTERN bool getFloat(const std::string& name, float& value) const;
    QPID_COMMON_EXTERN bool getDouble(const std::string& name, double& value) const;
    //QPID_COMMON_EXTERN bool getTimestamp(const std::string& name, uint64_t& value) const;
    //QPID_COMMON_EXTERN bool getDecimal(string& name, xxx& value);
    QPID_COMMON_EXTERN void erase(const std::string& name);


    QPID_COMMON_EXTERN bool operator==(const FieldTable& other) const;

    // Map-like interface.
    QPID_COMMON_EXTERN ValueMap::const_iterator begin() const;
    QPID_COMMON_EXTERN ValueMap::const_iterator end() const;
    QPID_COMMON_EXTERN ValueMap::const_iterator find(const std::string& s) const;

    QPID_COMMON_EXTERN ValueMap::iterator begin();
    QPID_COMMON_EXTERN ValueMap::iterator end();
    QPID_COMMON_EXTERN ValueMap::iterator find(const std::string& s);

    QPID_COMMON_EXTERN std::pair <ValueMap::iterator, bool> insert(const ValueMap::value_type&);
    QPID_COMMON_EXTERN ValueMap::iterator insert(ValueMap::iterator, const ValueMap::value_type&);
    QPID_COMMON_EXTERN void clear();

  private:
    void realDecode() const;
    void flushRawCache();

    mutable qpid::sys::Mutex lock;
    mutable ValueMap values;
    mutable boost::shared_array<uint8_t> cachedBytes;
    mutable uint32_t cachedSize; // if = 0 then non cached size as 0 is not a legal size
    mutable bool newBytes;

    QPID_COMMON_EXTERN friend std::ostream& operator<<(std::ostream& out, const FieldTable& body);
};

//class FieldNotFoundException{};
//class UnknownFieldName : public FieldNotFoundException{};
//class IncorrectFieldType : public FieldNotFoundException{};
}
}


#endif
