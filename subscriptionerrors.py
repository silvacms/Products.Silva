# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ModuleSecurityInfo, allow_module, allow_class

# Jumping through security hoops to get the adapter
# somewhat accessible to Python scripts

allow_module('Products.Silva.subscriptionerrors')

__allow_access_to_unprotected_subobjects__ = True
    
module_security = ModuleSecurityInfo('Products.Silva.subscriptionerrors')

class SubscriptionError(Exception):
    pass

allow_class(SubscriptionError)

class CancellationError(Exception):
    pass

allow_class(CancellationError)

class InvalidEmailaddressError(Exception):
    pass

allow_class(InvalidEmailaddressError)

class NotSubscribableError(Exception):
    pass

allow_class(NotSubscribableError)

class AlreadySubscribedError(Exception):
    # NOTE: Please make sure in the UI code not to expose any information
    # about the validity of the email address!
    pass

allow_class(AlreadySubscribedError)

class NotSubscribedError(Exception):
    # NOTE: Please make sure in the UI code not to expose any information
    # about the validity of the email address!
    pass

allow_class(NotSubscribedError)
