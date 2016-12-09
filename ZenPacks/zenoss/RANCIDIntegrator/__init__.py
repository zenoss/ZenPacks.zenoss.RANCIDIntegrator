######################################################################
#
# Copyright 2007 Zenoss, Inc.  All Rights Reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
######################################################################

from Products.ZenModel.ZenPack import ZenPackBase


class ZenPack(ZenPackBase):

    packZProperties = [
        ('zRancidGroup', 'router', 'string'),
        ('zRancidType', 'cisco', 'string'),
    ]

    def install(self, app):
        ZenPackBase.install(self, app)

    def upgrade(self, app):
        ZenPackBase.upgrade(self, app)

    def remove(self, app, leaveObjects=False):
        ZenPackBase.remove(self, app, leaveObjects)
