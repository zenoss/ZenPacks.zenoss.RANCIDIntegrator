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

   Implementation of this feature is as easy as adding a cronjob to execute
   ``$ZENHOME/Products/RANCIDIntegrator/bin/zenrancid.py`` as often as you'd
   like the ``router.db`` file to be updated.

#. Zenoss will automatically run RANCID's ``rancid-runm`` tool on a single
   device in response to a ``ciscoConfigManEvent`` SNMP trap being sent from
   the device to Zenoss. Cisco devices will send this trap whenever their
   configuration is change. This allows for real-time capturing of router
   configuration changes in your CVS repository.

   To implement this feature you must only configure your Cisco routers to
   send their SNMP traps to the Zenoss server.

#. Link from Cisco router device status pages to the most recent
   configuration stored in your CVS repository via viewvc
   (http://www.viewvc.org/).

   To implement this feature, change the ``zRancidUrl`` to your ``viewvc`` URL.

Prerequisites
===============================================================================

==================  =========================================================
Prerequisite        Restriction
==================  =========================================================
Product             Zenoss 4.1.1 or higher
Required ZenPacks   ``ZenPacks.zenoss.RANCIDIntegrator``
Other dependencies  Access to the RANCID versioned information
==================  =========================================================


Usage
===============================================================================
Other configuration options can be set using the following zProperties:

``zRancidRoot``
    File system directory where RANCID is installed. It may be NFS
    mounted from the real RANCID server. Default is ``/opt/rancid``

``zRancidUrl``
    Base URL to ``viewvc``.
    Default is http://rancid.mydomain.com/viewvc

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

 zenpack --install ZenPacks.zenoss.RANCIDIntegrator-2.1.5-py2.7.egg
 zenoss restart``

Removing
---------
To remove the ZenPack, use the following commands:

::

 zenpack --erase ZenPacks.zenoss.RANCIDIntegrator
 zenoss restart


Install RANCID locally on Zenoss master
========================================
This section describes briefly how to set up RANCID, and is not intended to be comprehensive
(for instance, only Subversion repositories are covered although CVS is also possible).

Pre-Requisites
------------------------------------------------------------------
Install Apache
******************************************************************
Apache ( http://subversion.tigris.org/ ) is used as the front-end for the RANCID system.  To install Apache on a ``yum``-based system:

::

  yum -y install httpd
  /etc/init.d/httpd start

If this has been installed correctly, you should be able to connect to port 80 and see the sample page.  If an Apache front-end has already been installed to act as an HTTPS proxy, then all that will be necessary is to adjust further configurations as appropriate.

Install Subversion
******************************************************************
The Subversion ( http://subversion.tigris.org/ ) revision tracking system allows for configuration changes to be tracked and the minimal changesets to be determined.  To install the Subversion system on a yum-based system:

::

  yum -y install subversion

.. note:
 The ``rancid-cvs`` command will create the SVN repository, so we don't need to manually create one.

Install Viewvc
******************************************************************

The viewvc ( http://www.viewvc.org/ ) system allows for a  graphical front-end to view Subversion (or CVS) repositories.

The following are instructions for RHEL 5 yum-based systems.

Add the required repository using the following commands as ``root``:

::

  mkdir /etc/yum/repos.d
  vi /etc/yum/repos.d/dries.repo

Provide the following content into the file:

::

  [repository]
  name=Dries RPM Repository
  baseurl=http://ftp.belnet.be/packages/dries.ulyssis.org/redhat/el4/en/i386/dries/RPMS
  gpgcheck=0
  enabled=1

And then finally install the software:

::

  yum -y install viewvc

Configure: Edit the viewvc and Apache Configuration Files, Test
------------------------------------------------------------------
Edit the ``/etc/viewvc/viewvc.conf`` file so that the following are not commented out (do not erase other content):


::

  svn_roots = svn: /opt/rancid/var/CVS
  default_root = svn

Now edit the Apache configuration ( ``vi /etc/httpd/conf.d/viewvc.conf`` ) to point to this new site area:

::

  ScriptAlias /viewvc /var/www/cgi-bin/viewvc.cgi
  ScriptAlias /query /var/www/cgi-bin/query.cgi
  Alias /viewvc-static /var/www/viewvc

  <Directory /var/www/viewvc>
        Allow from all
  </Directory>

Now restart the Apache server:

::

 /etc/init.d/httpd restart

To test the configuration, point your web browser to the following page:

::

 http://yourZenossServer/viewvc

The above URL is what should be set for the ``zRancidUrl`` zProperty.

Compile: Download and Compile RANCID
------------------------------------------------------------------

Since no RPM or ``yum`` packages exist, you will need to download, compile and install the package manually:

::

  yum -y install expect
  cd /opt  wget ftp://ftp.shrubbery.net/pub/rancid/rancid-2.3.8.tar.gz
  tar xzf rancid-2.3.8.tar.gz
  cd rancid-2.3.8
  ./configure --prefix=/opt/rancid
  make
  make install

This installs the package into the ``/opt/rancids`` directory, which is
the default expected by the ZenPack.  If your installation is set up to
a different directory, set the directory in the ``zRancidRoot`` Z-property.
Configure the permissions on the directories using the following commands:

::

  groupadd rancid
  usermod -a -G rancid apache
  usermod -a -G rancid zenoss
  chgrp -R rancid /opt/rancid

Configure: RANCID Configuration
------------------------------------------------------------------

Configure the RANCID system by editing the ``/opt/rancid/etc/rancid.conf`` file.  Make sure that the following are set:

::

  RCSSYS=svn; export RCSSYS
  LIST_OF_GROUPS="CORE_ROUTERS BGP_ROUTERS SWITCHES"

The group is an organizational structure, so the names should be meaningful
to your organization.  A Zenoss device needs to know which group it belongs
to in order to determine the path to the ``router.db`` file it will use.  Each
device must have the ``zRancidGroup`` Z-property set to one of the groups listed
in the ``LIST_OF_GROUPS`` variable in the ``rancid.conf`` file.

Now create the initial configuratiion database:

::

  /opt/rancid/bin/rancid-cvs

This creates a directory structure at ``/opt/rancid/var`` containing the
various groups and populates SVN with an initial import of the directories.
The group directories contain ``router.db`` files which contain a list of servers to gather configuration.

Now we will modify the ``router.db`` files so that the ``zenoss`` user can update the files.

::

  chmod g+w /opt/rancid/var/*/routers.db

The list of passwords that will be used in order to login to the devices must be set up
in the ``clogin.rc`` file.  There are examples in the ``/opt/rancid-2.3.8/cloginrc.sample`` file.
Create the file in the home directory of the user that will run the RANCID processes and owns
the configuration files.  In our example, this is the ``root`` user, so we would copy
the sample file and edit that as appropriate.

::

  cp  /opt/rancid-2.3.8/cloginrc.sample /root/clogin.rc
  vi /root/clogin.rc

Testing the ViewVC Configuration
------------------------------------------------------------------

To test the configuration, point your web browser to the following page:

http://yourZenossServer/viewvc

The above URL is what should be set for the ``zRancidUrl`` Z-property.

Configure: Set up Devices in Zenoss
------------------------------------------------------------------

As we set up devices in Zenoss, we need to set up these devices with the
approprate group (ie ``zRancidGroup`` ) and the appropriate device type
(ie ``zRancidType`` ).  The ``zRancidGroup`` Z-property determines which
``router.db`` file to update, and the ``zRancidType`` Z-property determines how
RANCID should communicate with the device.  The list of known device types
can be found at http://www.shrubbery.net/rancid/man/router.db.5.html page,
and this device-specific information must also match the ``zRancidType`` Z-property for the Zenoss device.

The ``zenracid --update`` command will update all of the ``router.db`` files in all
of the group directories, and the ``zenrancid`` command must be scheduled to keep
Zenoss and RANCID in sync.  Each ``router.db`` file contain the list of
devices which will have their configurations tracked in that group.

If you would like to verify what Zenoss is updating in the ``router.db`` file, each entry is a line with the following syntax:

::

 name_or_IP:device_type:up_or_down

Once a device is configured in Zenoss, the RANCID information can be seen by clicking on
the link at the bottom of the ``Overview`` page for the device.

Configure: Set up Cisco Devices to Send Traps
------------------------------------------------------------------
Zenoss will automatically run RANCID's ``rancid-runm`` tool on a single device
in response to a ``ciscoConfigManEvent`` SNMP trap being sent from the device to Zenoss.
Cisco devices will send this trap whenever their configuration is changed.

To update the event command used to reconfigure Zenoss:

#. Navigate to the ``Events`` top-level navigation item.
#. Navigate to the ``Triggers`` second-level navigation item.
#. Click on the ``Notification`` item from the left-hand pane..
#. Click on the ``rancid-run`` event command.
#. Click on the ``Contents`` tab.

Schedule: Gather Router Configuration Periodically
------------------------------------------------------------------
Set up a scheduled time to gather the network device configuration and keep
everything in sync between Zenoss and RANCID, as well as to make sure that RANCID
is updating itself.  This example gathers configuration information every hour.

::

  5 * * * * /opt/zenos/bin/zenrancid --update > /dev/null 2>&1
  10 * * * * /opt/rancid/bin/rancid-run > /dev/null 2>&1

.. note:
 The ``zenrancid`` command can be configured to update the ``router.db`` files with names rather than IP addresses by using the ``--name`` flag.

Integrate Zenoss with a Remote RANCID Instance
================================================

Check out the Source Repository
--------------------------------
We need to have a local copy of the RANCID configurations in order
to be in sync.

::

    mkdir -p /opt/rancid/var
    cdp /opt/rancid/var
    cvs checkout

To update the repository:

Allow Zenoss to Run Commands on the RANCID Server
----------------------------------------------------------------
The ``zenosss`` user on the Zenoss master must be able to run the ``rancid-run`` command
on the RANCID server.

::

    ssh rancidserver ls

Update the Notification Command
--------------------------------
Follow this procedure:

#. Navigate to the ``Events`` top-level navigation item.
#. Navigate to the ``Triggers`` second-level navigation item.
#. Click on the ``Notification`` item from the left-hand pane..
#. Click on the ``rancid-run`` event command.
#. Click on the ``Contents`` tab.
#. Update the ``Command`` field to run on the remote RANCID server. eg ``ssh rancidserver ${dev/zRancidRoot}/bin/rancid-run -r ${dev/manageIp} ${dev/zRancidGroup}``
#. Click on the ``Submit`` button to save the changes.

More Information
------------------------------------------------------------------
A detailed configuration example of RANCID can be found at:

http://www.linuxhomenetworking.com/wiki/index.php/Quick_HOWTO_\:_Ch1_\:_Network_Backups_With_Rancid

``zenrancid`` flags (from ``zenrancid --help``):

::

  --update              Update router.db instead of replacing it
  --name                Write device name instead of IP to router.db
  --dump2zb=DUMP2ZB     Read the specified router.db and dump to zenbatchload
                        format
  --zbfilename=ZBFILENAME
                        Write the router.db export into this file (default
                        /tmp/rancid_export.zenbatchload)

