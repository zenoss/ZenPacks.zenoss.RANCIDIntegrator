######################################################################
#
# Copyright 2007 Zenoss, Inc.  All Rights Reserved.
#
######################################################################

import Globals
from Products.ZenModel.ZenPack import ZenPackBase
from Products.CMFCore.DirectoryView import registerDirectory

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())


class ZenPack(ZenPackBase):
    """ RANCIDIntegrator loader
    """

    packZProperties = [
            ('zRancidRoot', '/opt/rancid', 'string'),
            ('zRancidUrl', 'http://rancid.mydomain.com/viewvc', 'string'),
            ('zRancidGroup', '', 'string'),
            ('zRancidType', '', 'string'),
            ]

    def install(self, app):
        ZenPackBase.install(self, app)
        self.setupZProperties(app)

    def upgrade(self, app):
        ZenPackBase.upgrade(self, app)
        self.setupZProperties(app)


    def setupZProperties(self, app):
        try:
            dc = app.zport.dmd.Devices.getOrganizer('Network/Router/Cisco')
        except AttributeError:
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
