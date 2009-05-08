# Copyright (c) 2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from unittest import TestCase

# Zope
from zope.interface.verify import verifyObject

# Silva
from silva.core.interfaces import IUpgradeRegistry
from Products.Silva import upgrade

import SilvaTestCase


class UpgradeUtilitiesTestCase(TestCase):
    """Test utilities which determines which version step should be
    run.
    """

    def setUp(self):
        self.versions = ['1.2', '1.4', '1.5a1', '1.5b2', '1.6a2', '2.0', '2.0.1', '2.1.3.4', '2.2', '2.3']

    def test_get_version_index(self):
        versions = self.versions
        self.assertEquals(upgrade.get_version_index(versions, '1.5a1'), 3)
        self.assertEquals(upgrade.get_version_index(versions, '1.7b2dev-r3456'), 5)
        self.assertEquals(upgrade.get_version_index(versions, '2.0'), 6)
        self.assertEquals(upgrade.get_version_index(versions, '2.0.0'), 6)
        self.assertEquals(upgrade.get_version_index(versions, '2.1'), 7)
        self.assertEquals(upgrade.get_version_index(versions, '2.2dev-r3458'), 9)
        self.assertEquals(upgrade.get_version_index(versions, '2.3'), 10)
        self.assertEquals(upgrade.get_version_index(versions, '2.4'), 10)

    def test_get_upgrade_chain(self):
        versions = self.versions
        self.assertEquals(upgrade.get_upgrade_chain(versions, '1.3', '2.0'), ['1.4', '1.5a1', '1.5b2', '1.6a2', '2.0'])
        self.assertEquals(upgrade.get_upgrade_chain(versions, '1.5', '2.0'), ['1.6a2', '2.0'])
        self.assertEquals(upgrade.get_upgrade_chain(versions, '1.7', '1.9'), [])
        self.assertEquals(upgrade.get_upgrade_chain(versions, '2.1dev-r5678', '2.4'), ['2.1.3.4', '2.2', '2.3',])
        self.assertEquals(upgrade.get_upgrade_chain(versions, '2.2', '2.3'), ['2.3',])


class UpgradeTestCase(SilvaTestCase.SilvaTestCase):
    """Test for the upgrade machinery.
    """

    def test_upgrade_registry(self):
        verifyObject(IUpgradeRegistry, upgrade.registry)


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UpgradeUtilitiesTestCase))
    suite.addTest(unittest.makeSuite(UpgradeTestCase))
    return suite
