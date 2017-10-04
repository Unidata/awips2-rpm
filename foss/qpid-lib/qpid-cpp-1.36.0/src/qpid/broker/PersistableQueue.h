#ifndef _broker_PersistableQueue_h
#define _broker_PersistableQueue_h

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
#include "qpid/broker/Persistable.h"
#include "qpid/management/Manageable.h"

namespace qpid {
namespace broker {


/**
* Empty class to be used by any module that wanted to set an external per queue store into
* persistableQueue
*/

class ExternalQueueStore : public management::Manageable
{
public:
    virtual ~ExternalQueueStore() {};

};


/**
 * The interface queues must expose to the MessageStore in order to be
 * persistable.
 */
class PersistableQueue : public Persistable
{
public:
    virtual const std::string& getName() const = 0;
    virtual ~PersistableQueue() {
        if (externalQueueStore) {
             delete externalQueueStore;
             externalQueueStore = 0;
        }
    };

    virtual void setExternalQueueStore(ExternalQueueStore* inst) = 0;
    virtual void flush() = 0;
    
    inline ExternalQueueStore* getExternalQueueStore() const {return externalQueueStore;};
    
    PersistableQueue():externalQueueStore(NULL){
    };
    
protected:
    ExternalQueueStore* externalQueueStore;
    
};

}}


#endif
