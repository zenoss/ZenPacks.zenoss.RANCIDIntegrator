#!/usr/bin/env python
##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2007, 2012 all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################

__doc__ = """
Update the RANCID .db files with current state in Zenoss.

"""

import logging
log = logging.getLogger("zen.rancid")

import os
import operator
import socket

import Globals

from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from Products.ZenUtils.IpUtil import isip


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
        self.parser.add_option('--dump2zb', dest='dump2zb', default='',
            help="Read the specified router.db and dump to zenbatchload format")
        self.parser.add_option('--zbfilename', dest='zbfilename',
            default='/tmp/rancid_export.zenbatchload',
            help="Write the router.db export into this file (default %default)")

    def run(self):
        if self.options.dump2zb:
            self.export(self.options.dump2zb)
        else:
            self.updateRancidDbs()

    def updateRancidDbs(self):
        configs = self.getZenossDeviceRancidConfigs()
        for group, entries in configs.items():
            filename = os.path.join(self.rancidRoot, 'var', group, 'router.db')
            
            if self.options.update:
                log.info("Updating existing %s", filename)
                self.readRancidDb(filename, entries)
            else:
                log.info("Replacing %s", filename)
            
            self.writeRancidDb(filename, entries)

    def export(self, path=''):
        """
        Convert RANCID router.db files into zenbatchload format.
        """
        group = 'dummy'
        dbentries = {}
        self.readRancidDb(path, dbentries)
        self.exportBatchLoadFile(group, dbentries, self.options.zbfilename)

    def exportBatchLoadFile(self, group, dbentries, filename):
        """
        Export the router.db data into zenbatchload format file.
        """
        zbfile = open(filename, 'w+')
        for deviceKey, config in dbentries.items():
            id = deviceKey
            data = [
               'zRancidType="%s"' % config['type'],
               'zRancidGroup="%s"' % group,
            ]

            if deviceKey.startswith('#'):
                # Mark the device as decommissioned
                data.append('setProductionState=-1')
                id = deviceKey[1:]

            if self.options.nameInsteadOfIp and isip(id):
                data.append('setManageIp="%s"' % id)
                try:
                    id = socket.gethostbyaddr(id)[0]
                except socket.error:
                    pass

            if 'comment' in config:
                data.append('setComments="%s"' % config['comment'])
          
            zbfile.write('"%s" %s\n' % (id,  ', '.join(data)))
        zbfile.close()
        log.info("Wrote %d entries for %s group to %s",
                 len(dbentries), group, filename)

    def getZenossDeviceRancidConfigs(self, root=None):
        """
        For all devices underneath the specified tree,
        create a mapping of the identifier to
        RANCID-specific device information.

        @parameter root: starting branch to examine (default /Devices)
        @type: string
        @returns: name or ip -> configs
        @rtype: dictionary
        """
        group_buckets = {}

        if root is None or root == '':
            root = self.dmd.Devices
        else:
            root = self.dmd.unrestrictedTraverse(root)

        for dev in root.getSubDevices():
            if not self.isRancidable(dev):
                log.info("Not adding %s (%s)", dev.id, dev.manageIp)
                continue

            if dev.zRancidGroup not in group_buckets:
                group_buckets[dev.zRancidGroup] = {}

            if dev.getPingStatus() == 0:
                status = 'up'
            else:
                # Note: 'up' is hardcoded by RANCID, but there
                #       can be other states other than 'down'
                #       For the moment, ignore this feature
                status = 'down'

            log.info("Added %s (%s) to %s with type: %s",
                dev.id, dev.manageIp, dev.zRancidGroup, dev.zRancidType)
            
            if self.options.nameInsteadOfIp:
                deviceKey = dev.id
            else:
                deviceKey = dev.manageIp
            
            group_buckets[dev.zRancidGroup][deviceKey] = dict(
                type=dev.zRancidType, status=status)
        return group_buckets

    def isRancidable(self, device):
        """
        Should this device participate in RANCID updates?
        """
        if getattr(device, 'zRancidType', '').strip() == '':
            return False

        if getattr(device, 'zRancidGroup', '').strip() == '':
            log.warn("%s has an empty zRancidGroup property", device.id)
            return False

        if getattr(device, 'productionState', -1) < 0:
            # No decommissioned devices
            return False

        return True

    def readRancidDb(self, dbfilename, dbentries):
        """
        Read the specfied router.db file and add in any entries
        from the router.db into the dictionary of already known
        devices.
        Don't remove any existing entries in the dbentries
        dictionary.

        The router.db file has lines of the following format:

        <device_name>:<device_type>:<state>[:comments]

        Complete description at:
        http://www.shrubbery.net/rancid/man/router.db.5.html

        @parameter dbfilename: path to the router.db file
        @type dbfilename: string
        @parameter dbentries: known device -> config mappings
        @type dbentries: dictionary
        """
        linesRead = 0
        rancid_db = open(dbfilename, 'r')
        for line in rancid_db:
            # Deliberately match commented out host entries
            data = [x.strip() for x in line.split(':')]
            if len(data) < 3:
                # Throw out trash entries
                continue

            linesRead += 1
            name, rType, status = data[:3]
            if name in dbentries:
                continue

            dbentries[name] = dict(type=rType, status=status)
            if len(data) == 4:
                dbentries[name]['comment'] = data[3]

        rancid_db.close()
        log.info("Read %d entries from %s", linesRead, dbfilename)

    def writeRancidDb(self, dbfilename, dbentries):
        """
        Write out the merged router.db file

        @parameter dbfilename: path to the router.db file
        @type dbfilename: string
        @parameter dbentries: known device -> config mappings
        @type dbentries: dictionary
        """
        # Sort entries by name
        entryList = sorted(dbentries.items(), key=operator.itemgetter(0))

        rancid_db = open(dbfilename, 'w')
        for deviceKey, entry in entryList:
            rancid_db.write("%s:%s:%s\n" % (
                deviceKey, entry['type'], entry['status']))

        rancid_db.close()
        log.info("Wrote %d entries to %s", len(entryList), dbfilename)


if __name__ == "__main__":
    u = ZenRancid()
    u.run()

