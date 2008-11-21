# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import md5
import time, datetime

# Zope 2
import Globals
import Acquisition
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo, allow_module
from BTrees.OOBTree import OOBTree

# Silva
from Products.Silva import interfaces
from Products.Silva import SilvaPermissions

from five import grok

TIMEOUTINDAYS =  3

NOT_SUBSCRIBABLE = 0
SUBSCRIBABLE = 1
ACQUIRE_SUBSCRIBABILITY = 2

from zope.interface import implements

class Subscription(object):

    grok.implements(interfaces.ISubscription)

    def __init__(self, emailaddress, contentsubscribedto):
        self._emailaddress = emailaddress
        self._contentsubscribedto = contentsubscribedto

    def emailaddress(self):
        return self._emailaddress

    def contentSubscribedTo(self):
        return self._contentsubscribedto

class Subscribable(Acquisition.Explicit, grok.Adapter):
    """Subscribable adapters potentially subscribable content and container
    Silva objects and encapsulates the necessary API for
    handling subscriptions.
    """

    grok.context(interfaces.IVersionedContent)
    grok.implements(interfaces.ISubscribable)
    grok.provides(interfaces.ISubscribable)

    security = ClassSecurityInfo()

    def __init__(self, context):
        super(Subscribable, self).__init__(context)
        if not hasattr(context, '__subscribability__'):
            context.__subscribability__ = ACQUIRE_SUBSCRIBABILITY
        if not hasattr(context, '__subscriptions__'):
            context.__subscriptions__ = OOBTree()
        if not hasattr(context, '__pending_subscription_tokens__'):
            context.__pending_subscription_tokens__ = OOBTree()

    # ACCESSORS FOR UI

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'isSubscribable')
    def isSubscribable(self):
        if self.context.__subscribability__ == NOT_SUBSCRIBABLE:
            return False
        subscribables = self._buildSubscribablesList()
        return bool(subscribables)

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'subscribability')
    def subscribability(self):
        return self.context.__subscribability__

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'getSubscribedEmailaddresses')
    def getSubscribedEmailaddresses(self):
        emailaddresses = list(self.context.__subscriptions__.keys())
        return emailaddresses

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'getSubscriptions')
    def getSubscriptions(self):
        return self._getSubscriptions().values()

    def _getSubscriptions(self):
        if self.context.__subscribability__ == NOT_SUBSCRIBABLE:
            return {}
        subscriptions = {}
        subscribables = self._buildSubscribablesList()
        for subscribable in subscribables:
            for emailaddress in subscribable.getSubscribedEmailaddresses():
                if not subscriptions.has_key(emailaddress):
                    subscriptions[emailaddress] = Subscription(
                        emailaddress, self.context)
        return subscriptions

    def _buildSubscribablesList(self, subscribables=None, marker=0):
        if subscribables is None:
            subscribables = []
        if self.context.__subscribability__ == NOT_SUBSCRIBABLE:
            # Empty list from the point without explicit subscribability onwards.
            del subscribables[marker:]
            return subscribables
        subscribables.append(self)
        if self.context.__subscribability__ == SUBSCRIBABLE:
            # Keep a marker for the object with explicit subscribability set.
            marker = len(subscribables)
        # Use aq_inner first, to unwrap the adapter-containment.
        parent = self.context.aq_inner.aq_parent
        subscr = getSubscribable(parent)
        return subscr._buildSubscribablesList(subscribables, marker)

    security.declarePrivate('isValidSubscription')
    def isValidSubscription(self, emailaddress, token):
        return self._validate(emailaddress, token)

    security.declarePrivate('isValidCancellation')
    def isValidCancellation(self, emailaddress, token):
        return self._validate(emailaddress, token)

    security.declarePrivate('isSubscribed')
    def isSubscribed(self, emailaddress):
        subscriptions = self.context.__subscriptions__
        return bool(subscriptions.has_key(emailaddress))

    security.declarePrivate('getSubscription')
    def getSubscription(self, emailaddress):
        subscriptions = self._getSubscriptions()
        return subscriptions.get(emailaddress, None)

    # MODIFIERS

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'setSubscribability')
    def setSubscribability(self, flag):
        self.context.__subscribability__ = flag

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'subscribe')
    def subscribe(self, emailaddress):
        subscriptions = self.context.__subscriptions__
        subscriptions[emailaddress] = None

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'unsubscribe')
    def unsubscribe(self, emailaddress):
        subscriptions = self.context.__subscriptions__
        if subscriptions.has_key(emailaddress):
            del subscriptions[emailaddress]

    security.declarePrivate('generateConfirmationToken')
    def generateConfirmationToken(self, emailaddress):
        tokens = self.context.__pending_subscription_tokens__
        timestamp = time.time()
        token = self._generateToken(emailaddress, '%f' % timestamp)
        tokens[emailaddress] = (timestamp, token)
        return token

    def _generateToken(self, *args):
        s = md5.new()
        for arg in args:
            s.update(arg)
        return s.hexdigest()

    def _validate(self, emailaddress, token):
        # The current implementation will keep items in the
        # pending list indefinitly if _validate is not called (end user
        # doesn't follow up on confirmantion email), or _validate is called,
        # but the supplied token is not valid.
        tokens = self.context.__pending_subscription_tokens__
        timestamp, validation_token = tokens.get(emailaddress,(None, None))
        if timestamp is None or validation_token is None:
            return False
        now = datetime.datetime.now()
        then = datetime.datetime.fromtimestamp(timestamp)
        delta = now - then
        if delta.days > TIMEOUTINDAYS:
            del tokens[emailaddress]
            return False
        if token == validation_token:
            del tokens[emailaddress]
            return True
        return False

Globals.InitializeClass(Subscribable)


class SubscribableContainer(Subscribable):
    """Subscribable container.
    """

    grok.context(interfaces.IContainer)


class SubscribableRoot(Subscribable):

    grok.context(interfaces.IRoot)

    def __init__(self, context):
        if not hasattr(context, '__subscribability__'):
            context.__subscribability__ = NOT_SUBSCRIBABLE
        super(SubscribableRoot, self).__init__(context)

    def _buildSubscribablesList(self, subscribables=None, marker=0):
        # Overrides Subscribable._buildSubscribablesList to stop recursion.
        if subscribables is None:
            subscribables = []
        if self.context.__subscribability__ == NOT_SUBSCRIBABLE:
            # Empty list from the point without explicit subscribability onwards.
            del subscribables[marker:]
            return subscribables
        subscribables.append(self)
        return subscribables


# Jumping through security hoops to get the adapter
# somewhat accessible to Python scripts

allow_module('Products.Silva.adapters.subscribable')

__allow_access_to_unprotected_subobjects__ = 1

module_security = ModuleSecurityInfo('Products.Silva.adapters.subscribable')

module_security.declareProtected(
    SilvaPermissions.ApproveSilvaContent, 'getSubscribable')
def getSubscribable(context):
    adapter = interfaces.ISubscribable(context, None)
    if adapter is not None:
        return adapter.__of__(context)
    return None
