######################################################################
#
# Copyright 2007 Zenoss, Inc.  All Rights Reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
######################################################################

import os

import Globals
from Products.ZenModel.ZenPack import ZenPackBase
from Products.ZenUtils.Utils import zenPath


class ZenPack(ZenPackBase):

    packZProperties = [
            ('zRancidRoot', '/opt/rancid', 'string'),
            ('zRancidUrl', 'http://rancid.example.com/viewvc', 'string'),
            ('zRancidGroup', '', 'string'),
            ('zRancidType', '', 'string'),
            ]

    def install(self, app):
        ZenPackBase.install(self, app)
        self.setupZProperties(app)
        self.symlinkScript()

    def upgrade(self, app):
        ZenPackBase.upgrade(self, app)
        self.setupZProperties(app)
        self.symlinkScript()
    
    def remove(self, app, leaveObjects=False):
        self.removeScriptSymlink()
        ZenPackBase.remove(self, app, leaveObjects)

    def setupZProperties(self, app):
        try:
            dc = app.zport.dmd.Devices.getOrganizer('Network/Router/Cisco')
        except (AttributeError, KeyError):
            return

        if not dc.hasProperty('zRancidGroup'):
            dc._setProperty('zRancidGroup', 'router')

        if not dc.hasProperty('zRancidType'):
            dc._setProperty('zRancidType', 'cisco')

        rancid_link = '<a href="${here/zRancidUrl}/${here/zRancidGroup}/configs/${here/manageIp}?root=CVS&view=markup" target="_">RANCID</a>'
        orig_zlinks = dc.zLinks
        if orig_zlinks.find('RANCID') >= 0: return
        if dc.hasProperty('zLinks'):
            dc.zLinks = dc.zLinks + ' | ' + rancid_link
        else:
            dc._setProperty('zLinks', rancid_link)

    def symlinkScript(self):
        os.system('ln -sf %s/zenrancid %s/' %
            (self.path('bin'), zenPath('bin')))
    
    def removeScriptSymlink(self):
        os.system('rm -f %s/zenrancid' % (zenPath('bin')))
