# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

"""This module contains interfaces declaration for Silva services.
"""

from Products.Silva.i18n import translate as _

from zope import schema
from zope.interface import Interface
from grokcore.component.interfaces import IContext

class IZMIObject(IContext):
    """An object in ZMI.
    """

class IInvisibleService(Interface):
    """Marker interface for services that want to be not visible in
    the ZMI."""

class ISilvaService(IZMIObject):
    """Basic Silva service.
    """

class ISilvaLocalService(ISilvaService):
    """A Silva service which can be added in a local site.
    """

class IMemberService(ISilvaService):
    """Member service.
    """

    def find_members(search_string, location=None):
        """Return all users with a full name containing search string
        at the given position.
        """

    def is_user(userid, location=None):
        """Return true if userid is indeed a known user.
        """

    def get_member(userid, location=None):
        """Get member object for userid, or None if no such member
        object.
        """

    def get_cached_member(userid, location=None):
        """Get memberobject which can be cached, or None if no such
        memberobject.
        """

    def allow_authentication_requests():
        """Return true if authentication requests are allowed, false
        if not.
        """

    def get_authentication_requests_url():
        """Returns the url of the authentication_requests form
        """

    def get_extra_names():
        """Return list of names of extra information.
        """

    def logout(came_from=None, REQUEST=None):
        """Logout the current user.
        """

class IMessageService(ISilvaService):

    def send_message(from_memberid, to_memberid, subject, message):
        """Send a message from one member to another.
        """

    def send_pending_messages():
        """Send all pending messages.

        This needs to be called at the end of a request otherwise any
        messages pending may be lost.
        """

class ISidebarService(ISilvaService):

    def render(obj, tab_name):
        """Returns the rendered PT

        Checks whether the PT is already available cached, if so
        renders the tab_name into it and returns it, if not renders
        the full pagetemplate and stores that in the cache
        """

    def invalidate(obj):
        """Invalidate the cache for a specific object
        """

class IFilesService(ISilvaLocalService):

    storage = schema.Choice(title=_(u"Files Storage"),
                            description=_(u"Method used to store files"),
                            required=True,
                            vocabulary="File Storage Type")
