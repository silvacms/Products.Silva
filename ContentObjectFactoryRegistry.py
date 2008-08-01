# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zExceptions import InternalError

class ContentObjectFactoryRegistry:
    """Registry for factories of content types

        is used for WebDAV and FTP to create content objects according
        to a set of arguments
    """
    def __init__(self):
        self._registry = []
        self._ordered = None

    def registerFactory(self, factory, checker, before=None):
        """Register a factory function for a certain content type

            'factory' is the factory function, will be called with 4 
            arguments: the container (context) the object will be added
            to, the id as used in PUT requests that trigger the creation,
            the content type (MIME-type) as specified by the client and
            the body of the request that should later be used as content
            (the factory itself doesn't have to actually write the content
            to the object, a call to PUT later on will make that happen,
            but may decide certain things from the body)

            Note that the factory may choose to not return an object, in
            that case checking will continue 

            checkhandler will be called with 3 arguments: the id, the
            content type as specified by the client and the body of the 
            request, and should return True or False according to whether
            the factory should be used to generate the object for this
            request

            before is the *checker* function which should be 'overridden'
            by the new one, what effectively happens is that the new 
            factory/checker will get called just before the 'before' one
            
            if the value of 'before' equals -1, the checker will be 
            registered at the end of the registry period, meaning that it
            will be used as the last item (default), this is *only* useful
            for a *single* checker/factory combination, therefore if anyone 
            else has already registered a default checker this will fail

            to override a default checker use it as the 'before' argument
        """
        # XXX the signature of this method suX0rz! perhaps we need to think
        # this over a bit to get it more comprehensible without losing 
        # flexibility
        if self._ordered:
            self._ordered = None
        self._registry.append((factory, checker, before))

    def _order(self):
        """Generates an ordered list out of the currently registered objects
        
            is called as soon as the registry is used for the first time
        """
        if self._ordered is not None:
            return
        regcopy = self._registry[:]
        ordered = []
        checkers = [-1, None]
        while 1:
            for checker in checkers[:]:
                regcopy_work = regcopy[:]
                checkers.remove(checker)
                for tup in regcopy:
                    if tup[2] is checker:
                        ordered.append(tup)
                        checkers.append(tup[1])
                        regcopy_work.remove(tup)
                regcopy = regcopy_work
            if len(checkers) == 0:
                break
        if len(regcopy) > 0:
            raise ValueError, 'registration error: %s could not be placed' % (
                                ', '.join([repr(r[1]) for r in regcopy]))
        self._ordered = ordered

    def getObjectFor(self, context, id, content_type, body):
        """Get a factory for a PUT request

            Is called from Folder.PUT_factory()
        """
        self._order()
        # walk the registry in reverse order
        tuples = self._ordered[:]
        tuples.reverse()
        for (factory, checker, before) in tuples:
            if checker(id, content_type, body):
                # we pass in the body even though the factory shouldn't 
                # actually set the contents of the object
                obj = factory(context, id, content_type, body)
                if obj:
                    # the factory can return None or something to
                    # notify this code that it doesn't want to handle
                    # the request after all
                    return obj
        # not sure about this exception type, is there a better one somewhere?
        raise InternalError, 'could not create new object, id might be invalid'

    def build(self):
        self._order()

contentObjectFactoryRegistry = ContentObjectFactoryRegistry()
