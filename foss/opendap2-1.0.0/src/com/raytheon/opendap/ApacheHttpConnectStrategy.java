/**
 * This software was developed and / or modified by Raytheon Company,
 * pursuant to Contract DG133W-05-CQ-1067 with the US Government.
 * 
 * U.S. EXPORT CONTROLLED TECHNICAL DATA
 * This software product contains export-restricted data whose
 * export/transfer/disclosure is restricted by U.S. law. Dissemination
 * to non-U.S. persons whether in the United States or abroad requires
 * an export license or other authorization.
 * 
 * Contractor Name:        Raytheon Company
 * Contractor Address:     6825 Pine Street, Suite 340
 *                         Mail Stop B8
 *                         Omaha, NE 68106
 *                         402.291.0100
 * 
 * See the AWIPS II Master Rights File ("Master Rights File.pdf") for
 * further licensing information.
 **/
package com.raytheon.opendap;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.util.zip.InflaterInputStream;

import opendap.dap.DAP2Exception;
import opendap.dap.ServerVersion;

import org.apache.http.Header;
import org.apache.http.HttpEntity;
import org.apache.http.HttpHost;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.conn.DefaultProxyRoutePlanner;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.apache.http.protocol.BasicHttpContext;
import org.apache.http.protocol.HttpContext;
import org.apache.http.util.EntityUtils;

/**
 * An {@link HttpConnectStrategy} implementation using the Apache HTTP Client.
 * 
 * <pre>
 * 
 * SOFTWARE HISTORY
 * 
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Jul 06, 2012 634        djohnson    Extracted from DConnect, 
 *                                      added {@link EntityInputStream}.
 * Jul 09, 2012 634        djohnson    Fully consume the entity prior to throwing exception.
 * 
 * Apr 14, 2015            dhladky     upgrading dods/opendap.
 * 
 * </pre>
 * 
 * @author djohnson
 * @version 1.0
 */

public class ApacheHttpConnectStrategy extends BaseHttpConnectStrategy {

    private static HttpClient httpClient;

    private static PoolingHttpClientConnectionManager connectionManager;
    
    private static HttpClientBuilder clientBuilder;
    
    private static RequestConfig requestConfig;

    static {
        connectionManager = new PoolingHttpClientConnectionManager();
        connectionManager.setDefaultMaxPerRoute(10);
        connectionManager.setMaxTotal(100);
        requestConfig = RequestConfig.custom().build();
        clientBuilder = HttpClientBuilder.create();
        clientBuilder.setDefaultRequestConfig(requestConfig);
        clientBuilder.setConnectionManager(connectionManager);
        httpClient = clientBuilder.build();
    }

    @Override
    public InputStream getInputStream(URL url) throws IOException,
            DAP2Exception {
        HttpResponse response = openHttpConnection(url);

        // If the response was null, return null to the caller
        // who will handle any re-requests
        if (response == null) {
            return null;
        }

        HttpEntity entity = response.getEntity();
        return new EntityInputStream(getInputStream(response, entity), entity);
    }

    /**
     * Open a connection to the DODS server.
     * 
     * @param url
     *            the URL to open.
     * @return the opened <code>InputStream</code>.
     * @exception IOException
     *                if an IO exception occurred.
     */
    private HttpResponse openHttpConnection(URL url) throws IOException {

        HttpContext context = new BasicHttpContext();
        HttpGet httpget = null;

        try {
            httpget = new HttpGet(url.toExternalForm());
            HttpResponse r = httpClient.execute(httpget, context);

            if (r.getStatusLine().getStatusCode() == HttpStatus.SC_OK) {
                return r;
            }

            // Status is not OK, abort current get and start again...
            httpget.abort();
        } catch (Exception ex) {
            if (!httpget.isAborted())
                httpget.abort();
            throw new IOException("Failed to open connection to URL: "
                    + url.toExternalForm(), ex);
        }

        return null;
    }

    private InputStream getInputStream(HttpResponse response, HttpEntity entity)
            throws IOException, DAP2Exception {

        StatusLine status = response.getStatusLine();

        if (status.getStatusCode() == HttpStatus.SC_OK) {
            Header descriptionHeader = response
                    .getFirstHeader(CONTENT_DESCRIPTION);
            if (descriptionHeader != null
                    && DODS_ERROR.equals(descriptionHeader.getValue())) {
                DAP2Exception ds = new DAP2Exception();
                // parse the Error object from stream and throw it
                // The entity must be fully consumed in the finally clause
                // since we are throwing an exception.
                try {
                    ds.parse(entity.getContent());
                    throw ds;
                } finally {
                    EntityUtils.consume(entity);
                }
            }

            String fullVersionHeader = response.getFirstHeader(XDODS_SERVER)
                    .getValue();
            int serverType = ServerVersion.XDODS_SERVER;
            ver = new ServerVersion(fullVersionHeader, serverType);
            String encoding = null;
            Header e = entity.getContentEncoding();
            if (e != null) {
                encoding = e.getValue();
            }

            return handleContentEncoding(entity.getContent(), encoding);
        }

        return null;
    }
    
    /**
     * This is an application level override of the Method in the DConnect class of DAP
     * This code handles the Content-type: header for
     * <code>openConnection</code> and <code>parseMime</code>
     *
     * @param is       the InputStream to read.
     * @param encoding the Content-type header, or null.
     * @return the new InputStream, after applying an
     *         <code>InflaterInputStream</code> filter if necessary.
     */
    private static InputStream handleContentEncoding(InputStream is, String encoding) {
        if (encoding != null && encoding.equals("deflate")) {
            return new InflaterInputStream(is);
        } else {
            return is;
        }
    }

    @Override
    public void setProxy(String host, int port) {
        HttpHost proxy = new HttpHost(host, port);
        DefaultProxyRoutePlanner routePlanner = new DefaultProxyRoutePlanner(proxy);
        clientBuilder.setRoutePlanner(routePlanner);
    }

    @Override
    public void setDeflate(boolean deflate) {
        if (deflate) {
            // is added by default
        } else {
            clientBuilder.disableContentCompression();
        }
    }


    @Override
    public void setConnectionTimeout(int connectionTimeout) {
        RequestConfig.custom()
                .setConnectTimeout(connectionTimeout * 1000);
    }

    @Override
    public void setSocketTimeout(int socketTimeout) {
        RequestConfig.custom()
                .setSocketTimeout(socketTimeout * 1000);
    }

    /**
     * Decorates an input stream such that when any operation other than close()
     * is called it is passed through to the decorated object. If close is
     * called, it closes the stream AND calls EntityUtils.consume().
     */
    public static class EntityInputStream extends InputStream {

        private final InputStream decorated;

        private final HttpEntity entity;

        private EntityInputStream(InputStream decorated, HttpEntity entity) {
            this.decorated = decorated;
            this.entity = entity;
        }

        @Override
        public int read() throws IOException {
            return decorated.read();
        }

        @Override
        public int read(byte[] b) throws IOException {
            return decorated.read(b);
        }

        @Override
        public int read(byte[] b, int off, int len) throws IOException {
            return decorated.read(b, off, len);
        }

        @Override
        public long skip(long n) throws IOException {
            return decorated.skip(n);
        }

        @Override
        public int available() throws IOException {
            return decorated.available();
        }

        /**
         * Overridden to consume the {@link HttpEntity} before closing the
         * underlying stream.
         */
        @Override
        public void close() throws IOException {
            try {
                EntityUtils.consume(entity);
            } finally {
                decorated.close();
            }
        }

        @Override
        public synchronized void mark(int readlimit) {
            decorated.mark(readlimit);
        }

        @Override
        public synchronized void reset() throws IOException {
            decorated.reset();
        }

        @Override
        public boolean markSupported() {
            return decorated.markSupported();
        }

        @Override
        public int hashCode() {
            return decorated.hashCode();
        }

        @Override
        public boolean equals(Object obj) {
            return decorated.equals(obj);
        }

        @Override
        public String toString() {
            return decorated.toString();
        }
    }
}
