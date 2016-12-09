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
    def getRouters(self, name_instead_of_ip=False):    # noqa
        """Get rancid router.db file."""
        facade = self._getFacade()
        success, message = facade.getRouters(name_instead_of_ip)

        if success:
            return DirectResponse.succeed(result=message)
        else:
            return DirectResponse.fail(message)

    @serviceConnectionError
    def getBatchLoadFile(self, router_content, name_instead_of_ip):    # noqa
        """Export router.db file contents to batchload format string."""
        facade = self._getFacade()
        success, message = facade.getBatchLoadFile(
            router_content,
            name_instead_of_ip
        )

        if success:
            return DirectResponse.succeed(result=message)
        else:
            return DirectResponse.fail(message)
