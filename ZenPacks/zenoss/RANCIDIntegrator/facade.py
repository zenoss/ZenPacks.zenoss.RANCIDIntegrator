##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Facade for RANCIDIntegrator API endpoint."""

import cStringIO
import logging

from Products.Zuul.facades import ZuulFacade

from zope.interface import implements

from .interfaces import IRANCIDIntegratorFacade


log = logging.getLogger("zen.rancid")


class RANCIDIntegratorFacade(ZuulFacade):
    """IRANCIDIntegratorFacade implementation."""

    implements(IRANCIDIntegratorFacade)

    def is_rancidable(self, device):
        """Should this device participate in RANCID updates? ."""
        if getattr(device, 'zRancidType', '').strip() == '':
            return False

        if getattr(device, 'zRancidGroup', '').strip() == '':
            log.warn("%s has an empty zRancidGroup property", device.id)
            return False

        if getattr(device, 'productionState', -1) < 0:
            # No decommissioned devices
            return False

        return True

    def get_rancid_configs(self, name_instead_of_ip, root=None):
        """
        For all devices underneath the specified tree.

        Create a mapping of the identifier to
        RANCID-specific device information.
        """
        group_buckets = {}

        if root is None or root == '':
            root = self.context.dmd.Devices
        else:
            root = self.context.dmd.unrestrictedTraverse(root)

        for dev in root.getSubDevicesGen():
            if not self.is_rancidable(dev):
                log.info("Skipping %s (%s)", dev.id, dev.manageIp)
                continue

            if dev.zRancidGroup not in group_buckets:
                group_buckets[dev.zRancidGroup] = {}

            if dev.getPingStatus() == 0:
                status = 'up'
            else:
                status = 'down'

            log.info(
                "Added %s (%s) to %s with type: %s",
                dev.id,
                dev.manageIp,
                dev.zRancidGroup,
                dev.zRancidType
            )

            if name_instead_of_ip:
                device_key = dev.id
            else:
                if not dev.manageIp:
                    log.error(
                        "Skipping device %s with no IP address assigned.",
                        dev.id
                    )
                    continue
                device_key = dev.manageIp

            group_buckets[dev.zRancidGroup][device_key] = dict(
                name=device_key,
                group=dev.zRancidGroup,
                type=dev.zRancidType,
                status=status,
                collector=dev.getPerformanceServer().id,
                manageIp=dev.manageIp
            )

        return group_buckets

    def getRouters(self, name_instead_of_ip):   # noqa
        """API."""
        return True, self.get_rancid_db(name_instead_of_ip)

    def get_rancid_db(self, name_instead_of_ip):
        """
        Generate rancid router.db file.

        Syntax:
        <device_name>;<device_type>;<state>[;comments]
        The 'comments' section will be used for setting collector name
        """
        rancidDatabases = {}
        dbentries = self.get_rancid_configs(name_instead_of_ip)

        for group in dbentries:
            rancidDB = cStringIO.StringIO()
            for dev in dbentries[group]:
                rancidDB.write(
                    "%s;%s;%s;%s\n" % (
                        dev,
                        dbentries[group][dev]['type'],
                        dbentries[group][dev]['status'],
                        dbentries[group][dev]['collector']
                    )
                )

            routerContent = rancidDB.getvalue()
            rancidDB.close()
            rancidDatabases[group] = routerContent

        batchloadContent = self.exportToBatchload(dbentries)

        return {
            "routerDBs": rancidDatabases,
            "batchLoad": batchloadContent
        }

    def exportToBatchload(self, dbentries):
        """Get router.db file content and return batchload format string."""
        batchloadFormat = '"{name}" setPerformanceMonitor="{collector}", ' \
                          'setManageIp="{manageIp}", zRancidType="{type}", ' \
                          'zRancidGroup="{group}"\n'
        if not dbentries:
            return ''

        zbfile = cStringIO.StringIO()

        for database in dbentries.itervalues():
            for data in database.itervalues():
                zbfile.write(batchloadFormat.format(**data))

        contents = zbfile.getvalue()
        zbfile.close()

        return contents
