# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_silvaviews.py,v 1.1 2005/05/04 15:41:54 jw Exp $

from __future__ import nested_scopes

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing.ZopeTestCase import Functional
    
import SilvaTestCase
from Testing.ZopeTestCase.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import utils

from StringIO import StringIO

import DateTime
now = DateTime.DateTime()


"""
SilvaViewsTest cases:


URLs and object paths that try to get to content through the 'edit'
view namespace of Silva shouldn't work.

These URLs and paths used to work in earlier versions of Silva, but
posed problems where content objects could 'override' views with the
same id.
    
To make matters worse, older Silva versions could build up path
references from Silva Documents to for example Silva Images, whith
repeating '[obj_id]/edit' segments (see the 'path' global used in the
test cases). These path references are used to 'restrictedTraverse()'
to objects.

These 'borked' paths and URLs appeared to work correctly, but only due
unwanted side effects and specific behaviour of Zope's acquisition.

The decision now is:

* URLs trying to get to content through the '.../edit' namespace
shouldn't work at all.

* Existing 'borked' URLs trying to get to content through the
'.../edit' namespace will not work anymore.
  
* Existing 'borked' paths trying to traverse to content through the
'.../edit' namespace will not work anymore.

To get the behaviour as described, MultiViewRegistry.get_method_onw_view()
has been modified: it will only return a view if this view is contained
in the service_views hierarchy. Thus, is not a n object that was retrieved,
by acquisistion, from on of service_views' parents.

"""


path =  (
    '/root/publication/folder'
    '/doc2/edit/doc2/edit/doc2/edit/doc2/edit/doc2/edit'
    '/doc2/edit/doc2/edit/doc2/edit/doc2/edit/doc2/edit'
    '/doc2/edit/doc2/edit/doc2/edit/doc2/edit/doc2/edit'
    '/testimage')
    
class SilvaViewsTest(Functional, SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        """Content tree:
        
        /publication
        /publication/folder
        /publication/folder/doc2
        /publication/testimage
        /doc
        
        """
        utils.setupCoreSessions(self.app)
        
        self.publication = self.add_publication(self.root, 'publication', u'Test Publication')
        self.folder = self.add_folder(self.publication, 'folder', u'Test Folder')
        self.doc = self.add_document(self.root, 'doc', u'Test Document')
        self.doc2 = self.add_document(self.folder, 'doc2', u'Test Document 2')
        self.doc.set_unapproved_version_publication_datetime(now)
        self.doc.approve_version()
        self.doc2.set_unapproved_version_publication_datetime(now)
        self.doc2.approve_version()
        
        image_file = open('data/testimage.gif', 'rb')
        image_data = image_file.read()
        image_file.seek(0)
        self.publication.manage_addProduct['Silva'].manage_addImage(
            'testimage', 'Test Image', image_file)
        image_file.close()
        self.image = self.root.publication.testimage

    def test_publish_through_borked_edit_url(self):
        # Before the SilvaViews fix, this would still not have worked anyway, 
        # because 'doc2' would not be found in the acq. context of the view.
        # After the fix, as per the behaviour as described above, it still
        # won't work.
        response = self.publish(path)
        self.assertEquals(404, response.getStatus())

    def test_traverse_through_borked_edit_path(self):
        # Before the SilvaViews fix, this would still not have worked anyway, 
        # because 'doc2' would not be found in the acq. context of the view.
        # After the fix, as per the behaviour as described above, it still
        # won't work.
        object = self.root.restrictedTraverse(path, None)
        self.assertEquals(None, object)
        
    def test_traverse_to_silvadocument_tab_metadata_view(self):
        # In an earlier attempt to get the described behaviour the
        # get_tabs script for Silva Documents could not be found anymore
        # from the tab_metadata template.
        # This test checks whether that specific situation does not occur
        # with the current fix anymore.
        uf = self.root.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        path = '/root/publication/folder/doc2/edit/tab_metadata'
        response = self.publish(path)
        self.assertEquals(401, response.getStatus())
        response = self.publish(path, basic='manager:r00t')
        self.assertEquals(200, response.getStatus())
        
class SilvaViewsTest2(SilvaViewsTest):

    def afterSetUp(self):
        """Content tree:
        
        /publication
        /publication/folder
        /publication/folder/doc2
        /publication/testimage
        /doc
        /doc2 # same name, different object, that used to make
              # 'borked' paths appear to work!
        
        """
        # Use content setup of base class
        SilvaViewsTest.afterSetUp(self)
        # Add the extra content object
        self.doc3 = self.add_document(self.root, 'doc2', u'Test Document 3')
        self.doc3.set_unapproved_version_publication_datetime(now)
        self.doc3.approve_version()

    def test_publish_through_borked_edit_url(self):
        # Before the SilvaViews fix, this would have worked because 'doc2'
        # would be found in the acq. context of the view - although it is
        # not actually a view.
        # After the fix, as per the behaviour as described above, it 
        # shouldn't work, because the view registry will check to see if
        # the 'view' found is contained in the service_views hierarchy.
        SilvaViewsTest.test_publish_through_borked_edit_url(self)

    def test_traverse_through_borked_edit_path(self):
        # Before the SilvaViews fix, this would have worked because 'doc2'
        # would be found in the acq. context of the view - although it is
        # not actually a view.
        # After the fix, as per the behaviour as described above, it 
        # shouldn't work, because the view registry will check to see if
        # the 'view' found is contained in the service_views hierarchy.
        SilvaViewsTest.test_traverse_through_borked_edit_path(self)
        
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SilvaViewsTest))
        suite.addTest(unittest.makeSuite(SilvaViewsTest2))
        return suite
