from AccessControl import ModuleSecurityInfo

module_security = ModuleSecurityInfo('Products.Silva.roleinfo')

BUILTIN_VIEWER_ROLES = ('Anonymous', 'Authenticated')
SILVA_VIEWER_ROLES = ('Viewer', 'Viewer +', 'Viewer ++')
VIEWER_ROLES = BUILTIN_VIEWER_ROLES + SILVA_VIEWER_ROLES
CHIEF_ROLES = ('ChiefEditor', 'Manager')
EDITOR_ROLES = ('Editor',) + CHIEF_ROLES
AUTHOR_ROLES = ('Author',) + EDITOR_ROLES
READER_ROLES = ('Reader',) + AUTHOR_ROLES
ALL_ROLES = VIEWER_ROLES + READER_ROLES

module_security.declareProtected('Change Silva access',
                                 'ASSIGNABLE_ROLES')
ASSIGNABLE_ROLES = SILVA_VIEWER_ROLES + READER_ROLES

module_security.declareProtected('Change Silva access',
                                 'ASSIGNABLE_VIEWER_ROLES')
ASSIGNABLE_VIEWER_ROLES = VIEWER_ROLES

def compareRoles(role1, role2):
    all_roles = list(ALL_ROLES)
    return cmp(all_roles.index(role1), all_roles.index(role2))

def getRolesAbove(role):
    all_roles = list(ALL_ROLES)
    return tuple(all_roles[all_roles.index(role):])
