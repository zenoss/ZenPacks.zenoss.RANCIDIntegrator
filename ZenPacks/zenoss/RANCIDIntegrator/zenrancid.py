#!/usr/bin/env python
######################################################################
#
# Copyright 2007 Zenoss, Inc.  All Rights Reserved.
#
######################################################################
import sys, os

import Globals
from Products.ZenUtils.ZenScriptBase import ZenScriptBase

import logging
log = logging.getLogger("zen.rancidUpdater")

class ZenRancid(ZenScriptBase):
    def __init__(self):
        ZenScriptBase.__init__(self, connect=True)
        self.rancidRoot = self.dmd.Devices.zRancidRoot

    def run(self):
        group_buckets = {}

        for dev in self.dmd.Devices.getSubDevices():
            if not self.validateDevice(dev): continue

            if not group_buckets.has_key(dev.zRancidGroup):
                group_buckets[dev.zRancidGroup] = []

            if dev.getPingStatus() == 0:
                status = 'up'
            else:
                status = 'down'

            log.info("Added %s (%s) to %s with type: %s",
                dev.id, dev.manageIp, dev.zRancidGroup, dev.zRancidType)

            group_buckets[dev.zRancidGroup].append(
                dev.manageIp + ":" + dev.zRancidType + ":" + status)

        for group, entries in group_buckets.items():
            entries.sort()

            rancid_db = open(os.path.join(self.rancidRoot, 'var',
                group, 'router.db'), 'w')

            for entry in entries:
                rancid_db.write("%s\n" % (entry,))

            rancid_db.close()

    def validateDevice(self, device):
        if not hasattr(device, 'zRancidType'):
            return False

        if device.zRancidType.strip() == '':
            return False

        if not hasattr(device, 'zRancidGroup'):
            log.warn("%s has no zRancidGroup property", device.id)
            return False

        if device.zRancidGroup.strip() == '':
            log.warn("%s has an empty zRancidGroup property", device.id)
            return False

        if not hasattr(device, 'productionState'):
            return False

        if device.productionState < 0:
            return False

        return True


if __name__ == "__main__":
    u = ZenRancid()
    u.run()

