# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os.path
import DateTime
import warnings


def approve_content(obj):
    """Publish object.
    """
    warnings.warn(u'Please use directly the IPublicationWorkflow adapter')
    now = DateTime.DateTime()
    obj.set_unapproved_version_publication_datetime(now + 10)
    obj.approve_version()

def publish_content(obj):
    """Publish object.
    """
    warnings.warn(u'Please use directly the IPublicationWorkflow adapter')
    now = DateTime.DateTime()
    obj.set_unapproved_version_publication_datetime(now - 10)
    obj.approve_version()

def publish_approved_content(obj):
    """Publish the approved object.
    """
    warnings.warn(u'Please use directly the IPublicationWorkflow adapter')
    now = DateTime.DateTime()
    obj.set_approved_version_publication_datetime(now - 10)

# We are going to convert all API not to use camelcase anymore.
publish_object = publish_content
publishObject = publish_content
approveObject = approve_content
approve_object = approve_content
publishApprovedObject = publish_approved_content

def test_filename(filename, globs=None):
    """Return the filename of a test file.
    """
    warnings.warn(u'This method will be removed. Please use open_test_file')
    if globs is None:
        testfile = __file__
    else:
        testfile = globs['__file__']
    return os.path.join(os.path.dirname(testfile), 'data', filename)

def open_test_file(filename, globs=None, mode='rb'):
    """Open the given test file.
    """
    if globs is None:
        base_path = os.path.dirname(__file__)
    else:
        base_path = os.path.dirname(globs['__file__'])
    filename = os.path.join(base_path, 'data', filename)
    return open(filename, mode)


openTestFile = open_test_file
