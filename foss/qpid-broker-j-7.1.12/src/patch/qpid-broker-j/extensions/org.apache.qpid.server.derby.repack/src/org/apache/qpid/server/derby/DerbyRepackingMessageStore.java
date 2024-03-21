/**
 * This software was developed and / or modified by Raytheon Company,
 * pursuant to Contract EA133W-17-CQ-0082 with the US Government.
 *
 * U.S. EXPORT CONTROLLED TECHNICAL DATA
 * This software product contains export-restricted data whose
 * export/transfer/disclosure is restricted by U.S. law. Dissemination
 * to non-U.S. persons whether in the United States or abroad requires
 * an export license or other authorization.
 *
 * Contractor Name:        Raytheon Company
 * Contractor Address:     2120 South 72nd Street, Suite 900
 *                         Omaha, NE 68124
 *                         402.291.0100
 *
 * See the AWIPS II Master Rights File ("Master Rights File.pdf") for
 * further licensing information.
 **/

package org.apache.qpid.server.derby;

import java.sql.Array;
import java.sql.Blob;
import java.sql.CallableStatement;
import java.sql.Clob;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.NClob;
import java.sql.PreparedStatement;
import java.sql.SQLClientInfoException;
import java.sql.SQLException;
import java.sql.SQLWarning;
import java.sql.SQLXML;
import java.sql.Savepoint;
import java.sql.Statement;
import java.sql.Struct;
import java.util.Map;
import java.util.Properties;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executor;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock.ReadLock;
import java.util.concurrent.locks.ReentrantReadWriteLock.WriteLock;

import org.apache.qpid.server.model.ConfiguredObject;
import org.apache.qpid.server.store.StoreException;
import org.apache.qpid.server.store.derby.DerbyMessageStore;
import org.apache.qpid.server.store.jdbc.JdbcUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 *
 * Extension of DerbyMessageStore that sends the Derby compress commands at a
 * set time after startup and then every n hours where n is configurable.
 *
 * Wraps the database connections in a wrapper that obtains shared read locks
 * for all connections, except the compress/repack task which obtains a write
 * lock. This is necessary to avoid database deadlock when running the compress
 * command.
 *
 * <pre>
 *
 * SOFTWARE HISTORY
 *
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Sep 06, 2022 8952       njensen     Initial creation
 *
 * </pre>
 *
 */
public class DerbyRepackingMessageStore extends DerbyMessageStore {

    private static final Logger LOGGER = LoggerFactory
            .getLogger(DerbyRepackingMessageStore.class);

    private static final String STARTUP_DELAY_PROP = "derby.repack.startup.delay.ms";

    private static final String INTERVAL_PROP = "derby.repack.interval.hours";

    protected final Timer timer = new Timer("RepackTimer");

    /**
     * Due to inability to override some methods, need to delay the startup
     * compression task so Qpid has time to open and restore the Derby message
     * store
     **/
    protected final long startupDelayMs;

    /** run the compression task every n hours where n is intervalHours **/
    protected final int intervalHours;

    protected ReadWriteLock lock = new ReentrantReadWriteLock();

    /**
     * ReadWriteLock's locks are tied to the thread and the connection may be
     * opened and closed on different threads. This causes an error if the
     * thread obtaining the lock does not match the thread releasing the lock.
     * Therefore, we use this executor as a hack to get around that.
     */
    private final ExecutorService readLockExecutor = Executors
            .newSingleThreadExecutor();

    public DerbyRepackingMessageStore() {
        // check startup delay in ms property
        long startupDelay = 60000;
        String sd = System.getProperty(STARTUP_DELAY_PROP);
        if (sd != null) {
            try {
                startupDelay = Long.parseLong(sd);
            } catch (NumberFormatException e) {
                LOGGER.error("Error parsing system property "
                        + STARTUP_DELAY_PROP + ". Default of " + startupDelay
                        + " ms will be used instead.");
            }
        } else {
            LOGGER.info("System property " + STARTUP_DELAY_PROP
                    + " not set. Defaulting to " + startupDelay + " ms.");
        }
        if (startupDelay < 30000) {
            throw new IllegalStateException("System property "
                    + STARTUP_DELAY_PROP + " must be at least 30000 ms.");
        } else {
            LOGGER.info("Initial repack will run in " + startupDelay + " ms.");
        }
        startupDelayMs = startupDelay;

        // check interval in hours property
        int interval = 24;
        String ih = System.getProperty(INTERVAL_PROP);
        if (ih != null) {
            try {
                interval = Integer.parseInt(ih);
            } catch (NumberFormatException e) {
                LOGGER.error("Error parsing system property " + INTERVAL_PROP
                        + ". Default of " + interval
                        + " hours will be used instead.");
            }
        } else {
            LOGGER.info("System property " + INTERVAL_PROP
                    + " not set. Defaulting to " + interval + " hours.");
        }
        if (interval < 1) {
            throw new IllegalStateException("System property " + INTERVAL_PROP
                    + " must be at least 1 hour.");
        } else {
            LOGGER.info("Repack will run every " + interval + " hours.");
        }
        intervalHours = interval;
    }

    @Override
    protected void doOpen(final ConfiguredObject<?> parent) {
        LOGGER.info(
                "Repacking enabled. To disable repacking, switch message store type back to DERBY.");
        super.doOpen(parent);
        /*
         * it's not fully open yet, see AbstractDerbyMessageStore.doOpen(), so
         * we delay the startup repack task
         */
        timer.scheduleAtFixedRate(new DiskCompressor(), startupDelayMs,
                intervalHours * 60 * 60 * 1000);
    }

    @Override
    protected void doClose() {
        timer.cancel();
        super.doClose();
    }

    @SuppressWarnings("rawtypes")
    @Override
    public void onDelete(ConfiguredObject parent) {
        timer.cancel();
        super.onDelete(parent);
    }

    @Override
    protected Connection newConnection() throws SQLException {
        Connection connection = super.newConnection();
        ReadLock connectionLock = (ReadLock) lock.readLock();
        ReadLockConnectionWrapper c = new ReadLockConnectionWrapper(connection,
                connectionLock);
        return c;
    }

    /**
     * Obtains a write lock from the lock and then calls Derby's compression
     * function against some of the Qpid tables.
     */
    protected void reduceSizeOnDisk() {
        ReadLockConnectionWrapper conn = null;
        WriteLock compressLock = null;
        try {
            conn = (ReadLockConnectionWrapper) newAutoCommitConnection();
            // release the automatically obtained read lock
            conn.unlock();
            compressLock = (WriteLock) lock.writeLock();
            compressLock.lock();
            LOGGER.info("Acquired write lock for compression.");

            // do the compression/release the space back to the OS
            LOGGER.info("Compressing QPID_QUEUE_ENTRIES.");
            conn.prepareStatement(
                    "call SYSCS_UTIL.SYSCS_COMPRESS_TABLE('APP', 'QPID_QUEUE_ENTRIES', 0)")
                    .executeUpdate();
            LOGGER.info("Compressing QPID_MESSAGE_METADATA.");
            conn.prepareStatement(
                    "call SYSCS_UTIL.SYSCS_COMPRESS_TABLE('APP', 'QPID_MESSAGE_METADATA', 0)")
                    .executeUpdate();
            LOGGER.info("Compressing QPID_MESSAGE_CONTENT.");
            conn.prepareStatement(
                    "call SYSCS_UTIL.SYSCS_COMPRESS_TABLE('APP', 'QPID_MESSAGE_CONTENT', 0)")
                    .executeUpdate();
            LOGGER.info("Compressing QPID_XIDS.");
            conn.prepareStatement(
                    "call SYSCS_UTIL.SYSCS_COMPRESS_TABLE('APP', 'QPID_XIDS', 0)")
                    .executeUpdate();
            LOGGER.info("Compressing QPID_XID_ACTIONS.");
            conn.prepareStatement(
                    "call SYSCS_UTIL.SYSCS_COMPRESS_TABLE('APP', 'QPID_XID_ACTIONS', 0)")
                    .executeUpdate();
        } catch (SQLException e) {
            throw new StoreException("Error reducing on disk size", e);
        } finally {
            JdbcUtils.closeConnection(conn, getLogger());
            if (compressLock != null) {
                LOGGER.info("Releasing compression's write lock.");
                compressLock.unlock();
                compressLock = null;
            }
        }
    }

    @Override
    protected Logger getLogger() {
        return LOGGER;
    }

    protected final class DiskCompressor extends TimerTask {

        @Override
        public void run() {
            if (isMessageStoreOpen()) {
                LOGGER.info(
                        "Attempting to return unused disk space to the operating system.");
                reduceSizeOnDisk();
                LOGGER.info(
                        "Finished returning unused disk space to the operating system.");
            } else {
                LOGGER.warn(
                        "Repack skipped because message store is not open.");
            }

        }
    }

    /**
     * Connection wrapper that immediately obtains a lock from the provided
     * ReadLock. The lock is released in close(). This enables all connections
     * used by this database to run simultaneously with shared read locks until
     * the write lock used by the DiskCompressor TimerTask is obtained and
     * temporarily blocks all other connections.
     */
    protected final class ReadLockConnectionWrapper implements Connection {

        private final Connection delegate;

        private final ReadLock connLock;

        /*
         * close() can be called multiple times so we use this variable to
         * ensure a lock can only be obtained and released once per connection
         */
        private boolean locked = false;

        /**
         * Constructor that takes an existing Connection and passes all calls
         * through to methods on the Connection interface.
         *
         * @param delegate
         *            the connection to use as the underlying connection
         * @param connLock
         *            the read lock to obtain a lock on
         */
        protected ReadLockConnectionWrapper(Connection delegate,
                ReadLock connLock) {
            this.delegate = delegate;
            this.connLock = connLock;
            lock();
        }

        protected synchronized void lock() {
            if (!locked) {
                try {
                    readLockExecutor.submit(() -> connLock.lock()).get();
                    locked = true;
                } catch (InterruptedException | ExecutionException e) {
                    LOGGER.error(
                            "Error obtaining read lock for connection. This is bad. Consider switching message store type back to DERBY or at least restart Qpid.",
                            e);
                }
            }
        }

        protected synchronized void unlock() {
            if (locked) {
                try {
                    readLockExecutor.submit(() -> connLock.unlock()).get();
                    locked = false;
                } catch (InterruptedException | ExecutionException e) {
                    LOGGER.error(
                            "Error releasing connection's read lock. This is really bad. Consider switching message store type back to DERBY or at least restart Qpid.",
                            e);
                }
            }
        }

        @Override
        public void close() throws SQLException {
            try {
                delegate.close();
            } finally {
                unlock();
            }
        }

        @Override
        public <T> T unwrap(Class<T> iface) throws SQLException {
            return delegate.unwrap(iface);
        }

        @Override
        public boolean isWrapperFor(Class<?> iface) throws SQLException {
            return delegate.isWrapperFor(iface);
        }

        @Override
        public Statement createStatement() throws SQLException {
            return delegate.createStatement();
        }

        @Override
        public PreparedStatement prepareStatement(String sql)
                throws SQLException {
            return delegate.prepareStatement(sql);
        }

        @Override
        public CallableStatement prepareCall(String sql) throws SQLException {
            return delegate.prepareCall(sql);
        }

        @Override
        public String nativeSQL(String sql) throws SQLException {
            return delegate.nativeSQL(sql);
        }

        @Override
        public void setAutoCommit(boolean autoCommit) throws SQLException {
            delegate.setAutoCommit(autoCommit);
        }

        @Override
        public boolean getAutoCommit() throws SQLException {
            return delegate.getAutoCommit();
        }

        @Override
        public void commit() throws SQLException {
            delegate.commit();
        }

        @Override
        public void rollback() throws SQLException {
            delegate.rollback();
        }

        @Override
        public boolean isClosed() throws SQLException {
            return delegate.isClosed();
        }

        @Override
        public DatabaseMetaData getMetaData() throws SQLException {
            return delegate.getMetaData();
        }

        @Override
        public void setReadOnly(boolean readOnly) throws SQLException {
            delegate.setReadOnly(readOnly);

        }

        @Override
        public boolean isReadOnly() throws SQLException {
            return delegate.isReadOnly();
        }

        @Override
        public void setCatalog(String catalog) throws SQLException {
            delegate.setCatalog(catalog);
        }

        @Override
        public String getCatalog() throws SQLException {
            return delegate.getCatalog();
        }

        @Override
        public void setTransactionIsolation(int level) throws SQLException {
            delegate.setTransactionIsolation(level);

        }

        @Override
        public int getTransactionIsolation() throws SQLException {
            return delegate.getTransactionIsolation();
        }

        @Override
        public SQLWarning getWarnings() throws SQLException {
            return delegate.getWarnings();
        }

        @Override
        public void clearWarnings() throws SQLException {
            delegate.clearWarnings();
        }

        @Override
        public Statement createStatement(int resultSetType,
                int resultSetConcurrency) throws SQLException {
            return delegate.createStatement(resultSetType,
                    resultSetConcurrency);
        }

        @Override
        public PreparedStatement prepareStatement(String sql, int resultSetType,
                int resultSetConcurrency) throws SQLException {
            return delegate.prepareStatement(sql, resultSetType,
                    resultSetConcurrency);
        }

        @Override
        public CallableStatement prepareCall(String sql, int resultSetType,
                int resultSetConcurrency) throws SQLException {
            return delegate.prepareCall(sql, resultSetType,
                    resultSetConcurrency);
        }

        @Override
        public Map<String, Class<?>> getTypeMap() throws SQLException {
            return delegate.getTypeMap();
        }

        @Override
        public void setTypeMap(Map<String, Class<?>> map) throws SQLException {
            delegate.setTypeMap(map);
        }

        @Override
        public void setHoldability(int holdability) throws SQLException {
            delegate.setHoldability(holdability);
        }

        @Override
        public int getHoldability() throws SQLException {
            return delegate.getHoldability();
        }

        @Override
        public Savepoint setSavepoint() throws SQLException {
            return delegate.setSavepoint();
        }

        @Override
        public Savepoint setSavepoint(String name) throws SQLException {
            return delegate.setSavepoint(name);
        }

        @Override
        public void rollback(Savepoint savepoint) throws SQLException {
            delegate.rollback(savepoint);
        }

        @Override
        public void releaseSavepoint(Savepoint savepoint) throws SQLException {
            delegate.releaseSavepoint(savepoint);
        }

        @Override
        public Statement createStatement(int resultSetType,
                int resultSetConcurrency, int resultSetHoldability)
                throws SQLException {
            return delegate.createStatement(resultSetType, resultSetConcurrency,
                    resultSetHoldability);
        }

        @Override
        public PreparedStatement prepareStatement(String sql, int resultSetType,
                int resultSetConcurrency, int resultSetHoldability)
                throws SQLException {
            return delegate.prepareStatement(sql, resultSetType,
                    resultSetConcurrency, resultSetHoldability);
        }

        @Override
        public CallableStatement prepareCall(String sql, int resultSetType,
                int resultSetConcurrency, int resultSetHoldability)
                throws SQLException {
            return delegate.prepareCall(sql, resultSetType,
                    resultSetConcurrency, resultSetHoldability);
        }

        @Override
        public PreparedStatement prepareStatement(String sql,
                int autoGeneratedKeys) throws SQLException {
            return delegate.prepareStatement(sql, autoGeneratedKeys);
        }

        @Override
        public PreparedStatement prepareStatement(String sql,
                int[] columnIndexes) throws SQLException {
            return delegate.prepareStatement(sql, columnIndexes);
        }

        @Override
        public PreparedStatement prepareStatement(String sql,
                String[] columnNames) throws SQLException {
            return delegate.prepareStatement(sql, columnNames);
        }

        @Override
        public Clob createClob() throws SQLException {
            return delegate.createClob();
        }

        @Override
        public Blob createBlob() throws SQLException {
            return delegate.createBlob();
        }

        @Override
        public NClob createNClob() throws SQLException {
            return delegate.createNClob();
        }

        @Override
        public SQLXML createSQLXML() throws SQLException {
            return delegate.createSQLXML();
        }

        @Override
        public boolean isValid(int timeout) throws SQLException {
            return delegate.isValid(timeout);
        }

        @Override
        public void setClientInfo(String name, String value)
                throws SQLClientInfoException {
            delegate.setClientInfo(name, value);
        }

        @Override
        public void setClientInfo(Properties properties)
                throws SQLClientInfoException {
            delegate.setClientInfo(properties);
        }

        @Override
        public String getClientInfo(String name) throws SQLException {
            return delegate.getClientInfo(name);
        }

        @Override
        public Properties getClientInfo() throws SQLException {
            return delegate.getClientInfo();
        }

        @Override
        public Array createArrayOf(String typeName, Object[] elements)
                throws SQLException {
            return delegate.createArrayOf(typeName, elements);
        }

        @Override
        public Struct createStruct(String typeName, Object[] attributes)
                throws SQLException {
            return delegate.createStruct(typeName, attributes);
        }

        @Override
        public void setSchema(String schema) throws SQLException {
            delegate.setSchema(schema);
        }

        @Override
        public String getSchema() throws SQLException {
            return delegate.getSchema();
        }

        @Override
        public void abort(Executor executor) throws SQLException {
            delegate.abort(executor);
        }

        @Override
        public void setNetworkTimeout(Executor executor, int milliseconds)
                throws SQLException {
            delegate.setNetworkTimeout(executor, milliseconds);
        }

        @Override
        public int getNetworkTimeout() throws SQLException {
            return delegate.getNetworkTimeout();
        }

    }

}
