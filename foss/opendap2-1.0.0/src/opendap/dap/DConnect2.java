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

import opendap.dap.parser.ParseException;
import org.apache.commons.httpclient.*;
import org.apache.commons.httpclient.methods.GetMethod;
import org.apache.commons.httpclient.util.URIUtil;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.zip.GZIPInputStream;
import java.util.zip.InflaterInputStream;

/**
 * Rewritten 1/15/07 jcaron to use HttpCLient library instead of jdk UrlConnection class.
 * Need more robust redirect and authentication.
 * <p/>
 * This class provides support for common DODS client-side operations such as
 * dereferencing a OPeNDAP URL, communicating network activity status
 * to the user and reading local OPeNDAP objects.
 * <p/>
 * Unlike its C++ counterpart, this class does not store instances of the DAS,
 * DDS, etc. objects. Rather, the methods <code>getDAS</code>, etc. return
 * instances of those objects.
 *
 * @author jehamby
 */
public class DConnect2 {
    static private boolean allowSessions = false;

    static public void setAllowSessions(boolean b) {
        allowSessions = b;
    }

    static private HttpClient _httpClient;

    /**
     * Set the HttpClient object - a single instance is used.
     */
    static public void setHttpClient(HttpClient client) {
        _httpClient = client;
    }

    /**
     * Get the HttpClient object - a single instance is used.
     */
    static public HttpClient getHttpClient() {
        return _httpClient;
    }

    // default HttpClient
    private synchronized void initHttpClient() {
        if (_httpClient != null) return;
        MultiThreadedHttpConnectionManager connectionManager = new MultiThreadedHttpConnectionManager();
        _httpClient = new HttpClient(connectionManager);
    }

    private String urlString; // The current DODS URL without Constraint Expression
    private String filePath = null; // if url is file://

    private String projString;
    /**
     * The projection portion of the current DODS CE (including leading "?").
     */
    private String selString;
    /**
     * The selection portion of the current DODS CE (including leading "&").
     */

    private boolean acceptCompress;
    /**
     * Whether to accept compressed documents.
     */

    // various stuff that comes from the HTTP headers
    private String lastModified = null;
    private String lastExtended = null;
    private String lastModifiedInvalid = null;
    private boolean hasSession = false;

    private ServerVersion ver; // The OPeNDAP server version.

    private boolean debugHeaders = false, debugStream = false;


    public void setServerVersion(int major, int minor) {
        //System.out.println("ServerVersion made with int,int: " + major + "," + minor);

        ver = new ServerVersion(major, minor);
        //System.out.println("ServerVersion.getMajor(): " + ver.getMajor());
        //System.out.println("ServerVersion.getMinor(): " + ver.getMinor());
    }


    /**
     * Creates an instance bound to url which accepts compressed documents.
     *
     * @param urlString      Connect to this URL. If the URL starts with <code>http://</code> then DConnect will attempt to
     * use HTTP to get the data. If the URL does not start with <code>http://</code> the it will treat the url as a
     * filename on the local system. If the url starts with <code>file://</code> then the leading <code>file://</code>
     * is removed and the remaining string is treated as a filename on the local system.
     * @throws FileNotFoundException thrown if <code>urlString</code> is not
     *                               a valid URL, or a filename which exists on the system.
     */
    public DConnect2(String urlString) throws FileNotFoundException {
        this(urlString, true);
    }

    /**
     * Creates an instance bound to the passed. If <code>acceptDeflate</code> is true
     * then HTTP Request headers will indicate to servers that this client can
     * accept compressed documents.
     *
     * @param urlString  Connect to this URL. If the URL starts with <code>http://</code> then DConnect will attempt to
     * use HTTP to get the data. If the URL does not start with <code>http://</code> the it will treat the URL as a
     * filename on the local system. If the URL starts with <code>file://</code> then the leading <code>file://</code>
     * is removed and the remaining string is treated as a filename on the local system.
     * @param acceptCompress true if this client will accept compressed responses
     * @throws FileNotFoundException thrown if <code>url</code> is not
     *                               a valid URL, or a filename which exists on the system.
     */
    public DConnect2(String urlString, boolean acceptCompress) throws FileNotFoundException {



        if(urlString.startsWith("http://")){

            // -------  Process CE
            int ceIndex = urlString.indexOf('?');
            if (ceIndex != -1) {
                urlString = urlString.substring(0, ceIndex);
                String expr = urlString.substring(ceIndex);
                int selIndex = expr.indexOf('&');
                if (selIndex != -1) {
                    this.projString = expr.substring(0, selIndex);
                    this.selString = expr.substring(selIndex);
                } else {
                    this.projString = expr;
                    this.selString = "";
                }
            } else {
                this.urlString = urlString;
                this.projString = this.selString = "";
            }


            // -------  Compression
            this.acceptCompress = acceptCompress;

        }
        else {



            // Check out the URL to see if it is file://
            try {

                String fileProtocol = "file://";

                filePath = urlString;

                if(filePath.startsWith(fileProtocol)){
                    filePath = urlString.substring(fileProtocol.length(),urlString.length());
                }


                // See if the file exists.
                File f = new File(filePath);
                if (!f.exists()) {
                    System.err.println(f.getName() + " does not exist.");
                    throw new FileNotFoundException("Cannot find file "+filePath);
                }
                if (!f.canRead()) {
                    System.err.println(f.getName() + "is not readable.");
                }


                /* Set the server version cause we won't get it from anywhere */
                ver = new ServerVersion(ServerVersion.DAP2_PROTOCOL_VERSION, ServerVersion.XDAP);
            } catch (DAP2Exception ex) {
                throw new FileNotFoundException("Cannot set server version");
            }
        }



    }

    /**
     * Returns the constraint expression supplied with the URL given to the
     * constructor. If no CE was given this returns an empty <code>String</code>.
     * <p/>
     * Note that the CE supplied to one of this object's constructors is
     * "sticky"; it will be used with every data request made with this object.
     * The CE passed to <code>getData</code>, however, is not sticky; it is used
     * only for that specific request. This method returns the sticky CE.
     *
     * @return the constraint expression associated with this connection.
     */
    public final String CE() {
        return projString + selString;
    }

    /**
     * Returns the URL supplied to the constructor. If the URL contained a
     * constraint expression that is not returned.
     *
     * @return the URL of this connection.
     */
    public final String URL() {
        return urlString;
    }

    /**
     * Open a connection to the DODS server.
     *
     * @param urlString the URL to open.
     * @param command   execute this command on the input stream
     * @throws IOException    if an IO exception occurred.
     * @throws DAP2Exception  if the DODS server returned an error.
     * @throws ParseException is cant parse the return
     */
    private void openConnection(String urlString, Command command) throws IOException, DAP2Exception, ParseException {


        initHttpClient();
        GetMethod method = new GetMethod(urlString);
        method.setFollowRedirects(true);

        if (acceptCompress)
            method.setRequestHeader(new Header("Accept-Encoding", "deflate,gzip"));

        // enable sessions
        if (allowSessions)
            method.setRequestHeader(new Header("X-Accept-Session", "true"));

        // Formatter f = new Formatter(System.out);

        InputStream is = null;
        try {
            // Execute the method.

            int statusCode = _httpClient.executeMethod(method);

            // debug
            // if (debugHeaders) ucar.nc2.util.net.HttpClientManager.showHttpRequestInfo(f, method);

            if (statusCode == HttpStatus.SC_NOT_FOUND) {
                throw new DAP2Exception(DAP2Exception.NO_SUCH_FILE, method.getStatusLine().toString());
            }

            if (statusCode == HttpStatus.SC_UNAUTHORIZED) {
                throw new org.apache.commons.httpclient.auth.CredentialsNotAvailableException(method.getStatusLine().toString());
            }

            if (statusCode != HttpStatus.SC_OK) {
                throw new DAP2Exception("Method failed:" + method.getStatusLine());
            }

            // Get the response body.
            is = method.getResponseBodyAsStream();

            // check if its an error
            Header header = method.getResponseHeader("Content-Description");
            if (header != null && (header.getValue().equals("dods-error") || header.getValue().equals("dods_error"))) {
                // create server exception object
                DAP2Exception ds = new DAP2Exception();
                is = dumpStream(is);
                // parse the Error object from stream and throw it
                ds.parse(is);
                throw ds;
            }

            ver = new ServerVersion(method);

            // debug
            //if (debugHeaders) ucar.nc2.util.net.HttpClientManager.showHttpResponseInfo(f, method);

            checkHeaders(method);

            // check for deflator
            Header h = method.getResponseHeader("content-encoding");
            String encoding = (h == null) ? null : h.getValue();
            //if (encoding != null) System.out.println("encoding= " + encoding);

            if (encoding != null && encoding.equals("deflate")) {
                is = new BufferedInputStream(new InflaterInputStream(is), 1000);

            } else if (encoding != null && encoding.equals("gzip")) {
                is = new BufferedInputStream(new GZIPInputStream(is), 1000);
            }

            // is = dumpStream(is);
            command.process(is);

        } catch (org.apache.commons.httpclient.auth.CredentialsNotAvailableException e) {
            throw e; // LOOK why are we catching ??

        } catch (HttpException e) {
            throw new DAP2Exception("Fatal protocol violation: " + e.getMessage());

        } finally {
            // Release the connection.
            if (is != null) is.close();
            method.releaseConnection();
        }
    }


    public void closeSession() {
        try {
            if (allowSessions && hasSession) {
                openConnection(urlString + ".close", new Command() {
                    public void process(InputStream is) throws IOException {
                        byte[] buffer = new byte[4096];  // read the body fully
                        while (is.read(buffer) > 0) {
                            // empty
                        }
                    }
                });
            }
        } catch (Throwable t) {
            // ignore
        }
    }

    private InputStream dumpStream(InputStream is) throws IOException {
        /* String contents = thredds.util.IO.readContents(is);
  System.out.println("debugStream=============\n"+ ucar.unidata.util.StringUtil.filter7bits(contents)+"\n================\n");
  is =  new StringBufferInputStream (contents); */
        return is;
    }

    /**
     * Returns the <code>ServerVersion</code> of the last connection.
     *
     * @return the <code>ServerVersion</code> of the last connection.
     */
    public final ServerVersion getServerVersion() {
        return ver;
    }

    /**
     * @return value of Last-Modified Header from last connection, may be null
     */
    public String getLastModifiedHeader() {
        return lastModified;
    }

    /**
     * @return value of X-Last-Modified-Invalid Header from last connection, may be null
     */
    public String getLastModifiedInvalidHeader() {
        return lastModifiedInvalid;
    }

    /**
     * @return value of Last-Extended Header from last connection, may be null
     */
    public String getLastExtendedHeader() {
        return lastExtended;
    }

    private void checkHeaders(GetMethod method) {
        if (debugHeaders) {
            System.out.println("\nOpenConnection Headers for " + method.getPath());
            System.out.println("Status Line: " + method.getStatusLine());
        }

        Header[] responseHeaders = method.getResponseHeaders();
        for (int i1 = 0; i1 < responseHeaders.length; i1++) {
            Header responseHeader = responseHeaders[i1];
            if (debugHeaders) System.out.print("  " + responseHeader);
            String key = responseHeader.getName();
            String value = responseHeader.getValue();

            if (key.equals("Last-Modified")) {
                lastModified = value;
                if (debugHeaders)
                    System.out.println(" **found lastModified = " + lastModified);

            } else if (key.equals("X-Last-Extended")) {
                lastExtended = value;
                if (debugHeaders)
                    System.out.println(" **found lastExtended = " + lastExtended);

            } else if (key.equals("X-Last-Modified-Invalid")) {
                lastModifiedInvalid = value;
                if (debugHeaders)
                    System.out.println(" **found lastModifiedInvalid = " + lastModifiedInvalid);
            }
        }

        if (debugHeaders)
            System.out.println("OpenConnection Headers for " + method.getPath());

        HttpState state = _httpClient.getState();
        Cookie[] cookies = state.getCookies();

        if (cookies.length > 0) {
            if (debugHeaders) System.out.println("Cookies= ");

            for (int i = 0; i < cookies.length; i++) {
                Cookie cooky = cookies[i];
                if (debugHeaders) System.out.println("  " + cooky);
                if (cooky.getName().equalsIgnoreCase("jsessionid"))
                    hasSession = true;
            }
        }

    }

    private interface Command {
        void process(InputStream is) throws DAP2Exception, ParseException, IOException;
    }

    /**
     * Returns the DAS object from the dataset referenced by this object's URL.
     * The DAS object is referred to by appending `.das' to the end of a DODS
     * URL.
     *
     * @return the DAS associated with the referenced dataset.
     * @throws MalformedURLException if the URL given to the
     *                               constructor has an error
     * @throws IOException           if an error connecting to the remote server
     * @throws ParseException        if the DAS parser returned an error
     * @throws DASException          on an error constructing the DAS
     * @throws DAP2Exception         if an error returned by the remote server
     */
    public DAS getDAS() throws IOException, ParseException, DAP2Exception {
        DASCommand command = new DASCommand();
        if (filePath != null) { // url was file:

            DDS dds = getData("");

            DAS das = dds.getDAS();

            return das;

        } else { // assume url is remote
            String dasUrl = urlString + ".das";
            openConnection(dasUrl, command);
        }
        return command.das;
    }

    private class DASCommand implements Command {
        DAS das = new DAS();

        public void process(InputStream is) throws DASException, ParseException {
            das.parse(is);
        }
    }

    /**
     * Returns the DDS object from the dataset referenced by this object's URL.
     * The DDS object is referred to by appending `.dds' to the end of a OPeNDAP
     * URL.
     *
     * @return the DDS associated with the referenced dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if an error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if an error returned by the remote server
     */
    public DDS getDDS() throws IOException, ParseException, DAP2Exception {
        return getDDS("");
    }

    /**
     * Returns the DDS object from the dataset referenced by this object's URL.
     * The DDS object is referred to by appending `.dds' to the end of a OPeNDAP
     * URL.
     *
     * @param CE The constraint expression to be applied to this request by the
     *           server.  This is combined with any CE given in the constructor.
     * @return the DDS associated with the referenced dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if an error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if an error returned by the remote server
     */
    public DDS getDDS(String CE) throws IOException, ParseException, DAP2Exception {
        DDSCommand command = new DDSCommand();

        if (filePath != null) {
            return getData(CE);
        } else { // must be a remote url
            openConnection(urlString + ".dds" + getCompleteCE(CE), command);
        }

        return command.dds;

    }

    private class DDSCommand implements Command {
        DDS dds = new DDS();

        public void process(InputStream is) throws DDSException, ParseException {
            dds.parse(is);
        }
    }

    /**
     * Use some sense when assembling the CE. Since this DConnect
     * object may have constructed using a CE, any new CE will
     * have to be integrated into it for subsequent requests.
     * Try to do this in a sensible manner!
     *
     * @param CE The new CE from the client.
     * @return The complete CE (the one this object was built
     *         with integrated with the clients)
     */
    private String getCompleteCE(String CE) {
        String localProjString, localSelString;
        int selIndex = CE.indexOf('&');
        if (selIndex != -1) {

            if (CE.indexOf('?') == 0)
                localProjString = CE.substring(1, selIndex);
            else
                localProjString = CE.substring(0, selIndex);

            localSelString = CE.substring(selIndex);
        } else {
            if (CE.indexOf('?') == 0)
                localProjString = CE.substring(1);
            else
                localProjString = CE;
            localSelString = "";
        }

        String ce = projString;

        if (!localProjString.equals("")) {
            if (!ce.equals("") && localProjString.indexOf(',') != 0)
                ce += ",";
            ce += localProjString;
        }

        if (!selString.equals("")) {
            if (selString.indexOf('&') != 0)
                ce += "&";
            ce += selString;
        }

        if (!localSelString.equals("")) {
            if (localSelString.indexOf('&') != 0)
                ce += "&";
            ce += localSelString;
        }

        if (ce.indexOf('?') != 0) {
            ce = "?" + ce;
        }

        String escCE;
        try {
            escCE = URIUtil.encodeQuery(ce);
        } catch (URIException e) {
            throw new IllegalStateException(e.getMessage());
        }

        if (false) {
            System.out.println("projString: '" + projString + "'");
            System.out.println("localProjString: '" + localProjString + "'");
            System.out.println("selString: '" + selString + "'");
            System.out.println("localSelString: '" + localSelString + "'");
            System.out.println("Complete CE: " + ce);
            System.out.println("Escaped CE: " + escCE);
        }
        return escCE;
    }

    /**
     * Returns the DDS object from the dataset referenced by this object's URL.
     * The DDS object is referred to by appending `.ddx' to the end of a OPeNDAP
     * URL. The server should send back a DDX (A DDS in XML format) which
     * will get parsed here (locally) and a new DDS instantiated using
     * the DDSXMLParser.
     *
     * @return the DDS associated with the referenced dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if an error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if an error returned by the remote server
     * @opendap.ddx.experimental
     */
    public DDS getDDX() throws IOException, ParseException, DAP2Exception {
        return (getDDX(""));
    }


    /**
     * Returns the DDS object from the dataset referenced by this object's URL.
     * The DDS object is referred to by appending `.ddx' to the end of a OPeNDAP
     * URL. The server should send back a DDX (A DDS in XML format) which
     * will get parsed here (locally) and a new DDS instantiated using
     * the DDSXMLParser.
     *
     * @param CE The constraint expression to be applied to this request by the
     *           server.  This is combined with any CE given in the constructor.
     * @return the DDS associated with the referenced dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if an error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if an error returned by the remote server
     * @opendap.ddx.experimental
     */
    public DDS getDDX(String CE) throws IOException, ParseException, DAP2Exception {

        if (filePath != null) {
            return getData(CE);

        } else { // must be a remote url
            DDXCommand command = new DDXCommand();
            openConnection(urlString + ".ddx" + getCompleteCE(CE), command);
            return command.dds;
        }
    }

    private class DDXCommand implements Command {
        DDS dds = new DDS();

        public void process(InputStream is) throws DAP2Exception, ParseException {
            dds.parseXML(is, false);
        }
    }

    /**
     * Returns the DataDDS object from the dataset referenced by this object's URL.
     * The DDS object is referred to by appending `.ddx' to the end of a OPeNDAP
     * URL. The server should send back a DDX (A DDS in XML format) which
     * will get parsed here (locally) and a new DDS instantiated using
     * the DDSXMLParser.
     *
     * @return the DataDDS associated with the referenced dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if an error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if an error returned by the remote server
     * @opendap.ddx.experimental
     */
    public DataDDS getDataDDX() throws IOException,
            ParseException, DAP2Exception {

        return getDataDDX("", new DefaultFactory());
    }


    /**
     * Returns the DataDDS object from the dataset referenced by this object's URL.
     * The DDS object is referred to by appending `.ddx' to the end of a OPeNDAP
     * URL. The server should send back a DDX (A DDS in XML format) which
     * will get parsed here (locally) and a new DDS instantiated using
     * the DDSXMLParser.
     *
     * @param CE The constraint expression to use for this request.
     * @return the DataDDS associated with the referenced dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if an error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if an error returned by the remote server
     * @opendap.ddx.experimental
     */
    public DataDDS getDataDDX(String CE) throws MalformedURLException, IOException,
            ParseException, DDSException, DAP2Exception {

        return getDataDDX(CE, new DefaultFactory());
    }

    /**
     * Returns the DataDDS object from the dataset referenced by this object's URL.
     * The DDS object is referred to by appending `.ddx' to the end of a OPeNDAP
     * URL. The server should send back a DDX (A DDS in XML format) which
     * will get parsed here (locally) and a new DDS instantiated using
     * the DDSXMLParser.
     *
     * @param CE  The constraint expression to use for this request.
     * @param btf The <code>BaseTypeFactory</code> to build the member
     *            variables in the DDS with.
     * @return the DataDDS associated with the referenced dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if an error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if an error returned by the remote server
     * @opendap.ddx.experimental
     * @see BaseTypeFactory
     */
    public DataDDS getDataDDX(String CE, BaseTypeFactory btf) throws IOException, ParseException, DAP2Exception {
        if (filePath != null) {
            return getData(CE,null,btf);
        } else { // must be a remote url
            DataDDXCommand command = new DataDDXCommand(btf);
            openConnection(urlString + ".xdods" + getCompleteCE(CE), command);
            return command.dds;
        }

    }

    private class DataDDXCommand implements Command {
        DataDDS dds;

        DataDDXCommand(BaseTypeFactory btf) {
            dds = new DataDDS(ver, btf);
        }

        public void process(InputStream is) throws DAP2Exception, ParseException {
            dds.parseXML(is, false);
        }
    }


    /**
     * Returns the `Data object' from the dataset referenced by this object's
     * URL given the constraint expression CE. Note that the Data object is
     * really just a DDS object with data bound to the variables. The DDS will
     * probably contain fewer variables (and those might have different
     * types) than in the DDS returned by getDDS() because that method returns
     * the entire DDS (but without any data) while this method returns
     * only those variables listed in the projection part of the constraint
     * expression.
     * <p/>
     * Note that if CE is an empty String then the entire dataset will be
     * returned, unless a "sticky" CE has been specified in the constructor.
     *
     * @param CE       The constraint expression to be applied to this request by the
     *                 server.  This is combined with any CE given in the constructor.
     * @param statusUI the <code>StatusUI</code> object to use for GUI updates
     *                 and user cancellation notification (may be null).
     * @param btf      The <code>BaseTypeFactory</code> to build the member
     *                 variables in the DDS with.
     * @return The <code>DataDDS</code> object that results from applying the
     *         given CE, combined with this object's sticky CE, on the referenced
     *         dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if any error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if any error returned by the remote server
     */
    public DataDDS getData(String CE, StatusUI statusUI, BaseTypeFactory btf) throws  IOException,
            ParseException, DAP2Exception {

        DataDDS dds = new DataDDS(ver, btf);
        if (filePath != null) {
            File f = new File(filePath);
            if (f.exists()) {
                FileInputStream fis = new FileInputStream(f);
                dds.parse(new HeaderInputStream(fis)); // read the DDS header
                dds.readData(fis, null); // read the data!
                return dds;
            } else  {
                System.err.println("No such file: " + f.getName());
                return null;
            }

        } else { // must be a remote url
            DataDDSCommand command = new DataDDSCommand(dds, statusUI);
            String urls = urlString + ".dods" + getCompleteCE(CE);
            openConnection(urls, command);
            return command.dds;
        }



    }

    private class DataDDSCommand implements Command {
        DataDDS dds;
        StatusUI statusUI;

        DataDDSCommand(DataDDS dds, StatusUI statusUI) {
            this.dds = dds;
            this.statusUI = statusUI;
        }

        public void process(InputStream is) throws DAP2Exception, ParseException, IOException {
            dds.parse(new HeaderInputStream(is));
            dds.readData(is, statusUI);
        }
    }


    public DataDDS getData(String CE) throws IOException, ParseException, DAP2Exception {
        return getData(CE, null, new DefaultFactory());
    }

    /**
     * Returns the `Data object' from the dataset referenced by this object's
     * URL given the constraint expression CE. Note that the Data object is
     * really just a DDS object with data bound to the variables. The DDS will
     * probably contain fewer variables (and those might have different
     * types) than in the DDS returned by getDDS() because that method returns
     * the entire DDS (but without any data) while this method returns
     * only those variables listed in the projection part of the constraint
     * expression.
     * <p/>
     * Note that if CE is an empty String then the entire dataset will be
     * returned, unless a "sticky" CE has been specified in the constructor.
     * <p/>
     * <p/>
     * This method uses the 2 step method for aquiring data from a server using
     * a DDX and a BLOB. First, a DDX (an XML representation of a DDS) is requested.
     * The DDX is parsed and a DataDDS is created.
     * The DDX contains a URL that points to the servers BLOB service. The BLOB
     * service returns only the serialized binary content of the DataDDS. The DataDDS
     * then deserializes the BLOB and fills itself with data.
     *
     * @param CE       The constraint expression to be applied to this request by the
     *                 server.  This is combined with any CE given in the constructor.
     * @param statusUI the <code>StatusUI</code> object to use for GUI updates
     *                 and user cancellation notification (may be null).
     * @return The <code>DataDDS</code> object that results from applying the
     *         given CE, combined with this object's sticky CE, on the referenced
     *         dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if any error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if any error returned by the remote server
     * @opendap.ddx.experimental
     *
    public DataDDS getDDXData(String CE, StatusUI statusUI, BaseTypeFactory btf) throws MalformedURLException, IOException,
    ParseException, DDSException, DAP2Exception {

    String urls = urlString + ".ddx" + getCompleteCE(CE);

    DataDDS dds = new DataDDS(ver, btf);
    DataDDXCommand command = new DataDDXCommand(dds, statusUI);
    openConnection(urls, command);

    return command.dds;
    }

    private class DataDDXCommand implements Command {
    DataDDS dds;
    StatusUI statusUI;

    DataDDXCommand(DataDDS dds, StatusUI statusUI) {
    this.dds = dds;
    this.statusUI = statusUI;
    }

    /*
     * Returns the `Data object' from the dataset referenced by this object's
     * URL given the constraint expression CE. Note that the Data object is
     * really just a DDS object with data bound to the variables. The DDS will
     * probably contain fewer variables (and those might have different
     * types) than in the DDS returned by getDDS() because that method returns
     * the entire DDS (but without any data) while this method returns
     * only those variables listed in the projection part of the constraint
     * expression.
     * <p/>
     * Note that if CE is an empty String then the entire dataset will be
     * returned, unless a "sticky" CE has been specified in the constructor.
     * <p/>
     * <p/>
     * This method uses the 2 step method for aquiring data from a server using
     * a DDX and a BLOB. First, a DDX (an XML representation of a DDS) is requested.
     * The DDX is parsed and a DataDDS is created.
     * The DDX contains a URL that points to the servers BLOB service. The BLOB
     * service returns only the serialized binary content of the DataDDS. The DataDDS
     * then deserializes the BLOB and fills itself with data.

    public void process(InputStream is) throws DAP2Exception, ParseException, IOException {
    dds.parseXML(is, false);    // read the DDX
    getBlobData(dds, statusUI);
    }
    }  */

    /**
     * Opens the BLOB uRL in the DDS supplied and deserializes that binary content
     * sent from the server cooresponding to the DDS.
     * <p/>
     * <p/>
     * This method is the 2nd step in the 2 step process for aquiring data from a server using
     * a DDX and a BLOB. First, a DDX (an XML representation of a DDS) is requested.
     * The DDX is parsed and a DataDDS is created.
     * The DDX contains a URL that points to the servers BLOB service. The BLOB
     * service returns only the serialized binary content of the DataDDS. The DataDDS
     * then deserializes the BLOB and fills itself with data.
     *
     * @param dds      The DDS containing the BLOB URL and into which the BLOB
     *                 (serialized binary content) will be deserialized.
     * @param statusUI the <code>StatusUI</code> object to use for GUI updates
     *                 and user cancellation notification (may be null).
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if any error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if any error returned by the remote server
     *
    private void getBlobData(DataDDS dds, StatusUI statusUI)
    throws MalformedURLException, IOException,
    ParseException, DDSException, DAP2Exception {


    /* boolean dumpStreamErr = false; // opendap.util.Debug.isSet("dumpStreamErr");

    System.out.println("dds.getBlobURL(): " + dds.getBlobContentID());

    if (dds.getBlobContentID() == null) {
    throw new MalformedURLException("Blob URL was 'null'. " +
    "This may indicate that this OPeNDAP Server does not support the full use of DDX.");
    }


    URL blobURL = new URL(dds.getBlobContentID());

    System.out.println("Opening BLOB URL: " + blobURL);

    InputStream is = openConnection(blobURL);


    try {

    dds.readData(is, statusUI); // read the data!

    } catch (Throwable e) {
    System.out.println("DConnect dds.readData problem with: " + blobURL + "\nStack Trace:");
    e.printStackTrace(System.out);

    throw new DAP2Exception("Connection problem when reading: " + blobURL + "\n" +
    "Error Message - " + e.toString());

    } finally {
    is.close();  // stream is always closed even if parse() throws exception
    if (connection instanceof HttpURLConnection)
    ((HttpURLConnection) connection).disconnect();
    }


    } */

    /**
     * Returns the `Data object' from the dataset referenced by this object's
     * URL given the constraint expression CE. Note that the Data object is
     * really just a DDS object with data bound to the variables. The DDS will
     * probably contain fewer variables (and those might have different
     * types) than in the DDS returned by getDDS() because that method returns
     * the entire DDS (but without any data) while this method returns
     * only those variables listed in the projection part of the constraint
     * expression.
     * <p/>
     * Note that if CE is an empty String then the entire dataset will be
     * returned, unless a "sticky" CE has been specified in the constructor.
     * <p/>
     * <p/>
     * This method uses the 2 step method for aquiring data from a server using
     * a DDX and a BLOB. First, a DDX (an XML representation of a DDS) is requested.
     * The DDX is parsed and a DataDDS is created.
     * The DDX contains a URL that points to the servers BLOB service. The BLOB
     * service returns only the serialized binary content of the DataDDS. The DataDDS
     * then deserializes the BLOB and fills itself with data.
     *
     * @param url      The complete URL of the dataset. Constraint Expression included.
     * @param statusUI the <code>StatusUI</code> object to use for GUI updates
     *                 and user cancellation notification (may be null).
     * @param btf      The <code>BaseTypeFactory</code> to build the member
     *                 variables in the DDS with.
     * @return The <code>DataDDS</code> object that results from applying the
     *         given CE, combined with this object's sticky CE, on the referenced
     *         dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if any error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if any error returned by the remote server
     * @opendap.ddx.experimental
     *
    public DataDDS getDDXDataFromURL(URL url, StatusUI statusUI, BaseTypeFactory btf)
    throws IOException,
    ParseException, DDSException, DAP2Exception {

    System.out.println("Opening DDX URL: " + url);
    InputStream is = openConnection(url);
    DataDDS dds = new DataDDS(ver, btf);

    boolean dumpStreamErr = false; // opendap.util.Debug.isSet("dumpStreamErr");


    try {


    dds.parseXML(is, false);    // read the DDX

    //dds.parse(new HeaderInputStream(is));    // read the DDS header
    // NOTE: the HeaderInputStream will have skipped over "Data:" line

    } catch (Throwable e) {
    System.out.println("DConnect ddx.parse problem with: " + url + "\nStack Trace:");
    e.printStackTrace(System.out);

    throw new DAP2Exception("Connection problem when reading: " + url + "\n" +
    "Error Message - " + e.toString());

    } finally {
    is.close();  // stream is always closed even if parse() throws exception
    if (connection instanceof HttpURLConnection)
    ((HttpURLConnection) connection).disconnect();
    }


    getBlobData(dds, statusUI);


    return dds;
    } */

    /**
     * Returns the `Data object' from the dataset referenced by this object's
     * URL given the constraint expression CE. Note that the Data object is
     * really just a DDS object with data bound to the variables. The DDS will
     * probably contain fewer variables (and those might have different
     * types) than in the DDS returned by getDDS() because that method returns
     * the entire DDS (but without any data) while this method returns
     * only those variables listed in the projection part of the constraint
     * expression.
     * <p/>
     * Note that if CE is an empty String then the entire dataset will be
     * returned, unless a "sticky" CE has been specified in the constructor.
     *
     * @param CE       The constraint expression to be applied to this request by the
     *                 server.  This is combined with any CE given in the constructor.
     * @param statusUI the <code>StatusUI</code> object to use for GUI updates
     *                 and user cancellation notification (may be null).
     * @return The <code>DataDDS</code> object that results from applying the
     *         given CE, combined with this object's sticky CE, on the referenced
     *         dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if any error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if any error returned by the remote server
     */
    public DataDDS getData(String CE, StatusUI statusUI) throws IOException,
            ParseException, DAP2Exception {

        return getData(CE, statusUI, new DefaultFactory());
    }

    /**
     * Returns the `Data object' from the dataset referenced by this object's
     * URL given the constraint expression CE. Note that the Data object is
     * really just a DDS object with data bound to the variables. The DDS will
     * probably contain fewer variables (and those might have different
     * types) than in the DDS returned by getDDS() because that method returns
     * the entire DDS (but without any data) while this method returns
     * only those variables listed in the projection part of the constraint
     * expression.
     * <p/>
     * Note that if CE is an empty String then the entire dataset will be
     * returned, unless a "sticky" CE has been specified in the constructor.
     * <p/>
     * <p/>
     * This method uses the 2 step method for aquiring data from a server using
     * a DDX and a BLOB. First, a DDX (an XML representation of a DDS) is requested.
     * The DDX is parsed and a DataDDS is created.
     * The DDX contains a URL that points to the servers BLOB service. The BLOB
     * service returns only the serialized binary content of the DataDDS. The DataDDS
     * then deserializes the BLOB and fills itself with data.
     *
     * @param CE       The constraint expression to be applied to this request by the
     *                 server.  This is combined with any CE given in the constructor.
     * @param statusUI the <code>StatusUI</code> object to use for GUI updates
     *                 and user cancellation notification (may be null).
     * @return The <code>DataDDS</code> object that results from applying the
     *         given CE, combined with this object's sticky CE, on the referenced
     *         dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if any error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if any error returned by the remote server
     * @opendap.ddx.experimental
     *
    public DataDDS getDDXData(String CE, StatusUI statusUI) throws MalformedURLException, IOException,
    ParseException, DDSException, DAP2Exception {

    return getDDXData(CE, statusUI, new DefaultFactory());
    } */


    /**
     * Return the data object with no local constraint expression.  Same as
     * <code>getData("", statusUI)</code>.
     *
     * @param statusUI the <code>StatusUI</code> object to use for GUI updates
     *                 and user cancellation notification (may be null).
     * @return The <code>DataDDS</code> object that results from applying
     *         this object's sticky CE, if any, on the referenced dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if any error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if any error returned by the remote server
     */
    public final DataDDS getData(StatusUI statusUI) throws  IOException,
            ParseException, DAP2Exception {
        return getData("", statusUI, new DefaultFactory());
    }

    /**
     * Returns the `Data object' from the dataset referenced by this object's
     * URL given the constraint expression CE. Note that the Data object is
     * really just a DDS object with data bound to the variables. The DDS will
     * probably contain fewer variables (and those might have different
     * types) than in the DDS returned by getDDS() because that method returns
     * the entire DDS (but without any data) while this method returns
     * only those variables listed in the projection part of the constraint
     * expression.
     * <p/>
     * Note that if CE is an empty String then the entire dataset will be
     * returned, unless a "sticky" CE has been specified in the constructor.
     * <p/>
     * <p/>
     * This method uses the 2 step method for aquiring data from a server using
     * a DDX and a BLOB. First, a DDX (an XML representation of a DDS) is requested.
     * The DDX is parsed and a DataDDS is created.
     * The DDX contains a URL that points to the servers BLOB service. The BLOB
     * service returns only the serialized binary content of the DataDDS. The DataDDS
     * then deserializes the BLOB and fills itself with data.
     *
     * @param statusUI the <code>StatusUI</code> object to use for GUI updates
     *                 and user cancellation notification (may be null).
     * @return The <code>DataDDS</code> object that results from applying the
     *         given CE, combined with this object's sticky CE, on the referenced
     *         dataset.
     * @throws MalformedURLException if the URL given to the constructor
     *                               has an error
     * @throws IOException           if any error connecting to the remote server
     * @throws ParseException        if the DDS parser returned an error
     * @throws DDSException          on an error constructing the DDS
     * @throws DAP2Exception         if any error returned by the remote server
     * @opendap.ddx.experimental
     *
    public final DataDDS getDDXData(StatusUI statusUI) throws MalformedURLException, IOException,
    ParseException, DDSException, DAP2Exception {
    return getDDXData("", statusUI, new DefaultFactory());
    } */


    /**
     * @param args command line arguments
     */
    public static void main(String[] args) {

        DConnect2 dc;

        for (String url : args) {
            try {
                System.out.println("");
                System.out.println("");
                System.out.println("########################################################");
                System.out.println("\nConnecting to " + url + "\n");

                // Make a new DConnect2 object for the dataset URL/file.
                dc = new DConnect2(url);

                System.out.println("\n- - - - - - - - - - - - - - - - - - -");

                System.out.println("Retrieving DDS:\n");
                DDS dds = dc.getDDS();
                dds.print(System.out);

                System.out.println("\n- - - - - - - - - - - - - - - - - - -");
                System.out.println("Retrieving DAS:\n");
                DAS das = dc.getDAS();
                das.print(System.out);

                System.out.println("\n- - - - - - - - - - - - - - - - - - -");
                System.out.println("Retrieving DDX:\n");
                dds = dc.getDDX();
                dds.printXML(System.out);


                System.out.println("\n- - - - - - - - - - - - - - - - - - -");
                System.out.println("Retrieving DATA:\n");
                dds = dc.getData("");
                dds.printVal(System.out, "");

                System.out.println("\n- - - - - - - - - - - - - - - - - - -");
                System.out.println("Writing DATA:\n");

                FileOutputStream fos = new FileOutputStream("dc2.out");
                DataOutputStream dos = new DataOutputStream(fos);
                dds.externalize(dos);

            } catch (Throwable t) {
                t.printStackTrace(System.err);
            }

        }

    }


}


