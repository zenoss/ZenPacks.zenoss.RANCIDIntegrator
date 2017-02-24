##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""RancidFacade tests."""


import unittest

from Products.Zuul.tests.base import ZuulFacadeTestCase

from ZenPacks.zenoss.RANCIDIntegrator.facade import RANCIDIntegratorFacade
from ZenPacks.zenoss.RANCIDIntegrator.interfaces import IRANCIDIntegratorFacade

from zope.interface.verify import verifyClass


class RancidFacadeTest(ZuulFacadeTestCase):
    """RancidFacade tests."""
    def afterSetUp(self):   # noqa
        super(RancidFacadeTest, self).afterSetUp()

        self.facade = RANCIDIntegratorFacade(self.dmd)

        self.dc = self.dmd.Devices.createOrganizer('/Network/Router/TestCisco')
        self.dc.setZenProperty('zRancidGroup', 'router')
        self.dc.setZenProperty('zRancidType', 'cisco')

        self.device1 = self.dc.createInstance("testDevice1")
        self.device1.setPerformanceMonitor('localhost')

        self.device2 = self.dc.createInstance("testDevice2")
        self.device2.setPerformanceMonitor('localhost')

    def test_getRouters(self):  # noqa
        response = self.facade.getRouters(name_instead_of_ip=True)
        self.assertEquals(
            response,
            (
                True,
                'testDevice1;cisco;up;localhost\ntestDevice2;cisco;up;localhost\n',
            )
        )

    def test_getBatchLoadFile(self):    # noqa
        response = self.facade.getBatchLoadFile(
            'testDevice1;cisco;up;localhost\ntestDevice2;cisco;up;localhost\n'
        )
        self.assertEquals(
            response,
            (
                True,
                '"testDevice1" zRancidType="cisco", setPerformanceMonitor="localhost"\n"testDevice2" zRancidType="cisco", setPerformanceMonitor="localhost"\n',
            )
        )

    def test_interfaces(self):
        verifyClass(IRANCIDIntegratorFacade, RANCIDIntegratorFacade)


def test_suite():
    return unittest.TestSuite((unittest.makeSuite(RancidFacadeTest),))


if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
