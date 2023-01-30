/////////////////////////////////////////////////////////////////////////////
// This file is part of the "Java-DAP" project, a Java implementation
// of the OPeNDAP Data Access Protocol.
//
// Copyright (c) 2010, OPeNDAP, Inc.
// Copyright (c) 2002,2003 OPeNDAP, Inc.
//
// Author: James Gallagher <jgallagher@opendap.org>
//
// All rights reserved.
//
// Redistribution and use in source and binary forms,
// with or without modification, are permitted provided
// that the following conditions are met:
//
// - Redistributions of source code must retain the above copyright
//   notice, this list of conditions and the following disclaimer.
//
// - Redistributions in binary form must reproduce the above copyright
//   notice, this list of conditions and the following disclaimer in the
//   documentation and/or other materials provided with the distribution.
//
// - Neither the name of the OPeNDAP nor the names of its contributors may
//   be used to endorse or promote products derived from this software
//   without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
// IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
// TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
// PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
// TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
/////////////////////////////////////////////////////////////////////////////


package opendap.dap;

/**
 * Rewritten 1/15/07 jcaron to use HttpCLient library instead of jdk
 * UrlConnection class. Need more robust redirect and authentication.
 * <p/>
 * This class provides support for common DODS client-side operations such as
 * dereferencing a OPeNDAP URL, communicating network activity status to the
 * user and reading local OPeNDAP objects.
 * <p/>
 * Unlike its C++ counterpart, this class does not store instances of the DAS,
 * DDS, etc. objects. Rather, the methods <code>getDAS</code>, etc. return
 * instances of those objects.
 *
 * @author jehamby
 */

/**
 * Modified for AWIPSII to remove OpenDap's dependency on Apache Commons
 * HttpClient 3.1.
 * 
 * Because the public API depended on HttpClient 3.1 and isn't used by AWIPS, it
 * didn't make sense to rewrite this class using the Apache HttpComponents.
 * 
 * This file remains just to provide a change log.
 * 
 * <pre>
 * 
 * SOFTWARE HISTORY
 * 
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Jul 11, 2016 5091       nabowle     Modified.
 * 
 * </pre>
 */
public class DConnect2 {
    private DConnect2() {
        super();
    }
}
