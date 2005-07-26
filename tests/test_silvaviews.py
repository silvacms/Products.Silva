# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_silvaviews.py,v 1.3 2005/07/26 20:36:37 walco Exp $

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
view namespace of Silva shouldn't work, but they do.

These URLs and paths have historically worked in Silva, but pose
problems where content objects could 'override' views with the same
id.
    
To make matters worse, older Silva versions could build up path
references from Silva Documents to for example Silva Images, whith
repeating '[obj_id]/edit' segments (see the 'path' global used in the
test cases). These path references are used to 'restrictedTraverse()'
to objects.

These 'borked' paths and URLs appear to work correctly, but only due
unwanted side effects and specific behaviour of Zope's acquisition.

Unfortunately, changing the behavior of Silva right now breaks too
much to be a sensible change. We've tried various strategies, but decided it
was too complicated. We've since decided to go back to the behavior as
it is now, and codify this in a set of tests.

In an ideal world, we might instead do something like this:

* URLs trying to get to content through the '.../edit' namespace
shouldn't work at all.

* Existing 'borked' URLs trying to get to content through the
'.../edit' namespace will not work anymore.
  
* Existing 'borked' paths trying to traverse to content through the
'.../edit' namespace will not work anymore.

This could be accomplished by modifying
MultiViewRegistry.get_method_onw_view() so that it will only return a
view if this view is contained in the service_views hierarchy. Thus,
is not an object that was retrieved, by acquisistion, from on of
service_views' parents. To repeat: we haven't actually done this.
"""

directory = os.path.dirname(__file__)

# a very long path string
path =  (
    '/root/publication/folder'
    '/doc2/edit/doc2/edit/doc2/edit/doc2/edit/doc2/edit'
    '/doc2/edit/doc2/edit/doc2/edit/doc2/edit/doc2/edit'
    '/doc2/edit/doc2/edit/doc2/edit/doc2/edit/doc2/edit'
    '/testimage')
    
path_to_nonexisting_content = (
    '/root/publication/folder'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
    '/index/edit/index/edit/index/edit/index/edit/index/edit'
     '/testimag')
 
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
        
        image_file = open(os.path.join(directory, 'data/testimage.gif'), 'rb')
        image_data = image_file.read()
        image_file.seek(0)
        self.publication.manage_addProduct['Silva'].manage_addImage(
            'testimage', 'Test Image', image_file)
        image_file.close()
        self.image = self.root.publication.testimage

    def test_publish_through_borked_edit_url(self):
        response = self.publish(path)
        self.assertEquals(200, response.getStatus())
        # in a hypothetical situation where we'd have made the change,
        # we would've tested for 404.
        
    def test_traverse_through_borked_edit_path(self):
        object = self.root.restrictedTraverse(path, None)
        self.assertEquals('testimage', object.id)
        # In the ideal situation, this would result in None instead

    def test_traverse_through_borked_edit_path_to_nonexisting_content(self):
        object = self.root.restrictedTraverse(path_to_nonexisting_content, None)
        self.assertEquals(None, object)

    def test_publish_nonexisting_content(self):
        uf = self.root.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        response = self.publish(path_to_nonexisting_content, basic='manager:rOOt')
        self.assertEquals(404, response.getStatus())
        
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
        SilvaViewsTest.test_publish_through_borked_edit_url(self)

    def test_traverse_through_borked_edit_path(self):
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
