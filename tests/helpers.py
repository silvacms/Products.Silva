# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import noLongerProvides, alsoProvides
from silva.core.views.interfaces import IPreviewLayer

import os.path
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

def approve_object(obj):
    """Publish object.
    """
    now = DateTime.DateTime()
    obj.set_unapproved_version_publication_datetime(now + 10)
    obj.approve_version()


def publish_object(obj):
    """Publish object.
    """
    now = DateTime.DateTime()
    obj.set_unapproved_version_publication_datetime(now - 10)
    obj.approve_version()

# We are going to convert all API not to use camelcase anymore.
publishObject = publish_object
approveObject = approve_object

def publishApprovedObject(obj):
    """Publish the approved object.
    """
    now = DateTime.DateTime()
    obj.set_approved_version_publication_datetime(now - 10)


def open_test_file(path, mode='rb'):
    """Open the given test file.
    """
    directory = os.path.join(os.path.dirname(__file__), 'data')
    return open(os.path.join(directory, path), mode)


openTestFile = open_test_file
