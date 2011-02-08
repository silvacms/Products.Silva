# Copyright (c) 2003-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id $

# Python
from StringIO import StringIO
from datetime import datetime, timedelta
import unittest

from DateTime import DateTime

from Products.Silva.Versioning import VersioningError
from Products.Silva.adapters.version_management import \
    getVersionManagementAdapter
from Products.Silva.tests import SilvaTestCase

now = DateTime()


class VersionManagementTestCase(SilvaTestCase.SilvaTestCase):
    """Test the version management adapter"""

    def afterSetUp(self):
        self.add_document(self.root, 'testdoc', 'TestDoc')
        self.doc = self.root.testdoc
        # create some versions
        for i in range(10):
            self.create_version()
        self.adapter = getVersionManagementAdapter(self.doc)

    def create_version(self):
        doc = self.doc
        if doc._unapproved_version[0] is not None:
            doc.set_unapproved_version_publication_datetime(now)
            doc.approve_version()
            doc.close_version()
        id = doc.get_new_version_id()
        doc.manage_addProduct['SilvaDocument'].\
            manage_addDocumentVersion(id, 'Version %s' % id)
        doc.create_version(id, None, None)

    def test_getVersionById(self):
        self.assertEquals(
            self.adapter.getVersionById('0'),
            getattr(self.doc, '0'))

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

    def test_revertPreviousToEditable(self):
        # publish the current editable
        self.doc.set_unapproved_version_publication_datetime(now)
        self.doc.approve_version()
        # create a new version
        self.create_version()
        # add some content to the old doc so we can compare that to the new
        # one after reverting
        old_doc = getattr(self.doc, '9')
        old_doc.content.manage_edit('<doc>foobar</doc>')
        # Since there are other tests to cover get*Version, we won't test if
        # the publish and create actions succeeded, let's assume they did.
        #
        # We should now have an unapproved version 11 and a public version 10.
        #
        # Let's revert previous version 9 to editable, which would make
        # editable version 12, public still is version 10 and the last
        # closed is version 11.
        self.adapter.revertPreviousToEditable('9')
        self.assertEquals(self.adapter.getUnapprovedVersion().id, '12')
        self.assertEquals(self.adapter.getPublishedVersion().id, '10')
        org_content_buffer = StringIO()
        getattr(self.doc, '12').content.writeStream(org_content_buffer)
        org_content = org_content_buffer.getvalue()
        new_content_buffer = StringIO()
        getattr(self.doc, '9').content.writeStream(new_content_buffer)
        new_content = new_content_buffer.getvalue()
        self.assertEquals(org_content, new_content)
        # We now have a unapproved (editable) version.
        # Let's request approval for it, which should put it in pending
        # state in turn result in an error raised.
        self.doc.request_version_approval('foo bar')
        self.assertRaises(
            VersioningError, self.adapter.revertPreviousToEditable, '8')
        # Now approve the editable version, without yet publishing it. This
        # should result in an error raised too when trying to revert.
        # To do this, we first need to close the currently published version
        # and reject the approval request.
        self.doc.close_version()
        self.doc.reject_version_approval('baz qux')
        self.doc.set_unapproved_version_publication_datetime(now + 1)
        self.doc.approve_version()
        self.assertRaises(
            VersioningError, self.adapter.revertPreviousToEditable, '7')

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

    def test_deleteVersions(self):
        self.adapter.deleteVersions(['0', '1'])
        self.assert_('0' not in self.adapter.getVersionIds())
        self.assert_('1' not in self.adapter.getVersionIds())

        # test a delete of a set of documents of which one can't be
        # deleted (published)
        self.doc.set_unapproved_version_publication_datetime(DateTime())
        self.doc.approve_version()
        published_id = self.adapter.getPublishedVersion().id
        self.assertEquals(published_id, '10')

        ids = self.adapter.getVersionIds()
        self.assert_('10' in ids)
        self.assert_('9' in ids)
        self.adapter.deleteVersions(['9', '10'])
        ids = self.adapter.getVersionIds()
        self.assert_('10' in ids)
        self.assert_('9' not in ids)

    def test_deleteVersions_catalog(self):
        #make sure unpublished versions are removed from the catalog
        query = {'meta_type': 'Silva Document Version',
                 'version_status': 'unapproved'}
        #there should only be one version in the catalog, the last
        # version, which happens to be unpublished
        current = self.catalog(query)
        self.assertEquals(len(current),1)
        version = current[0].getObject()
        content = version.get_content()
        self.assertEquals(version.id,content.get_unapproved_version())
        self.adapter.deleteVersions([version.id])
        #there should be no versions in the catalog
        current = self.catalog(query)
        self.assertEquals(len(current),0)


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

    def _setupModificationTimes(self):
        versions = self.adapter.getVersions()
        versions.reverse()
        then = datetime.now()
        for version in versions:
            then -= timedelta(days=1)
            moddate = DateTime(then.isoformat())
            binding = self.doc.service_metadata.getMetadata(version)
            binding.setValues('silva-extra', {'modificationtime': moddate}, 0)

    def test_deleteOldVersionsByAge1(self):
        self._setupModificationTimes()
        max_age = 5
        self.adapter.deleteOldVersionsByAge(max_age)
        self.assertEquals(
            ['6', '7', '8', '9', '10'],
            self.doc.objectIds('Silva Document Version'))

    def test_deleteOldVersionsByAge2(self):
        self._setupModificationTimes()
        max_age = 5
        max_to_keep = 8
        self.adapter.deleteOldVersionsByAge(max_age, max_to_keep)
        self.assertEquals(
            ['6', '7', '8', '9', '10'],
            self.doc.objectIds('Silva Document Version'))

    def test_deleteOldVersionsByAge3(self):
        self._setupModificationTimes()
        max_age = 5
        max_to_keep = 2
        self.adapter.deleteOldVersionsByAge(max_age, max_to_keep)
        self.assertEquals(
            ['8', '9', '10'],
            self.doc.objectIds('Silva Document Version'))

    # catalog tests, see if the adapter methods that change
    # workflow in some way result in correct catalog changes
    def test_revertPreviousToEditable_catalog(self):
        # queries for the interesting versions
        query_editable = {'meta_type': 'Silva Document Version',
                            'version_status': 'unapproved'}
        query_public = {'meta_type': 'Silva Document Version',
                            'version_status': 'public'}

        # little sanity check
        current_editables = self.doc.service_catalog(query_editable)
        self.assertEquals(len(current_editables), 1)
        self.assertEquals(current_editables[0].id, '10')

        current_public = [b for b in
                            self.doc.service_catalog(query_public) if
                            b.getObject().get_content().id == 'testdoc']
        self.assertEquals(len(current_public), 0)

        # make sure there's a published version and an editable one
        self.doc.set_unapproved_version_publication_datetime(DateTime())
        self.doc.approve_version()
        self.create_version()

        # now get the ids of the current editable and public
        current_editable = self.doc.service_catalog(query_editable)
        self.assertEquals(len(current_editable), 1)
        self.assertEquals(current_editable[0].id, '11')

        current_public = [b for b in
                            self.doc.service_catalog(query_public) if
                            b.getObject().get_content().id == 'testdoc']
        self.assertEquals(len(current_public), 1)
        self.assertEquals(current_public[0].id, '10')

        # revert editable to some old version
        self.adapter.revertPreviousToEditable('4')

        # get the ids of the current editable and public again
        current_editable = self.doc.service_catalog(query_editable)
        self.assertEquals(len(current_editable), 1)
        self.assertEquals(current_editable[0].id, '12')

        current_public = [b for b in
                            self.doc.service_catalog(query_public) if
                            b.getObject().get_content().id == 'testdoc']
        self.assertEquals(len(current_public), 1)
        self.assertEquals(current_public[0].id, '10')

    # XXX Integrity checks, these will fail as soon as something
    # in the underlying implementation changes
    def test_deleteVersions_integrity(self):
        self.adapter.deleteVersions(['9'])
        self.assertEquals(self.doc.get_last_closed_version(), '8')
        self.assertEquals(len(self.doc._previous_versions), 9)

    def test_revertPreviousToEditable_integrity(self):
        # publish the current editable
        self.doc.set_unapproved_version_publication_datetime(now)
        self.doc.approve_version()
        # create a new version
        self.create_version()
        # add some content to the old doc so we can compare that to the new
        # one after reverting
        old_doc = getattr(self.doc, '9')
        old_doc.content.manage_edit('<doc>foobar</doc>')
        # revert to some old version
        self.adapter.revertPreviousToEditable('9')

        # test the VersionedContent object's attributes
        self.assert_(self.doc._unapproved_version[0] is not None)
        self.assert_(self.doc._approved_version[0] is None)
        self.assert_(self.doc._public_version[0] is not None)
        self.assert_(len(self.doc._previous_versions) == 11)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersionManagementTestCase))
    return suite

