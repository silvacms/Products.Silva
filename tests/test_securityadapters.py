# Copyright (c) 2003-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.5 $
import os, sys, time
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

from Products.Silva.adapters.interfaces import IViewerSecurity
from Products.Silva.adapters import security
from AccessControl.SecurityManagement import newSecurityManager

class ViewerSecurityTestCase(SilvaTestCase.SilvaTestCase):
    def test_defaultRoot(self):
        # by default, all viewer roles can view silva root
        self.assertEquals(
            'Anonymous',
            IViewerSecurity(self.root).getMinimumRole())

    def test_defaultAcquire(self):
        self.add_folder(self.root, 'test', 'Test')
        self.assertEquals(
            'Anonymous',
            IViewerSecurity(self.root.test).getMinimumRole())
        
    def test_setMinimumRole(self):
        viewer_security = IViewerSecurity(self.root)
        viewer_security.setMinimumRole('Viewer')
        self.assertEquals(
            'Viewer',
            viewer_security.getMinimumRole())

    def test_setMinimumRole2(self):
        viewer_security = IViewerSecurity(self.root)
        viewer_security.setMinimumRole('Viewer +')
        self.assertEquals(
            'Viewer +',
            viewer_security.getMinimumRole())
        
    def test_getDefaultMinimumRole(self):
        viewer_security = IViewerSecurity(self.root)
        self.assertEquals(
            'Anonymous',
            viewer_security.getMinimumRole())

    def test_acquireRestriction(self):
        # acquire restriction by default
        viewer_security = IViewerSecurity(self.root)
        viewer_security.setMinimumRole('Viewer')
        self.add_folder(self.root, 'test', 'Test')
        lower_viewer_security = IViewerSecurity(
            self.root.test)
        self.assertEquals(
            'Viewer',
            lower_viewer_security.getMinimumRole())

    def test_openRestricted(self):
        # it is possible to open a folder in a restricted area
        # further than would be possible according to acquisition
        self.add_folder(self.root, 'test', 'Test')
        viewer_security = IViewerSecurity(self.root)
        viewer_security.setMinimumRole('Viewer')
        lower_viewer_security = IViewerSecurity(
            self.root.test)
        lower_viewer_security.setMinimumRole('Authenticated')
        self.assertEquals(
            'Authenticated',
            lower_viewer_security.getMinimumRole())
        self.assert_(not lower_viewer_security.isAcquired())
        # but now we set it to acquire
        lower_viewer_security.setAcquired()
        self.assert_(lower_viewer_security.isAcquired())
        self.assertEquals('Viewer',
                          lower_viewer_security.getMinimumRole())

    def test_openRestrictedLower(self):
        # it is possible to open a folder in a restricted area
        # further than would be possible according to acquisition
        self.add_folder(self.root, 'alpha', 'Alpha')
        self.add_folder(self.root.alpha, 'beta', 'Beta')
        
        s_alpha = IViewerSecurity(self.root.alpha)
        s_alpha.setMinimumRole('Viewer')
        s_beta = IViewerSecurity(
            self.root.alpha.beta)
        s_beta.setMinimumRole('Authenticated')
        self.assertEquals(
            'Authenticated',
            s_beta.getMinimumRole())
        self.assert_(not s_beta.isAcquired())
        # but now we set it to acquire
        s_beta.setAcquired()
        self.assert_(s_beta.isAcquired())
        self.assertEquals('Viewer',
                          s_beta.getMinimumRole())

    def test_restrictAndOpenRoot(self):
        viewer_security = IViewerSecurity(self.root)
        viewer_security.setMinimumRole('Viewer')
        self.assertEquals('Viewer',
                          viewer_security.getMinimumRole())
        self.assert_(not viewer_security.isAcquired())
        viewer_security.setAcquired()
        self.assert_(viewer_security.isAcquired()) 
        self.assertEquals('Anonymous',
                          viewer_security.getMinimumRole())

    def test_restrictedAndOpenRoot2(self):
        viewer_security = IViewerSecurity(self.root)
        viewer_security.setMinimumRole('Viewer')
        self.assertEquals('Viewer',
                          viewer_security.getMinimumRole())
        self.assert_(not viewer_security.isAcquired())
        viewer_security.setMinimumRole('Anonymous')
        self.assert_(viewer_security.isAcquired()) 
        self.assertEquals('Anonymous',
                          viewer_security.getMinimumRole())

    def test_getMinimumRoleAbove(self):
        self.add_folder(self.root, 'alpha', 'Alpha')
        self.add_folder(self.root.alpha, 'beta', 'Beta')
        
        s_alpha = IViewerSecurity(self.root.alpha)
        s_alpha.setMinimumRole('Viewer')
        s_beta = IViewerSecurity(
            self.root.alpha.beta)
        self.assertEquals(s_beta.getMinimumRole(),
                          s_beta.getMinimumRoleAbove())
        self.assertEquals(s_beta.getMinimumRole(),
                          'Viewer')
        s_beta.setMinimumRole('Viewer +')
        self.assertEquals('Viewer +',
                          s_beta.getMinimumRole())
        self.assertEquals('Viewer',
                          s_beta.getMinimumRoleAbove())
                          

class LockSecurityTestCase(SilvaTestCase.SilvaTestCase):
    def test_startUnlocked(self):
        self.add_document(self.root, 'doc', 'Doc')
        adapter = security.getLockAdapter(self.root.doc)
        self.assert_(not adapter.isLocked())

    def test_isLocked(self):        
        self.add_document(self.root, 'doc', 'Doc')
        adapter = security.getLockAdapter(self.root.doc)
        self.assert_(adapter.createLock())
        # as we're the same user
        self.assert_(not adapter.isLocked())
        # log in as other user
        uf = self.root.acl_users
        uf._doAddUser('dummy', 'secret', ['Author'], [])
        user = uf.getUserById('dummy').__of__(uf)
        newSecurityManager(None, user)
        # should be locked now
        self.assert_(adapter.isLocked())
        # can't create lock
        self.assert_(not adapter.createLock())
        # break lock
        adapter.breakLock()
        self.assert_(not adapter.isLocked())
        # now can make lock
        self.assert_(adapter.createLock())
        # and we're not locked at the moment either
        self.assert_(not adapter.isLocked())
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ViewerSecurityTestCase))
        suite.addTest(unittest.makeSuite(LockSecurityTestCase))
        return suite
