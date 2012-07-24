#!/usr/bin/env python
##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2007, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


import sys
import os
import re
import operator

import Globals
from Products.ZenUtils.ZenScriptBase import ZenScriptBase

import logging
log = logging.getLogger("zen.rancid")

class ZenRancid(ZenScriptBase):
    def __init__(self):
        ZenScriptBase.__init__(self, connect=True)
        self.rancidRoot = self.dmd.Devices.zRancidRoot


    def buildOptions(self):
        ZenScriptBase.buildOptions(self)
        self.parser.add_option('--update', dest='update',
            action='store_true', default=False,
            help='Update router.db instead of replacing it')
        self.parser.add_option('--name', dest='nameInsteadOfIp',
            action='store_true', default=False,
            help="Write device name instead of IP to router.db")


    def run(self):
        group_buckets = {}

        for dev in self.dmd.Devices.getSubDevices():
            if not self.validateDevice(dev):
                log.info("Not adding %s (%s)", dev.id, dev.manageIp)
                continue

            if not group_buckets.has_key(dev.zRancidGroup):
                group_buckets[dev.zRancidGroup] = {}

            if dev.getPingStatus() == 0:
                status = 'up'
            else:
                status = 'down'

            log.info("Added %s (%s) to %s with type: %s",
                dev.id, dev.manageIp, dev.zRancidGroup, dev.zRancidType)
            
            if self.options.nameInsteadOfIp:
                deviceKey = dev.id
            else:
                deviceKey = dev.manageIp
            
            group_buckets[dev.zRancidGroup][deviceKey] = dict(
                type=dev.zRancidType, status=status)

        for group, entries in group_buckets.items():
            filename = os.path.join(self.rancidRoot, 'var', group, 'router.db')
            
            # Only update existing entries. Don't remove any.
            if self.options.update:
                log.info("Updating existing %s", filename)
                rancid_db = open(filename, 'r')
                for line in rancid_db:
                    match = re.match(r'([^:]+):([^:]+):([^:]+)', line.rstrip())
                    if not match: continue
                    ip, rType, status = match.groups()
                    if entries.has_key(ip): continue
                    entries[ip] = dict(type=rType, status=status)
                
                rancid_db.close()
            else:
                log.info("Replacing %s", filename)
            
            # Sort entries by IP address.
            entryList = sorted(entries.items(), key=operator.itemgetter(0))
            
            # Write out the merged router.db file.
            rancid_db = open(filename, 'w')
            for deviceKey, entry in entryList:
                rancid_db.write("%s:%s:%s\n" % (
                    deviceKey, entry['type'], entry['status']))

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
