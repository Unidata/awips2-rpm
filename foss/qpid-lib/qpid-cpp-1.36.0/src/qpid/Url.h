#ifndef QPID_URL_H
#define QPID_URL_H

/*
 *
 * Copyright (c) 2006 The Apache Software Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

#include "qpid/Address.h"
#include "qpid/Exception.h"
#include <string>
#include <vector>
#include <new>
#include <ostream>
#include "qpid/CommonImportExport.h"

namespace qpid {

/** An AMQP URL contains a list of addresses */
struct Url : public std::vector<Address> {

    struct Invalid : public Exception { QPID_COMMON_EXTERN Invalid(const std::string& s); };

    /** Convert to string form. */
    QPID_COMMON_EXTERN std::string str() const;

    /** Empty URL. */
    Url() {}

    /** URL containing a single address */
    explicit Url(const Address& addr) { push_back(addr); }

    /** Parse url, throw Invalid if invalid. */
    explicit Url(const std::string& url) { parse(url.c_str()); }
    /** Parse url, throw Invalid if invalid. */
    explicit Url(const std::string& url, const std::string& defaultProtocol) { parse(url.c_str(), defaultProtocol); }

    /** Parse url, throw Invalid if invalid. */
    explicit Url(const char* url) { parse(url); }

    Url& operator=(const char* s) { parse(s); return *this; }
    Url& operator=(const std::string& s) { parse(s); return *this; }

    /** Throw Invalid if the URL does not contain any addresses. */
    QPID_COMMON_EXTERN void throwIfEmpty() const;

    /** Replace contents with parsed url
     *@exception Invalid if the url is invalid.
     */
    QPID_COMMON_EXTERN void parse(const char* url);
    QPID_COMMON_EXTERN void parse(const char* url, const std::string& defaultProtocol);
    QPID_COMMON_INLINE_EXTERN void parse(const std::string& url) { parse(url.c_str()); }

    /** Replace contesnts with parsed URL. Replace with empty URL if invalid. */
    QPID_COMMON_EXTERN void parseNoThrow(const char* url);
    QPID_COMMON_EXTERN void parseNoThrow(const char* url, const std::string& defaultProtocol);

    /** Add a protocol tag to be recognzed in URLs.
     * Only for use by protcol plug-in initializers.
     */
    QPID_COMMON_EXTERN static void addProtocol(const std::string& tag);

    QPID_COMMON_EXTERN void setUser(const std::string&);
    QPID_COMMON_EXTERN void setPass(const std::string&);
    QPID_COMMON_EXTERN std::string getUser() const;
    QPID_COMMON_EXTERN std::string getPass() const;

  private:
    mutable std::string cache;  // cache string form for efficiency.
    std::string user, pass;

  friend class UrlParser;
};

inline bool operator==(const Url& a, const Url& b) { return a.str()==b.str(); }
inline bool operator!=(const Url& a, const Url& b) { return a.str()!=b.str(); }

QPID_COMMON_EXTERN std::ostream& operator<<(std::ostream& os, const Url& url);
QPID_COMMON_EXTERN std::istream& operator>>(std::istream& is, Url& url);

} // namespace qpid

#endif  /*!QPID_URL_H*/
