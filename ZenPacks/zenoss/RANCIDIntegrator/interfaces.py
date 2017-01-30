##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""RANCIDIntegrator interface(s)."""

from Products.Zuul.interfaces import IFacade


class IRANCIDIntegratorFacade(IFacade):
    """Facade iface."""

    def getRouters(self, name_instead_of_ip):    # noqa
        """Get rancid router.db file."""

    def is_rancidable(self, device):
        """Check if device has RANCID zProps."""

    def get_rancid_configs(self, name_instead_of_ip, root=None):
        """Get a mapping of devices which are 'is_rancidable'."""

    def get_rancid_db(self, name_instead_of_ip):   # noqa
        """Return string which loolks like rancid router.db file contents."""

    def export_to_batchload(self, router_content):     # noqa
        """Get router.db file content and return batchload format string."""

    def getBatchLoadFile(self, router_content):    # noqa
        """Export router.db file contents to batchload format string."""
