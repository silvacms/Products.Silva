BUILTIN_VIEWER_ROLES = ('Anonymous', 'Authenticated')
SILVA_VIEWER_ROLES = ('Viewer', 'Viewer +', 'Viewer ++')
VIEWER_ROLES = BUILTIN_VIEWER_ROLES + SILVA_VIEWER_ROLES
CHIEF_ROLES = ('ChiefEditor', 'Manager')
EDITOR_ROLES = ('Editor',) + CHIEF_ROLES
AUTHOR_ROLES = ('Author',) + EDITOR_ROLES
READER_ROLES = ('Reader',) + AUTHOR_ROLES
ALL_ROLES = VIEWER_ROLES + READER_ROLES
ASSIGNABLE_ROLES = SILVA_VIEWER_ROLES + READER_ROLES

def compareRoles(role1, role2):
    ALL_ROLES = list(ALL_ROLES)
    return cmp(ALL_ROLES.index(role1), ALL_ROLES.index(role2))

def getRolesAbove(role):
    ALL_ROLES = list(ALL_ROLES)
    return tuple(ALL_ROLES[ALL_ROLES.index(role):])
