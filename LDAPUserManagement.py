import types

try:
    import _ldap
    if not hasattr(_ldap, 'open'):
        raise ImportError
except ImportError:
    import ldap
    _ldap = ldap

class LDAPUserManagement:
    def _get_user_folder(self, object):
        # XXX hack...relatively inefficient
        while 1:
            if (hasattr(object.aq_base, 'acl_users') and
                object.acl_users.meta_type == 'LDAPUserFolder'):
                return object.acl_users
            if object.meta_type == 'Silva Root':
                break
            object = object.aq_parent
        return None
    
    def find_users(self, object, search_string):
        acl_users = self._get_user_folder(object)
        return ldap_search(acl_users, 'cn=*%s*' % search_string)
        
    def get_user_info(self, object, userid):
        acl_users = self._get_user_folder(object)
        result = ldap_search(acl_users, 'uid=%s' % userid)
        if not result:
            return {'uid': userid, 'cn': "%s (not in ldap)" % userid}  
        else:
            return result[0]
 
user_management = LDAPUserManagement()

def ldap_search(user_folder, search_string, attrs=None):
    res = user_folder._searchResults(
        search_base=user_folder.users_base,
        search_scope=_ldap.SCOPE_SUBTREE,
        search_string=search_string,
        attrs=attrs)
    
    result = []
    for dn, dict in res:
        userinfo = { 'dn': dn, 'sn' : '', 'cn' : '' }
        for key, value in dict.items():
            if key == 'ou':
                userinfo[key] = value
            else:
                userinfo[key] = value[0]
       
        result.append(userinfo)

    return result
