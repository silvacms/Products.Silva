# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import interface


class IRegistry(interface.Interface):
    """An registry is a special utility which exists only in memory
    (it's not dump in the ZOBD).
    """


class IUpgradeRegistry(IRegistry):
    """It's a registry for upgrade purpose.
    """

    def registerUpgrader(upgrader, version=None, meta_type=None):
        pass

    def registerSetUp(function, version):
        pass

    def registerTearDown(function, version):
        pass

    def getUpgraders(version, meta_type):
        """Return the registered upgrade_handlers of meta_type
        """

    def upgradeObject(obj, version):
        pass

    def upgradeTree(root, version):
        """Upgrade a whole tree to version."""

    def upgrade(root, from_version, to_version):
        pass

    def setUp(root, version):
        pass

    def tearDown(root, version):
        pass
