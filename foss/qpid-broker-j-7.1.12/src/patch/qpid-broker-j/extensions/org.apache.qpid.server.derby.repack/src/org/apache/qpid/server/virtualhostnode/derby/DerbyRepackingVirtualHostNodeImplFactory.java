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

package org.apache.qpid.server.virtualhostnode.derby;

import java.util.Map;

import org.apache.qpid.server.model.AbstractConfiguredObject;
import org.apache.qpid.server.model.AbstractConfiguredObjectTypeFactory;
import org.apache.qpid.server.model.Broker;
import org.apache.qpid.server.model.ConfiguredObject;

/**
 *
 * Extension to get Qpid to recognize the derby repacking virtual host node.
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
@SuppressWarnings("rawtypes")
public class DerbyRepackingVirtualHostNodeImplFactory
        extends AbstractConfiguredObjectTypeFactory {

    public DerbyRepackingVirtualHostNodeImplFactory() {
        this(DerbyRepackingVirtualHostNodeImpl.class);
    }

    @SuppressWarnings("unchecked")
    public DerbyRepackingVirtualHostNodeImplFactory(Class clazz) {
        super(clazz);
    }

    @SuppressWarnings("unchecked")
    @Override
    protected AbstractConfiguredObject createInstance(Map attributes,
            ConfiguredObject parent) {
        Broker br = (Broker) parent;
        return new DerbyRepackingVirtualHostNodeImpl(attributes, br);
    }

}
