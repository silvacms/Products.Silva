import types

try:
    import _ldap
    if not hasattr(_ldap, 'open'):
        raise ImportError
except ImportError:
    import ldap
    _ldap = ldap

class LDAPUserManagement:
    def find_users(self, object, search_string):
        return ldap_search(object.acl_users, 'cn=*%s*' % search_string)
        
    def get_user_info(self, object, userid):
        result = ldap_search(object.acl_users, 'uid=%s' % userid)
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
