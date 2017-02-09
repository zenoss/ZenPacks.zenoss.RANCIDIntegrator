===============================================================================
ZenPacks.zenoss.RANCIDIntegrator
===============================================================================

.. contents::

About
-------------------------------------------------------------------------------
The Really Awesome New Cisco config Differ (RANCID http://www.shrubbery.net/rancid )
toolset allows one to monitor the changes to different network device configurations.
Although the name has Cisco in it, this toolset can be used to monitor other network devices.


Features
===============================================================================
RANCIDIntegrator is a ZenPack designed to allow integration between the popular
RANCID (http://www.shrubbery.net/rancid/) tool and Zenoss. The integration
points between the tools can be described as following:

#. Zenoss will build the ``router.db`` file for RANCID. This allows for the
   centralization of administration activities and reduces the duplication
   of effort normally required to maintain the two tools.

   Implementation of this feature is as easy as adding a cronjob to hit a http
   endpoint to get router.db data

#. Zenoss will build the ``batchload`` file for ``router.db`` file. This allows
    back up devices across collectors.

Prerequisites
===============================================================================

==================  =========================================================
Prerequisite        Restriction
==================  =========================================================
Product             Zenoss 4.2.5 or higher
Required ZenPacks   ``ZenPacks.zenoss.RANCIDIntegrator``
Other dependencies  Access to the RANCID versioned information
==================  =========================================================


Usage
===============================================================================
Other configuration options can be set using the following zProperties:

``zRancidGroup``
    RANCID ``group`` attribute. Controls the ``router.db`` file to which
    the device information is written. Can be set at the device class or device
    level. Default is ``router`` on the ``/Network/Router/Cisco`` class.

``zRancidType``
    RANCID type attribute. Controls what device type is written to
    the ``router.db`` file. Can be set at the device class or device
    level. Default is ``cisco`` on the ``/Network/Router/Cisco`` class.


Installing
-----------
Install the ZenPack via the command line and restart Zenoss:

::

 zenpack --install ZenPacks.zenoss.RANCIDIntegrator-*.*.*-py2.7.egg
 zenoss restart

Removing
---------
To remove the ZenPack, use the following commands:

::

 zenpack --erase ZenPacks.zenoss.RANCIDIntegrator
 zenoss restart

Running
-------

To begin to work with RANCIDIntegrator please visit http://wiki.zenoss.org/Working_with_the_JSON_API

To get ``router.db`` file contents, run:

::

 zenoss_api rancidintegrator_router RANCIDIntegratorRouter getRouters '{"name_instead_of_ip": true}'

Response example:

::

{"uuid": "9ec44304-3ec2-41aa-adc7-b7d358084ea5", "action": "RANCIDIntegratorRouter", "result": {"result": {"router_db": "test_device2;cisco;down;localhost\ntest_device1;cisco;up;localhost\n", "batchload": "\"test_device2\" zRancidType=\"cisco\", setPerformanceMonitor=\"localhost\"\n\"test_device1\" zRancidType=\"cisco\", setPerformanceMonitor=\"localhost\"\n"}, "success": true}, "tid": 1, "type": "rpc", "method": "getRouters"}

The ``router.db`` content is accessible by ``router_db`` key.
The ``batchLoad`` content is accessible by ``batchLoad`` key.
