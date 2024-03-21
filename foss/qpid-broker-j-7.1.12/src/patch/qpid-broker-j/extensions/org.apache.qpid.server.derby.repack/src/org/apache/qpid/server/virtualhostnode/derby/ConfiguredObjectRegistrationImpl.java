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

import java.util.Collection;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

import org.apache.qpid.server.model.ConfiguredObject;
import org.apache.qpid.server.plugin.ConfiguredObjectRegistration;

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
public class ConfiguredObjectRegistrationImpl
        implements ConfiguredObjectRegistration {

    protected Set<Class<? extends ConfiguredObject>> implementations;

    public ConfiguredObjectRegistrationImpl() {
        Set<Class<? extends ConfiguredObject>> impl = new HashSet<>();
        impl.add(DerbyRepackingVirtualHostNodeImpl.class);
        implementations = Collections.unmodifiableSet(impl);
    }

    @Override
    public String getType() {
        return "org.apache.qpid.server.virtualhostnode.derby.repack";
    }

    @Override
    public Collection<Class<? extends ConfiguredObject>> getConfiguredObjectClasses() {
        return implementations;
    }

}
