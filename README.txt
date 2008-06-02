RANCIDIntegrator
----------------

RANCIDIntegrator is a ZenPack designed to allow integration between the popular
RANCID (http://www.shrubbery.net/rancid/) tool and Zenoss. The integration
points between the tools can be described as following:

    1. Zenoss will build the router.db file for RANCID. This allows for the
       centralization of administration activities and reduces the duplication
       of effort normally required to maintain the two tools.

       Implementation of this feature is as easy as adding a cronjob to execute
       $ZENHOME/Products/RANCIDIntegrator/bin/zenrancid.py as often as you'd
       like the router.db file to be updated.


    2. Zenoss will automatically run RANCID's rancid-runm tool on a single
       device in response to a ciscoConfigManEvent SNMP trap being sent from
       the device to Zenoss. Cisco devices will send this trap whenever their
       configuration is change. This allows for real-time capturing of router
       configuration changes in your CVS repository.

       To implement this feature you must only configure your Cisco routers to
       send their SNMP traps to the Zenoss server.


    3. Link from Cisco router device status pages to the most recent
       configuration stored in your CVS repository via viewvc
       (http://www.viewvc.org/).

       To implement this feature, change the zRancidUrl to your viewvc URL.


Other configuration options can be set using the following zProperties:

    zRancidRoot: File system directory where RANCID is installed. It may be NFS
                 mounted from the real RANCID server. Default is "/opt/rancid"

    zRancidUrl: Base URL to viewvc.
                Default is http://rancid.mydomain.com/viewvc

    zRancidGroup: RANCID group attribute. Controls what router.db file the
                  device is written to. Can be set at the device class or device
                  level. Default is "router" on the /Network/Router/Cisco class.

    zRancidType: RANCID type attribute. Controls what device type is written to
                 the router.db file. Can be set at the device class or device
                 level. Default is "cisco" on the /Network/Router/Cisco class.


