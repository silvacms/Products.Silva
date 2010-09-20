# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


class SubscriptionError(Exception):
    pass


class CancellationError(Exception):
    pass


class InvalidEmailaddressError(Exception):
    pass


class NotSubscribableError(Exception):
    pass


class AlreadySubscribedError(Exception):
    # NOTE: Please make sure in the UI code not to expose any information
    # about the validity of the email address!
    pass


class NotSubscribedError(Exception):
    # NOTE: Please make sure in the UI code not to expose any information
    # about the validity of the email address!
    pass
