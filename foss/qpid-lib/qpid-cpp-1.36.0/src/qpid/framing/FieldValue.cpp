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
#include "qpid/framing/FieldValue.h"
#include "qpid/framing/Array.h"
#include "qpid/framing/Buffer.h"
#include "qpid/framing/List.h"
#include "qpid/framing/Uuid.h"
#include "qpid/framing/reply_exceptions.h"
#include "qpid/framing/Endian.h"
#include "qpid/Msg.h"

namespace qpid {
namespace framing {

// Some template magic for computing types from sizes.
template<int W> struct IntType{};
template<> struct IntType<1> { typedef int8_t Type; };
template<> struct IntType<2> { typedef int16_t Type; };
template<> struct IntType<4> { typedef int32_t Type; };
template<> struct IntType<8> { typedef int64_t Type; };

template<int W> struct UintType{};
template<> struct UintType<1> { typedef uint8_t Type; };
template<> struct UintType<2> { typedef uint16_t Type; };
template<> struct UintType<4> { typedef uint32_t Type; };
template<> struct UintType<8> { typedef uint64_t Type; };

template<int W> struct FloatType{};
template<> struct FloatType<4> { typedef float Type; };
template<> struct FloatType<8> { typedef double Type; };

// Stolen from C++11
template <bool, class T=void> struct enable_if {};
template <class T> struct enable_if<true, T> { typedef T type; };

// Construct the right subclass of FixedWidthValue for numeric types using width and kind.
// Kind 1=int, 2=unsigned int, 3=float
template<int W>
typename enable_if<(W<3), FixedWidthValue<W>*>::type
numericFixedWidthValue(uint8_t kind) {
    switch (kind) {
      case 1: return new FixedWidthIntValue<typename IntType<W>::Type>();
      case 2: return new FixedWidthIntValue<typename UintType<W>::Type>();
      default: return new FixedWidthValue<W>();
    }
}

template<int W>
typename enable_if<(W>=3), FixedWidthValue<W>*>::type
numericFixedWidthValue(uint8_t kind) {
    switch (kind) {
      case 1: return new FixedWidthIntValue<typename IntType<W>::Type>();
      case 2: return new FixedWidthIntValue<typename UintType<W>::Type>();
      case 3: return new FixedWidthFloatValue<typename FloatType<W>::Type>();
      default: return new FixedWidthValue<W>();
    }
}

uint8_t FieldValue::getType() const
{
    return typeOctet;
}

void FieldValue::setType(uint8_t type)
{
    typeOctet = type;
    if (typeOctet == 0xA8) {
        data.reset(new EncodedValue<FieldTable>());
    } else if (typeOctet == 0xA9) {
        data.reset(new EncodedValue<List>());
    } else if (typeOctet == 0xAA) {
        data.reset(new EncodedValue<Array>());
    } else if (typeOctet == 0x48) {
        data.reset(new UuidData());
    } else {
        uint8_t kind = typeOctet & 0xF;
        uint8_t lenType = typeOctet >> 4;
        switch(lenType){
          case 0:
            data.reset(numericFixedWidthValue<1>(kind));
            break;
          case 1:
            data.reset(numericFixedWidthValue<2>(kind));
            break;
          case 2:
            data.reset(numericFixedWidthValue<4>(kind));
            break;
          case 3:
            data.reset(numericFixedWidthValue<8>(kind));
            break;
            // None of the remaining widths can be numeric types so just use new FixedWidthValue
          case 4:
            data.reset(new FixedWidthValue<16>());
            break;
          case 5:
            data.reset(new FixedWidthValue<32>());
            break;
          case 6:
            data.reset(new FixedWidthValue<64>());
            break;
          case 7:
            data.reset(new FixedWidthValue<128>());
            break;
          case 8:
            data.reset(new VariableWidthValue<1>());
            break;
          case 9:
            data.reset(new VariableWidthValue<2>());
            break;
          case 0xA:
            data.reset(new VariableWidthValue<4>());
            break;
          case 0xC:
            data.reset(new FixedWidthValue<5>());
            break;
          case 0xD:
            data.reset(new FixedWidthValue<9>());
            break;
          case 0xF:
            data.reset(new FixedWidthValue<0>());
            break;
          default:
            throw IllegalArgumentException(QPID_MSG("Unknown field table value type: " << (int)typeOctet));
        }
    }
}

void FieldValue::decode(Buffer& buffer)
{
    setType(buffer.getOctet());
    data->decode(buffer);
}

void FieldValue::encode(Buffer& buffer)
{
    buffer.putOctet(typeOctet);
    data->encode(buffer);
}

bool FieldValue::operator==(const FieldValue& v) const
{
    return
        typeOctet == v.typeOctet &&
        *data == *v.data;
}

Str8Value::Str8Value(const std::string& v) :
    FieldValue(
        TYPE_CODE_STR8,
        new VariableWidthValue<1>(
            reinterpret_cast<const uint8_t*>(v.data()),
            reinterpret_cast<const uint8_t*>(v.data()+v.size())))
{
}

Str16Value::Str16Value(const std::string& v) :
    FieldValue(
        0x95,
        new VariableWidthValue<2>(
            reinterpret_cast<const uint8_t*>(v.data()),
            reinterpret_cast<const uint8_t*>(v.data()+v.size())))
{}

Var16Value::Var16Value(const std::string& v, uint8_t code) :
    FieldValue(
        code,
        new VariableWidthValue<2>(
            reinterpret_cast<const uint8_t*>(v.data()),
            reinterpret_cast<const uint8_t*>(v.data()+v.size())))
{}
Var32Value::Var32Value(const std::string& v, uint8_t code) :
    FieldValue(
        code,
        new VariableWidthValue<4>(
            reinterpret_cast<const uint8_t*>(v.data()),
            reinterpret_cast<const uint8_t*>(v.data()+v.size())))
{}

Struct32Value::Struct32Value(const std::string& v) :
    FieldValue(
        0xAB,
        new VariableWidthValue<4>(
            reinterpret_cast<const uint8_t*>(v.data()),
            reinterpret_cast<const uint8_t*>(v.data()+v.size())))
{}

IntegerValue::IntegerValue(int v) :
    FieldValue(0x21, new FixedWidthIntValue<int32_t>(v))
{}

FloatValue::FloatValue(float v) :
    FieldValue(0x23, new FixedWidthFloatValue<float>(v))
{}

DoubleValue::DoubleValue(double v) :
    FieldValue(0x33, new FixedWidthFloatValue<double>(v))
{}

Integer64Value::Integer64Value(int64_t v) :
    FieldValue(0x31, new FixedWidthIntValue<int64_t>(v))
{}

Unsigned64Value::Unsigned64Value(uint64_t v) :
    FieldValue(0x32, new FixedWidthIntValue<uint64_t>(v))
{}


TimeValue::TimeValue(uint64_t v) :
    FieldValue(0x38, new FixedWidthIntValue<uint64_t>(v))
{
}

FieldTableValue::FieldTableValue(const FieldTable& f) : FieldValue(0xa8, new EncodedValue<FieldTable>(f))
{
}

ListValue::ListValue(const List& l) : FieldValue(0xa9, new EncodedValue<List>(l))
{
}

ArrayValue::ArrayValue(const Array& a) : FieldValue(0xaa, new EncodedValue<Array>(a))
{
}

VoidValue::VoidValue() : FieldValue(0xf0, new FixedWidthValue<0>()) {}

BoolValue::BoolValue(bool b) :
    FieldValue(0x08, new FixedWidthIntValue<bool>(b))
{}

Unsigned8Value::Unsigned8Value(uint8_t v) :
    FieldValue(0x02, new FixedWidthIntValue<uint8_t>(v))
{}
Unsigned16Value::Unsigned16Value(uint16_t v) :
    FieldValue(0x12, new FixedWidthIntValue<uint16_t>(v))
{}
Unsigned32Value::Unsigned32Value(uint32_t v) :
    FieldValue(0x22, new FixedWidthIntValue<uint32_t>(v))
{}

Integer8Value::Integer8Value(int8_t v) :
    FieldValue(0x01, new FixedWidthIntValue<int8_t>(v))
{}
Integer16Value::Integer16Value(int16_t v) :
    FieldValue(0x11, new FixedWidthIntValue<int16_t>(v))
{}

UuidData::UuidData() {}
UuidData::UuidData(const unsigned char* bytes) : FixedWidthValue<16>(bytes) {}
bool UuidData::convertsToString() const { return true; }
std::string UuidData::getString() const { return Uuid(rawOctets()).str(); }
UuidValue::UuidValue(const unsigned char* v) : FieldValue(0x48, new UuidData(v)) {}

void FieldValue::print(std::ostream& out) const {
    data->print(out);
    out << TypeCode(typeOctet) << '(';
    if (data->convertsToString()) out << data->getString();
    else if (data->convertsToInt()) out << data->getInt();
    else data->print(out);
    out << ')';
}

}}
