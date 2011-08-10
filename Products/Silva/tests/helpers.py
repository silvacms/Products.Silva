# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os.path

from zope.interface import noLongerProvides, alsoProvides
from silva.core.views.interfaces import IPreviewLayer

import DateTime

def resetPreview(content):
    """Reset preview mode.
    """
    if IPreviewLayer.providedBy(content.REQUEST):
        noLongerProvides(content.REQUEST, IPreviewLayer)

def enablePreview(content):
    """Enable preview mode.
    """
    if not IPreviewLayer.providedBy(content.REQUEST):
        alsoProvides(content.REQUEST, IPreviewLayer)

def approve_content(obj):
    """Publish object.
    """
    now = DateTime.DateTime()
    obj.set_unapproved_version_publication_datetime(now + 10)
    obj.approve_version()


def publish_content(obj):
    """Publish object.
    """
    now = DateTime.DateTime()
    obj.set_unapproved_version_publication_datetime(now - 10)
    obj.approve_version()

def publish_approved_content(obj):
    """Publish the approved object.
    """
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
    if globs is None:
        testfile = __file__
    else:
        testfile = globs['__file__']
    return os.path.join(os.path.dirname(testfile), 'data', filename)

def open_test_file(filename, globs=None, mode='rb'):
    """Open the given test file.
    """
    try:
        fd = open(test_filename(filename, globs=globs), mode)
    except Exception:
        raise
    return fd

openTestFile = open_test_file
