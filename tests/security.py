# credits go to the CMF for this code.
# code is under ZPL version 2.0

from Acquisition import Implicit

class PermissiveSecurityPolicy:
    """
        Very permissive security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate( self
                , accessed=None
                , container=None
                , name=None
                , value=None
                , context=None
                , roles=None
                , *args
                , **kw):
        return 1
    
    def checkPermission( self, permission, object, context) :
        if permission == 'forbidden permission':
            return 0
        return 1

class OmnipotentUser( Implicit ):
    """
      Omnipotent User for unit testing purposes.
    """
    def getId( self ):
        return 'all_powerful_Oz'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        return 1

class UserWithRoles( Implicit ):
    """
      User with roles specified in constructor
      for unit testing purposes.
    """
    def __init__( self, *roles ):
        self._roles = roles

    def getId( self ):
        return 'high_roller'
    
    getUserName = getId

    def allowed( self, object, object_roles=None ):
        if object_roles is None:
            object_roles=()
        for orole in object_roles:
            if orole in self._roles:
                return 1
        return 0

class AnonymousUser( Implicit ):
    """
      Anonymous USer for unit testing purposes.
    """
    def getId( self ):
        return 'Anonymous User'
    
    getUserName = getId

    def has_permission(self, permission, obj):
        # For types tool tests dealing with filtered_meta_types
        return 1

    def allowed( self, object, object_roles=None ):
        # for testing permissions on actions
        if object.getId() == 'actions_dummy':
            if 'Anonymous' in object_roles:
                return 1
            else:
                return 0
        return 1

    def getRoles(self):
        return ('Anonymous',)
