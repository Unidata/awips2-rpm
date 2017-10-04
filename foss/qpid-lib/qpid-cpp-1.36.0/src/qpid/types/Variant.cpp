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
#include "qpid/types/Variant.h"
#include "qpid/log/Statement.h"
#include "encodings.h"
#include <boost/format.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <algorithm>
#include <limits>
#include <sstream>

namespace qpid {
namespace types {

// Stolen from C++11
template <bool, class T=void> struct enable_if {};
template <class T> struct enable_if<true, T> { typedef T type; };

struct true_type { static const bool value = true; };
struct false_type { static const bool value = false; };

template <class T> struct is_signed : public false_type {};
template <> struct is_signed<uint8_t> : public false_type {};
template <> struct is_signed<uint16_t> : public false_type {};
template <> struct is_signed<uint32_t> : public false_type {};
template <> struct is_signed<uint64_t> : public false_type {};
template <> struct is_signed<int8_t> : public true_type {};
template <> struct is_signed<int16_t> : public true_type {};
template <> struct is_signed<int32_t> : public true_type {};
template <> struct is_signed<int64_t> : public true_type {};

template <> struct is_signed<float> : public true_type {};
template <> struct is_signed<double> : public true_type {};


namespace {
const std::string EMPTY;
const std::string PREFIX("invalid conversion: ");
}

InvalidConversion::InvalidConversion(const std::string& msg) : Exception(PREFIX + msg) {}
InvalidConversion::~InvalidConversion() throw() {}

class VariantImpl
{
  public:
    VariantImpl();
    void reset();
    void set(bool);
    void set(uint8_t);
    void set(uint16_t);
    void set(uint32_t);
    void set(uint64_t);
    void set(int8_t);
    void set(int16_t);
    void set(int32_t);
    void set(int64_t);
    void set(float);
    void set(double);
    void set(const std::string&, const std::string& encoding=std::string());
    void set(const Variant::Map&);
    void set(const Variant::List&);
    void set(const Uuid&);
    void set(const Variant&);
    ~VariantImpl();

    VariantType getType() const;

    bool asBool() const;
    uint8_t asUint8() const;
    uint16_t asUint16() const;
    uint32_t asUint32() const;
    uint64_t asUint64() const;
    int8_t asInt8() const;
    int16_t asInt16() const;
    int32_t asInt32() const;
    int64_t asInt64() const;
    float asFloat() const;
    double asDouble() const;
    std::string asString() const;
    Uuid asUuid() const;

    const Variant::Map& asMap() const;
    Variant::Map& asMap();
    const Variant::List& asList() const;
    Variant::List& asList();

    const std::string& getString() const;
    std::string& getString();

    void setEncoding(const std::string&);
    const std::string& getEncoding() const;

    bool isEqualTo(VariantImpl&) const;
    bool isEquivalentTo(VariantImpl&) const;

    Variant::List descriptors;         // Optional descriptors for described value.

  private:
    VariantType type;
    union {
        bool b;
        uint8_t ui8;
        uint16_t ui16;
        uint32_t ui32;
        uint64_t ui64;
        int8_t i8;
        int16_t i16;
        int32_t i32;
        int64_t i64;
        float f;
        double d;
        Uuid* uuid;
        Variant::Map* map;
        Variant::List* list;
        std::string* string;
    } value;
    std::string encoding;       // Optional encoding for variable length data.

    template<class T>
    typename enable_if<is_signed<T>::value, T>::type convertFromString() const
    {
        const std::string& s = *value.string;

        try {
            // Extra shenanigans to work around negative zero
            // conversion error in older GCC libs.
            if ( s[0] != '-' ) {
                return boost::lexical_cast<T>(s);
            } else {
                return -boost::lexical_cast<T>(s.substr(1));
            }
        } catch(const boost::bad_lexical_cast&) {
        }
        throw InvalidConversion(QPID_MSG("Cannot convert " << s));
    }

    template<class T>
    typename enable_if<!is_signed<T>::value, T>::type convertFromString() const
    {
        const std::string& s = *value.string;

        try {
            // Extra shenanigans to work around negative zero
            // conversion error in older GCC libs.
            if ( s[0] != '-' ) {
                return boost::lexical_cast<T>(s);
            } else {
                T r = boost::lexical_cast<T>(s.substr(1));
                if (r==0) return 0;
            }
        } catch(const boost::bad_lexical_cast&) {
        }
        throw InvalidConversion(QPID_MSG("Cannot convert " << s));
    }
};

VariantImpl::VariantImpl() : type(VAR_VOID) {}

void VariantImpl::set(bool b) { reset(); type = VAR_BOOL; value.b = b; }
void VariantImpl::set(uint8_t i) { reset(); type = VAR_UINT8; value.ui8 = i; }
void VariantImpl::set(uint16_t i) { reset(); type = VAR_UINT16; value.ui16 = i; }
void VariantImpl::set(uint32_t i) { reset(); type = VAR_UINT32; value.ui32 = i; }
void VariantImpl::set(uint64_t i) { reset(); type = VAR_UINT64; value.ui64 = i; }
void VariantImpl::set(int8_t i) { reset(); type = VAR_INT8; value.i8 = i; }
void VariantImpl::set(int16_t i) { reset(); type = VAR_INT16; value.i16 = i; }
void VariantImpl::set(int32_t i) { reset(); type = VAR_INT32; value.i32 = i; }
void VariantImpl::set(int64_t i) { reset(); type = VAR_INT64; value.i64 = i; }
void VariantImpl::set(float f) { reset(); type = VAR_FLOAT; value.f = f; }
void VariantImpl::set(double d) { reset(); type = VAR_DOUBLE; value.d = d; }
void VariantImpl::set(const std::string& s, const std::string& e) { reset();  type = VAR_STRING; encoding = e; value.string = new std::string(s); }

void VariantImpl::set(const Variant::Map& m) {
    reset();
    type = VAR_MAP;
    value.map = new Variant::Map(m);
}

void VariantImpl::set(const Variant::List& l) { reset(); type = VAR_LIST; value.list = new Variant::List(l); }

void VariantImpl::set(const Uuid& u) { reset(); type = VAR_UUID; value.uuid = new Uuid(u); }

VariantImpl::~VariantImpl() { reset(); }

void VariantImpl::reset() {
    switch (type) {
      case VAR_STRING:
        delete value.string;
        break;
      case VAR_MAP:
        delete value.map;
        break;
      case VAR_LIST:
        delete value.list;
        break;
      case VAR_UUID:
        delete value.uuid;
        break;
      default:
        break;
    }
    type = VAR_VOID;
}

VariantType VariantImpl::getType() const { return type; }

namespace {

bool same_char(char a, char b)
{
    return toupper(a) == toupper(b);
}

bool caseInsensitiveMatch(const std::string& a, const std::string& b)
{
    return a.size() == b.size() && std::equal(a.begin(), a.end(), b.begin(), &same_char);
}

const std::string TRUE_STRING("True");
const std::string FALSE_STRING("False");

bool toBool(const std::string& s)
{
    if (caseInsensitiveMatch(s, TRUE_STRING)) return true;
    if (caseInsensitiveMatch(s, FALSE_STRING)) return false;
    try { return boost::lexical_cast<int>(s); } catch(const boost::bad_lexical_cast&) {}
    throw InvalidConversion(QPID_MSG("Cannot convert " << s << " to bool"));
}

template <class T> std::string toString(const T& t)
{
    std::stringstream out;
    out << t;
    return out.str();
}

template <class T> bool equal(const T& a, const T& b)
{
    return a.size() == b.size() && std::equal(a.begin(), a.end(), b.begin());
}

}

bool VariantImpl::asBool() const
{
    switch(type) {
      case VAR_VOID: return false;
      case VAR_BOOL: return value.b;
      case VAR_UINT8: return value.ui8;
      case VAR_UINT16: return value.ui16;
      case VAR_UINT32: return value.ui32;
      case VAR_UINT64: return value.ui64;
      case VAR_INT8: return value.i8;
      case VAR_INT16: return value.i16;
      case VAR_INT32: return value.i32;
      case VAR_INT64: return value.i64;
      case VAR_STRING: return toBool(*value.string);
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_BOOL)));
    }
}
uint8_t VariantImpl::asUint8() const
{
    switch(type) {
      case VAR_UINT8: return value.ui8;
      case VAR_UINT16:
          if (value.ui16 <= 0x00ff)
              return uint8_t(value.ui16);
          break;
      case VAR_UINT32:
          if (value.ui32 <= 0x000000ff)
              return uint8_t(value.ui32);
          break;
      case VAR_UINT64:
          if (value.ui64 <= 0x00000000000000ff)
              return uint8_t(value.ui64);
          break;
      case VAR_INT8:
          if (value.i8 >= 0)
              return uint8_t(value.i8);
          break;
      case VAR_INT16:
          if (value.i16 >= 0 && value.i16 <= 0x00ff)
              return uint8_t(value.i16);
          break;
      case VAR_INT32:
          if (value.i32 >= 0 && value.i32 <= 0x000000ff)
              return uint8_t(value.i32);
          break;
      case VAR_INT64:
          if (value.i64 >= 0 && value.i64 <= 0x00000000000000ff)
              return uint8_t(value.i64);
          break;
      case VAR_STRING: return convertFromString<uint8_t>();
      default: break;
    }
    throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_UINT8)));
}
uint16_t VariantImpl::asUint16() const
{
    switch(type) {
      case VAR_UINT8: return value.ui8;
      case VAR_UINT16: return value.ui16;
      case VAR_UINT32:
          if (value.ui32 <= 0x0000ffff)
              return uint16_t(value.ui32);
          break;
      case VAR_UINT64:
          if (value.ui64 <= 0x000000000000ffff)
              return uint16_t(value.ui64);
          break;
      case VAR_INT8:
          if (value.i8 >= 0)
              return uint16_t(value.i8);
          break;
      case VAR_INT16:
          if (value.i16 >= 0)
              return uint16_t(value.i16);
          break;
      case VAR_INT32:
          if (value.i32 >= 0 && value.i32 <= 0x0000ffff)
              return uint16_t(value.i32);
          break;
      case VAR_INT64:
          if (value.i64 >= 0 && value.i64 <= 0x000000000000ffff)
              return uint16_t(value.i64);
          break;
      case VAR_STRING: return convertFromString<uint16_t>();
      default: break;
    }
    throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_UINT16)));
}
uint32_t VariantImpl::asUint32() const
{
    switch(type) {
      case VAR_UINT8: return value.ui8;
      case VAR_UINT16: return value.ui16;
      case VAR_UINT32: return value.ui32;
      case VAR_UINT64:
          if (value.ui64 <= 0x00000000ffffffff)
              return uint32_t(value.ui64);
          break;
      case VAR_INT8:
          if (value.i8 >= 0)
              return uint32_t(value.i8);
          break;
      case VAR_INT16:
          if (value.i16 >= 0)
              return uint32_t(value.i16);
          break;
      case VAR_INT32:
          if (value.i32 >= 0)
              return uint32_t(value.i32);
          break;
      case VAR_INT64:
          if (value.i64 >= 0 && value.i64 <= 0x00000000ffffffff)
              return uint32_t(value.i64);
          break;
      case VAR_STRING: return convertFromString<uint32_t>();
      default: break;
    }
    throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_UINT32)));
}
uint64_t VariantImpl::asUint64() const
{
    switch(type) {
      case VAR_UINT8: return value.ui8;
      case VAR_UINT16: return value.ui16;
      case VAR_UINT32: return value.ui32;
      case VAR_UINT64: return value.ui64;
      case VAR_INT8:
          if (value.i8 >= 0)
              return uint64_t(value.i8);
          break;
      case VAR_INT16:
          if (value.i16 >= 0)
              return uint64_t(value.i16);
          break;
      case VAR_INT32:
          if (value.i32 >= 0)
              return uint64_t(value.i32);
          break;
      case VAR_INT64:
          if (value.i64 >= 0)
              return uint64_t(value.i64);
          break;
      case VAR_STRING: return convertFromString<uint64_t>();
      default: break;
    }
    throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_UINT64)));
}

int8_t VariantImpl::asInt8() const
{
    switch(type) {
      case VAR_INT8: return value.i8;
      case VAR_INT16:
          if ((value.i16 >= std::numeric_limits<int8_t>::min()) && (value.i16 <= std::numeric_limits<int8_t>::max()))
              return int8_t(value.i16);
          break;
      case VAR_INT32:
          if ((value.i32 >= std::numeric_limits<int8_t>::min()) && (value.i32 <= std::numeric_limits<int8_t>::max()))
              return int8_t(value.i32);
          break;
      case VAR_INT64:
          if ((value.i64 >= std::numeric_limits<int8_t>::min()) && (value.i64 <= std::numeric_limits<int8_t>::max()))
              return int8_t(value.i64);
          break;
      case VAR_UINT8:
          if (value.ui8 <= std::numeric_limits<int8_t>::max())
              return int8_t(value.ui8);
          break;
      case VAR_UINT16:
          if (value.ui16 <= std::numeric_limits<int8_t>::max())
              return int8_t(value.ui16);
          break;
      case VAR_UINT32:
          if (value.ui32 <= (uint32_t) std::numeric_limits<int8_t>::max())
              return int8_t(value.ui32);
          break;
      case VAR_UINT64:
          if (value.ui64 <= (uint64_t) std::numeric_limits<int8_t>::max())
              return int8_t(value.ui64);
          break;
      case VAR_STRING: return convertFromString<int8_t>();
      default: break;
    }
    throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_INT8)));
}
int16_t VariantImpl::asInt16() const
{
    switch(type) {
      case VAR_INT8: return value.i8;
      case VAR_INT16: return value.i16;
      case VAR_INT32:
          if ((value.i32 >= std::numeric_limits<int16_t>::min()) && (value.i32 <= std::numeric_limits<int16_t>::max()))
              return int16_t(value.i32);
          break;
      case VAR_INT64:
          if ((value.i64 >= std::numeric_limits<int16_t>::min()) && (value.i64 <= std::numeric_limits<int16_t>::max()))
              return int16_t(value.i64);
          break;
      case VAR_UINT8:  return int16_t(value.ui8);
      case VAR_UINT16:
          if (value.ui16 <= std::numeric_limits<int16_t>::max())
              return int16_t(value.ui16);
          break;
      case VAR_UINT32:
          if (value.ui32 <= (uint32_t) std::numeric_limits<int16_t>::max())
              return int16_t(value.ui32);
          break;
      case VAR_UINT64:
          if (value.ui64 <= (uint64_t) std::numeric_limits<int16_t>::max())
              return int16_t(value.ui64);
          break;
      case VAR_STRING: return convertFromString<int16_t>();
      default: break;
    }
    throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_INT16)));
}
int32_t VariantImpl::asInt32() const
{
    switch(type) {
      case VAR_INT8: return value.i8;
      case VAR_INT16: return value.i16;
      case VAR_INT32: return value.i32;
      case VAR_INT64:
          if ((value.i64 >= std::numeric_limits<int32_t>::min()) && (value.i64 <= std::numeric_limits<int32_t>::max()))
              return int32_t(value.i64);
          break;
      case VAR_UINT8:  return int32_t(value.ui8);
      case VAR_UINT16: return int32_t(value.ui16);
      case VAR_UINT32:
        if (value.ui32 <= (uint32_t) std::numeric_limits<int32_t>::max())
              return int32_t(value.ui32);
          break;
      case VAR_UINT64:
        if (value.ui64 <= (uint64_t) std::numeric_limits<int32_t>::max())
              return int32_t(value.ui64);
          break;
      case VAR_STRING: return convertFromString<int32_t>();
      default: break;
    }
    throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_INT32)));
}
int64_t VariantImpl::asInt64() const
{
    switch(type) {
      case VAR_INT8: return value.i8;
      case VAR_INT16: return value.i16;
      case VAR_INT32: return value.i32;
      case VAR_INT64: return value.i64;
      case VAR_UINT8: return int64_t(value.ui8);
      case VAR_UINT16: return int64_t(value.ui16);
      case VAR_UINT32: return int64_t(value.ui32);
      case VAR_UINT64:
        if (value.ui64 <= (uint64_t) std::numeric_limits<int64_t>::max())
              return int64_t(value.ui64);
          break;
      case VAR_STRING: return convertFromString<int64_t>();
      default: break;
    }
    throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_INT64)));
}
float VariantImpl::asFloat() const
{
    switch(type) {
      case VAR_FLOAT: return value.f;
      case VAR_STRING: return convertFromString<float>();
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_FLOAT)));
    }
}
double VariantImpl::asDouble() const
{
    switch(type) {
      case VAR_FLOAT: return value.f;
      case VAR_DOUBLE: return value.d;
      case VAR_STRING: return convertFromString<double>();
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_DOUBLE)));
    }
}
std::string VariantImpl::asString() const
{
    switch(type) {
      case VAR_VOID: return EMPTY;
      case VAR_BOOL: return value.b ? TRUE_STRING : FALSE_STRING;
      case VAR_UINT8: return boost::lexical_cast<std::string>((int) value.ui8);
      case VAR_UINT16: return boost::lexical_cast<std::string>(value.ui16);
      case VAR_UINT32: return boost::lexical_cast<std::string>(value.ui32);
      case VAR_UINT64: return boost::lexical_cast<std::string>(value.ui64);
      case VAR_INT8: return boost::lexical_cast<std::string>((int) value.i8);
      case VAR_INT16: return boost::lexical_cast<std::string>(value.i16);
      case VAR_INT32: return boost::lexical_cast<std::string>(value.i32);
      case VAR_INT64: return boost::lexical_cast<std::string>(value.i64);
      case VAR_DOUBLE: return boost::lexical_cast<std::string>(value.d);
      case VAR_FLOAT: return boost::lexical_cast<std::string>(value.f);
      case VAR_STRING: return *value.string;
      case VAR_UUID: return value.uuid->str();
      case VAR_LIST: return toString(asList());
      case VAR_MAP: return toString(asMap());
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_STRING)));
    }
}
Uuid VariantImpl::asUuid() const
{
    switch(type) {
      case VAR_UUID: return *value.uuid;
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_UUID)));
    }
}

bool VariantImpl::isEqualTo(VariantImpl& other) const
{
    if (type == other.type) {
        switch(type) {
          case VAR_VOID: return true;
          case VAR_BOOL: return value.b == other.value.b;
          case VAR_UINT8: return value.ui8 == other.value.ui8;
          case VAR_UINT16: return value.ui16 == other.value.ui16;
          case VAR_UINT32: return value.ui32 == other.value.ui32;
          case VAR_UINT64: return value.ui64 == other.value.ui64;
          case VAR_INT8: return value.i8 == other.value.i8;
          case VAR_INT16: return value.i16 == other.value.i16;
          case VAR_INT32: return value.i32 == other.value.i32;
          case VAR_INT64: return value.i64 == other.value.i64;
          case VAR_DOUBLE: return value.d == other.value.d;
          case VAR_FLOAT: return value.f == other.value.f;
          case VAR_STRING: return *value.string == *other.value.string;
          case VAR_UUID: return *value.uuid == *other.value.uuid;
          case VAR_LIST: return equal(asList(), other.asList());
          case VAR_MAP: return equal(asMap(), other.asMap());
        }
    }
    return false;
}

const Variant::Map& VariantImpl::asMap() const
{
    switch(type) {
      case VAR_MAP: return *value.map;
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_MAP)));
    }
}

Variant::Map& VariantImpl::asMap()
{
    switch(type) {
      case VAR_MAP: return *value.map;
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_MAP)));
    }
}

const Variant::List& VariantImpl::asList() const
{
    switch(type) {
      case VAR_LIST: return *value.list;
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_LIST)));
    }
}

Variant::List& VariantImpl::asList()
{
    switch(type) {
      case VAR_LIST: return *value.list;
      default: throw InvalidConversion(QPID_MSG("Cannot convert from " << getTypeName(type) << " to " << getTypeName(VAR_LIST)));
    }
}

std::string& VariantImpl::getString()
{
    switch(type) {
      case VAR_STRING: return *value.string;
      default: throw InvalidConversion(QPID_MSG("Variant is not a string; use asString() if conversion is required."));
    }
}

const std::string& VariantImpl::getString() const
{
    switch(type) {
      case VAR_STRING: return *value.string;
      default: throw InvalidConversion(QPID_MSG("Variant is not a string; use asString() if conversion is required."));
    }
}

void VariantImpl::setEncoding(const std::string& s) { encoding = s; }
const std::string& VariantImpl::getEncoding() const { return encoding; }

std::string getTypeName(VariantType type)
{
    switch (type) {
      case VAR_VOID: return "void";
      case VAR_BOOL: return "bool";
      case VAR_UINT8: return "uint8";
      case VAR_UINT16: return "uint16";
      case VAR_UINT32: return "uint32";
      case VAR_UINT64: return "uint64";
      case VAR_INT8: return "int8";
      case VAR_INT16: return "int16";
      case VAR_INT32: return "int32";
      case VAR_INT64: return "int64";
      case VAR_FLOAT: return "float";
      case VAR_DOUBLE: return "double";
      case VAR_STRING: return "string";
      case VAR_MAP: return "map";
      case VAR_LIST: return "list";
      case VAR_UUID: return "uuid";
    }
    return "<unknown>";//should never happen
}

bool isIntegerType(VariantType type)
{
    switch (type) {
      case VAR_BOOL:
      case VAR_UINT8:
      case VAR_UINT16:
      case VAR_UINT32:
      case VAR_UINT64:
      case VAR_INT8:
      case VAR_INT16:
      case VAR_INT32:
      case VAR_INT64:
        return true;
      default:
        return false;
    }
}

void VariantImpl::set(const Variant& v)
{
    switch (v.getType()) {
      case VAR_BOOL: set(v.asBool()); break;
      case VAR_UINT8: set(v.asUint8()); break;
      case VAR_UINT16: set(v.asUint16()); break;
      case VAR_UINT32: set(v.asUint32()); break;
      case VAR_UINT64: set(v.asUint64()); break;
      case VAR_INT8: set(v.asInt8()); break;
      case VAR_INT16: set(v.asInt16()); break;
      case VAR_INT32: set(v.asInt32()); break;
      case VAR_INT64: set(v.asInt64()); break;
      case VAR_FLOAT: set(v.asFloat()); break;
      case VAR_DOUBLE: set(v.asDouble()); break;
      case VAR_STRING: set(v.asString(), v.getEncoding()); break;
      case VAR_MAP: set(v.asMap()); break;
      case VAR_LIST: set(v.asList()); break;
      case VAR_UUID: set(v.asUuid()); break;
      default: reset();
    }
    encoding = v.getEncoding();
    descriptors = v.getDescriptors();
}

Variant::Variant() : impl(0) {}
Variant::Variant(bool b) : impl(new VariantImpl()) { impl->set(b); }
Variant::Variant(uint8_t i) : impl(new VariantImpl()) { impl->set(i); }
Variant::Variant(uint16_t i) : impl(new VariantImpl()) { impl->set(i); }
Variant::Variant(uint32_t i) : impl(new VariantImpl()) { impl->set(i); }
Variant::Variant(uint64_t i) : impl(new VariantImpl()) { impl->set(i); }
Variant::Variant(int8_t i) : impl(new VariantImpl()) { impl->set(i); }
Variant::Variant(int16_t i) : impl(new VariantImpl()) { impl->set(i); }
Variant::Variant(int32_t i) : impl(new VariantImpl()) { impl->set(i); }
Variant::Variant(int64_t i) : impl(new VariantImpl()) { impl->set(i); }
Variant::Variant(float f) : impl(new VariantImpl()) { impl->set(f); }
Variant::Variant(double d) : impl(new VariantImpl()) { impl->set(d); }
Variant::Variant(const std::string& s) : impl(new VariantImpl()) { impl->set(s); }
Variant::Variant(const std::string& s, const std::string& encoding) : impl(new VariantImpl()) { impl->set(s, encoding); }
Variant::Variant(const char* s) : impl(new VariantImpl()) { impl->set(std::string(s)); }
Variant::Variant(const char* s, const char* encoding) : impl(new VariantImpl()) { impl->set(std::string(s), std::string(encoding)); }
Variant::Variant(const Map& m) : impl(new VariantImpl()) { impl->set(m); }
Variant::Variant(const List& l) : impl(new VariantImpl()) { impl->set(l); }
Variant::Variant(const Variant& v) : impl(new VariantImpl()) { impl->set(v); }
Variant::Variant(const Uuid& u) : impl(new VariantImpl()) { impl->set(u); }

Variant::~Variant() { if (impl) delete impl; }

void Variant::reset()
{
    if (impl) delete impl;
    impl = 0;
}

namespace {
VariantImpl* assure(VariantImpl*& ptr) {
    if (!ptr) ptr = new VariantImpl();
    return ptr;
}
}

Variant& Variant::operator=(bool b)
{
    assure(impl)->set(b);
    return *this;
}

Variant& Variant::operator=(uint8_t i)
{
    assure(impl)->set(i);
    return *this;
}
Variant& Variant::operator=(uint16_t i)
{
    assure(impl)->set(i);
    return *this;
}
Variant& Variant::operator=(uint32_t i)
{
    assure(impl)->set(i);
    return *this;
}
Variant& Variant::operator=(uint64_t i)
{
    assure(impl)->set(i);
    return *this;
}

Variant& Variant::operator=(int8_t i)
{
    assure(impl)->set(i);
    return *this;
}
Variant& Variant::operator=(int16_t i)
{
    assure(impl)->set(i);
    return *this;
}
Variant& Variant::operator=(int32_t i)
{
    assure(impl)->set(i);
    return *this;
}
Variant& Variant::operator=(int64_t i)
{
    assure(impl)->set(i);
    return *this;
}

Variant& Variant::operator=(float f)
{
    assure(impl)->set(f);
    return *this;
}
Variant& Variant::operator=(double d)
{
    assure(impl)->set(d);
    return *this;
}

Variant& Variant::operator=(const std::string& s)
{
    assure(impl)->set(s);
    return *this;
}

Variant& Variant::operator=(const char* s)
{
    assure(impl)->set(std::string(s));
    return *this;
}

Variant& Variant::operator=(const Uuid& u)
{
    assure(impl)->set(u);
    return *this;
}

Variant& Variant::operator=(const Map& m)
{
    assure(impl)->set(m);
    return *this;
}

Variant& Variant::operator=(const List& l)
{
    assure(impl)->set(l);
    return *this;
}

Variant& Variant::operator=(const Variant& v)
{
    assure(impl)->set(v);
    return *this;
}

Variant& Variant::parse(const std::string& s)
{
    operator=(s);
    try {
        return operator=(asInt64());
    } catch (const InvalidConversion&) {}
    try {
        return operator=(asUint64());
    } catch (const InvalidConversion&) {}
    try {
        return operator=(asDouble());
    } catch (const InvalidConversion&) {}
    try {
        return operator=(asBool());
    } catch (const InvalidConversion&) {}
    setEncoding(qpid::types::encodings::UTF8);
    return *this;
}


VariantType Variant::getType() const { return impl ? impl->getType() : VAR_VOID; }
bool Variant::isVoid() const { return getType() == VAR_VOID; }
bool Variant::asBool() const { return impl && impl->asBool(); }
uint8_t Variant::asUint8() const { return impl ? impl->asUint8() : 0; }
uint16_t Variant::asUint16() const { return impl ? impl->asUint16() : 0; }
uint32_t Variant::asUint32() const { return impl ? impl->asUint32() : 0; }
uint64_t Variant::asUint64() const { return impl ? impl->asUint64() : 0; }
int8_t Variant::asInt8() const { return impl ? impl->asInt8() : 0; }
int16_t Variant::asInt16() const { return impl ? impl->asInt16() : 0; }
int32_t Variant::asInt32() const { return impl ? impl->asInt32(): 0; }
int64_t Variant::asInt64() const { return impl ? impl->asInt64() : 0; }
float Variant::asFloat() const { return impl ? impl->asFloat() : 0; }
double Variant::asDouble() const { return impl ? impl->asDouble() : 0; }
std::string Variant::asString() const { return impl ? impl->asString() : EMPTY; }
Uuid Variant::asUuid() const { return impl ? impl->asUuid() : Uuid(); }
const Variant::Map& Variant::asMap() const { if (!impl) throw InvalidConversion("Can't convert VOID to MAP"); return impl->asMap(); }
Variant::Map& Variant::asMap() { if (!impl) throw InvalidConversion("Can't convert VOID to MAP"); return impl->asMap(); }
const Variant::List& Variant::asList() const { if (!impl) throw InvalidConversion("Can't convert VOID to LIST"); return impl->asList(); }
Variant::List& Variant::asList() { if (!impl) throw InvalidConversion("Can't convert VOID to LIST"); return impl->asList(); }
const std::string& Variant::getString() const { if (!impl) throw InvalidConversion("Can't convert VOID to STRING"); return impl->getString(); }
std::string& Variant::getString() { if (!impl) throw InvalidConversion("Can't convert VOID to STRING"); return impl->getString(); }
void Variant::setEncoding(const std::string& s) {
    assure(impl)->setEncoding(s);
}
const std::string& Variant::getEncoding() const { return impl ? impl->getEncoding() : EMPTY; }

Variant::operator bool() const { return asBool(); }
Variant::operator uint8_t() const { return asUint8(); }
Variant::operator uint16_t() const { return asUint16(); }
Variant::operator uint32_t() const { return asUint32(); }
Variant::operator uint64_t() const { return asUint64(); }
Variant::operator int8_t() const { return asInt8(); }
Variant::operator int16_t() const { return asInt16(); }
Variant::operator int32_t() const { return asInt32(); }
Variant::operator int64_t() const { return asInt64(); }
Variant::operator float() const { return asFloat(); }
Variant::operator double() const { return asDouble(); }
Variant::operator std::string() const { return asString(); }
Variant::operator Uuid() const { return asUuid(); }

std::ostream& operator<<(std::ostream& out, const Variant::Map& map)
{
    out << "{";
    for (Variant::Map::const_iterator i = map.begin(); i != map.end(); ++i) {
        if (i != map.begin()) out << ", ";
        out << i->first << ":" << i->second;
    }
    out << "}";
    return out;
}

std::ostream& operator<<(std::ostream& out, const Variant::List& list)
{
    out << "[";
    for (Variant::List::const_iterator i = list.begin(); i != list.end(); ++i) {
        if (i != list.begin()) out << ", ";
        out << *i;
    }
    out << "]";
    return out;
}

std::ostream& operator<<(std::ostream& out, const Variant& value)
{
    // Print the descriptors
    const Variant::List& descriptors = value.getDescriptors();
    for (Variant::List::const_iterator i = descriptors.begin(); i != descriptors.end(); ++i)
        out << "@" << *i << " ";

    // Print the value
    switch (value.getType()) {
      case VAR_MAP:
        out << value.asMap();
        break;
      case VAR_LIST:
        out << value.asList();
        break;
      case VAR_VOID:
        out << "<void>";
        break;
      default:
        out << value.asString();
        break;
    }
    return out;
}

bool operator==(const Variant& a, const Variant& b)
{
    return a.isEqualTo(b);
}

bool operator!=(const Variant& a, const Variant& b) { return !(a == b); }

bool Variant::isEqualTo(const Variant& other) const
{
    if (isVoid() && other.isVoid()) return true;
    if (isVoid() || other.isVoid()) return false;
    return impl && impl->isEqualTo(*other.impl);
}

bool Variant::isDescribed() const {
    return impl && !impl->descriptors.empty();
}

Variant::List& Variant::getDescriptors() {
    return assure(impl)->descriptors;
}

const Variant::List& Variant::getDescriptors() const {
    return assure(impl)->descriptors;
}

Variant Variant::getDescriptor() const {
    if (getDescriptors().size() > 0) return getDescriptors().front();
    else return Variant();
}

void Variant::setDescriptor(const Variant& descriptor) {
    getDescriptors().clear();
    getDescriptors().push_back(descriptor);
}

Variant Variant::described(const Variant& descriptor, const Variant& value) {
    Variant described(value);
    described.setDescriptor(descriptor);
    return described;
}

Variant Variant::described(const Variant& descriptor, const List& value) {
    Variant described(value);
    described.setDescriptor(descriptor);
    return described;
}

}} // namespace qpid::types
