# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import SilvaTestCase
from Testing.ZopeTestCase.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import utils

from StringIO import StringIO

from Products.Silva import File

class QuotaTest(SilvaTestCase.SilvaTestCase):
    """Test quota implementation.
    """

    def _enable_quota(self):
        self.root.service_extensions.enable_quota_subsystem()
        
    def test_counting(self):
        self._enable_quota()
        # TODO

    def test_quota(self):
        self._enable_quota()
        # TODO

    def test_extension(self):
        s_ext = self.root.service_extensions
        self.failIf(s_ext.get_quota_subsystem_status(),
                    "Quota should be disable by default")
        s_ext.enable_quota_subsystem()
        self.failUnless(s_ext.get_quota_subsystem_status())
        s_ext.disable_quota_subsystem()
        self.failIf(s_ext.get_quota_subsystem_status())
   
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuotaTest))
    return suite
