# Copyright (c) 2003-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from DateTime import DateTime
from Products.Silva.adapters.version_management import getVersionManagementAdapter
from StringIO import StringIO

now = DateTime()

class VersionManagementTestCase(SilvaTestCase.SilvaTestCase):
    """Test the version management adapter"""

    def afterSetUp(self):
        root = self.root
        root.manage_addProduct['SilvaDocument'].manage_addDocument('testdoc', 'TestDoc')
        doc = self.doc = root.testdoc
        # create a nice list of versions
        for i in range(10):
            id = str(i+1)
            doc.set_unapproved_version_publication_datetime(now)
            doc.approve_version()
            doc.close_version()
            doc.manage_addProduct['SilvaDocument'].\
                manage_addDocumentVersion(id, 'Version %s' % id)
            doc.create_version(id, None, None)

        self.adapter = getVersionManagementAdapter(doc)

    def beforeTearDown(self):
        pass

    def test_getVersionById(self):
        self.assertEquals(self.adapter.getVersionById('0'), getattr(self.doc, '0'))

    def test_getPublishedVersion(self):
        self.assertEquals(self.adapter.getPublishedVersion(), None)
        self.doc.set_unapproved_version_publication_datetime(now)
        self.doc.approve_version()
        self.assertEquals(self.adapter.getPublishedVersion().id, '10')

    def test_getUnapprovedVersion(self):
        self.assertNotEquals(self.doc.get_unapproved_version(), None)
        self.assertEquals(self.adapter.getUnapprovedVersion().id, '10')

    def test_getApprovedVersion(self):
        self.assertEquals(self.adapter.getApprovedVersion(), None)
        self.doc.set_unapproved_version_publication_datetime(now + 1)
        self.doc.approve_version()
        self.assertEquals(self.adapter.getApprovedVersion().id, '10')

    def test_revertEditableToOld(self):
        # publish the current editable
        self.doc.set_unapproved_version_publication_datetime(now)
        self.doc.approve_version()
        # create a new document
        self.doc.manage_addProduct['SilvaDocument'].manage_addDocumentVersion('11', 'someTitle')
        # add some content to the old doc so we can compare that to the new
        # one after reverting
        old_doc = getattr(self.doc, '9')
        old_doc.content.manage_edit('<doc>foobar</doc>')
        # since there are other tests to cover get*Version, we won't test if
        # the publish and create actions succeeded, let's assume they did,
        # we should now have an unapproved version 11 and a public 10
        # let's revert the editable to version 9, which would make editable
        # 9, public still 10 and the last closed (using the old API to get 
        # that) 11
        self.adapter.revertEditableToOld('9')
        self.assertEquals(self.adapter.getUnapprovedVersion().id, '12')
        self.assertEquals(self.adapter.getPublishedVersion().id, '10')
        org_content_buffer = StringIO()
        getattr(self.doc, '12').content.writeStream(org_content_buffer)
        org_content = org_content_buffer.getvalue()
        new_content_buffer = StringIO()
        getattr(self.doc, '9').content.writeStream(new_content_buffer)
        new_content = new_content_buffer.getvalue()
        self.assertEquals(org_content, new_content)

    def test_getVersionIds(self):
        ids = self.adapter.getVersionIds()
        ids.sort()
        self.assertEquals(ids,
                ['0', '1', '10', '2', '3', '4', '5', '6', '7', '8', '9'])

    def test_getVersions(self):
        def sort_strings_as_ints(a, b):
            return cmp(int(a), int(b))
        versionids = [o.id for o in self.adapter.getVersions()]
        versionids_zope = self.doc.objectIds('Silva Document Version')
        # if no argument is given, getVersions() sorts by id (int sort)
        versionids_zope.sort(sort_strings_as_ints)
        self.assertEquals(versionids, versionids_zope)

    def test_deleteVersion(self):
        self.adapter.deleteVersion('9')
        self.assert_('9' not in self.doc.objectIds('Silva Document Version'))

    def test_deleteOldVersions(self):
        # there should be 10 versions that *can* be deleted
        # first try to remove the last 2, so keep 8
        self.adapter.deleteOldVersions(8)
        objids = self.doc.objectIds('Silva Document Version')
        self.assertEquals(len(objids), 9)
        self.assert_('0' not in objids)
        self.assert_('1' not in objids)
        self.assert_('2' in objids)
        # now try to remove all versions that can be removed
        # in the end only 1 version must be kept (the current
        # unapproved)
        self.adapter.deleteOldVersions()
        objids = self.doc.objectIds('Silva Document Version')
        self.assertEquals(len(objids), 1)
        self.assertEquals(objids, ['10'])

if __name__ == '__main__':
    framework()
