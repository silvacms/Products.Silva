# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import itertools
import hashlib
import time
import datetime

from App.class_init import InitializeClass
from BTrees.OOBTree import OOBTree
from Acquisition import aq_parent

from silva.core import interfaces
from five import grok


TIMEOUTINDAYS =  3

NOT_SUBSCRIBABLE = 0
SUBSCRIBABLE = 1
ACQUIRE_SUBSCRIBABILITY = 2

def generate_token(*args):
    hash = hashlib.md5()
    for arg in args:
        hash.update(str(args))
    return hash.hexdigest()

class Subscription(object):
    grok.implements(interfaces.ISubscription)

    def __init__(self, email, content):
        self.email = email
        self.content = content


class Subscribable(grok.Adapter):
    """Subscribable adapters potentially subscribable content and container
    Silva objects and encapsulates the necessary API for
    handling subscriptions.
    """
    grok.context(interfaces.ISilvaObject)
    grok.implements(interfaces.ISubscribable)
    grok.provides(interfaces.ISubscribable)

    subscribability_possibilities = [
        NOT_SUBSCRIBABLE, SUBSCRIBABLE, ACQUIRE_SUBSCRIBABILITY]

    def __init__(self, context):
        super(Subscribable, self).__init__(context)
        if not hasattr(context, '__subscribability__'):
            context.__subscribability__ = ACQUIRE_SUBSCRIBABILITY
        if not hasattr(context, '__subscriptions__'):
            context.__subscriptions__ = OOBTree()
        if not hasattr(context, '__pending_subscription_tokens__'):
            context.__pending_subscription_tokens__ = OOBTree()

    # ACCESSORS

    def is_subscribable(self):
        subscribability = self.context.__subscribability__
        if subscribability == NOT_SUBSCRIBABLE:
            return False
        if subscribability == SUBSCRIBABLE:
            return True
        parent = interfaces.ISubscribable(aq_parent(self.context))
        return parent.is_subscribable()

    @apply
    def subscribability():
        def getter(self):
            return self.context.__subscribability__
        def setter(self, flag):
            assert flag in self.subscribability_possibilities
            self.context.__subscribability__ = flag
        return property(getter, setter)

    @apply
    def locally_subscribed_emails():
        def getter(self):
            return set(self.context.__subscriptions__.keys())
        def setter(self, emails):
            # XXX Should not this be a set ??? (Need an upgrader)
            subscriptions = self.context.__subscriptions__
            subscriptions.clear()
            subscriptions.update(
                zip(emails, itertools.repeat(None, len(emails))))
        return property(getter, setter)

    # ACCESSORS

    def getSubscriptions(self):
        return self._getSubscriptions().values()

    def _getSubscriptions(self):
        if self.context.__subscribability__ == NOT_SUBSCRIBABLE:
            return {}
        subscriptions = {}
        subscribables = self._buildSubscribablesList()
        for subscribable in subscribables:
            for emailaddress in subscribable.locally_subscribed_emails:
                if not subscriptions.has_key(emailaddress):
                    subscriptions[emailaddress] = Subscription(
                        emailaddress, self.context)
        return subscriptions

    def _buildSubscribablesList(self, subscribables=None, marker=0):
        if subscribables is None:
            subscribables = []
        if self.context.__subscribability__ == NOT_SUBSCRIBABLE:
            # Empty list from the point without explicit
            # subscribability onwards.
            del subscribables[marker:]
            return subscribables
        subscribables.append(self)
        if self.context.__subscribability__ == SUBSCRIBABLE:
            # Keep a marker for the object with explicit subscribability set.
            marker = len(subscribables)
        parent = interfaces.ISubscribable(aq_parent(self.context))
        return parent._buildSubscribablesList(subscribables, marker)

    def isSubscribed(self, email):
        subscriptions = self.context.__subscriptions__
        return bool(subscriptions.has_key(email))

    def getSubscription(self, email):
        subscriptions = self._getSubscriptions()
        return subscriptions.get(email, None)

    # MODIFIERS

    def subscribe(self, email):
        subscriptions = self.context.__subscriptions__
        subscriptions[email] = None

    def unsubscribe(self, emailaddress):
        subscriptions = self.context.__subscriptions__
        if subscriptions.has_key(emailaddress):
            del subscriptions[emailaddress]

    def generateConfirmationToken(self, email):
        tokens = self.context.__pending_subscription_tokens__
        timestamp = '%f' % time.time()
        token = generate_token(email, timestamp)
        tokens[email] = (timestamp, token)
        return token

    def _validate(self, email, token):
        # The current implementation will keep items in the
        # pending list indefinitly if _validate is not called (end user
        # doesn't follow up on confirmantion email), or _validate is called,
        # but the supplied token is not valid.
        tokens = self.context.__pending_subscription_tokens__
        timestamp, validation_token = tokens.get(email, (None, None))
        if timestamp is None or validation_token is None:
            return False
        now = datetime.datetime.now()
        then = datetime.datetime.fromtimestamp(timestamp)
        delta = now - then
        if delta.days > TIMEOUTINDAYS:
            del tokens[email]
            return False
        if token == validation_token:
            del tokens[email]
            return True
        return False

    isValidSubscription = _validate
    isValidCancellation = _validate


InitializeClass(Subscribable)


class SubscribableRoot(Subscribable):
    grok.context(interfaces.IRoot)

    subscribability_possibilities = [NOT_SUBSCRIBABLE, SUBSCRIBABLE]

    def __init__(self, context):
        if not hasattr(context, '__subscribability__'):
            context.__subscribability__ = NOT_SUBSCRIBABLE
        super(SubscribableRoot, self).__init__(context)

    def _buildSubscribablesList(self, subscribables=None, marker=0):
        # Overrides Subscribable._buildSubscribablesList to stop recursion.
        if subscribables is None:
            subscribables = []
        if self.context.__subscribability__ == NOT_SUBSCRIBABLE:
            # Empty list from the point without explicit
            # subscribability onwards.
            del subscribables[marker:]
            return subscribables
        subscribables.append(self)
        return subscribables
