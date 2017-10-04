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
#include "qpid/sys/MemoryMappedFile.h"

namespace qpid {
namespace sys {
class MemoryMappedFilePrivate {};

MemoryMappedFile::MemoryMappedFile() : state(0) {}
MemoryMappedFile::~MemoryMappedFile() {}

void MemoryMappedFile::open(const std::string& /*name*/, const std::string& /*directory*/)
{
}
void MemoryMappedFile::close()
{
}
size_t MemoryMappedFile::getPageSize()
{
    return 0;
}
char* MemoryMappedFile::map(size_t /*offset*/, size_t /*size*/)
{
    return 0;
}
void MemoryMappedFile::unmap(char* /*region*/, size_t /*size*/)
{
}
void MemoryMappedFile::flush(char* /*region*/, size_t /*size*/)
{
}
void MemoryMappedFile::expand(size_t /*offset*/)
{
}
bool MemoryMappedFile::isSupported()
{
    return false;
}

}} // namespace qpid::sys
