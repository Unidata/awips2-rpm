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

package org.apache.qpid.server.virtualhost.derby;

import java.util.Map;

import org.apache.qpid.server.derby.DerbyRepackingMessageStore;
import org.apache.qpid.server.model.ManagedObject;
import org.apache.qpid.server.model.VirtualHostNode;
import org.apache.qpid.server.store.MessageStore;
import org.apache.qpid.server.virtualhost.derby.DerbyVirtualHostImpl;

/**
 *
 * Extension to ensure that the DerbyRepackingMessageStore is used when the type
 * is set to DERBY-REPACK.
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
@ManagedObject(type = "DERBY-REPACK", category = false)
public class DerbyRepackingVirtualHostImpl extends DerbyVirtualHostImpl {

    public DerbyRepackingVirtualHostImpl(Map<String, Object> attributes,
            VirtualHostNode<?> virtualHostNode) {
        super(attributes, virtualHostNode);
    }

    @Override
    protected MessageStore createMessageStore() {
        return new DerbyRepackingMessageStore();
    }

}
