##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Api.py."""

import logging

from Products.ZenUtils.Ext import (
    DirectResponse,
    DirectRouter
)
from Products.Zuul import getFacade

from Products.Zuul.decorators import serviceConnectionError


log = logging.getLogger("zen.rancid")


class RANCIDIntegratorRouter(DirectRouter):
    """Rancid router."""

    def _getFacade(self):   # noqa
        return getFacade('rancidintegrator', self.context)

    @serviceConnectionError
    def getRouters(self, name_instead_of_ip):    # noqa
        """Get rancid router.db file."""
        facade = self._getFacade()
        success, message = facade.getRouters(name_instead_of_ip)

        if success:
            return DirectResponse.succeed(result=message)
        else:
            return DirectResponse.fail(message)
