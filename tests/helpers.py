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

def approveObject(obj):
    """Publish object.
    """
    now = DateTime.DateTime()
    obj.set_unapproved_version_publication_datetime(now + 10)
    obj.approve_version()


def publishObject(obj):
    """Publish object.
    """
    now = DateTime.DateTime()
    obj.set_unapproved_version_publication_datetime(now - 10)
    obj.approve_version()


def publishApprovedObject(obj):
    """Publish the approved object.
    """
    now = DateTime.DateTime()
    obj.set_approved_version_publication_datetime(now - 10)


def openTestFile(path, mode='rb'):
    """Open the given test file.
    """
    directory = os.path.join(os.path.dirname(__file__), 'data')
    return open(os.path.join(directory, path), mode)
