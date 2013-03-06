# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
from AccessControl import ModuleSecurityInfo
from silva.translations import translate as _

module_security = ModuleSecurityInfo('Products.Silva.roleinfo')

BUILTIN_VIEWER_ROLES = ('Anonymous', 'Authenticated')
SILVA_VIEWER_ROLES = ('Viewer', 'Viewer +', 'Viewer ++')
VIEWER_ROLES = BUILTIN_VIEWER_ROLES + SILVA_VIEWER_ROLES

module_security.declareProtected('View', 'CHIEF_ROLES')
MANAGER_ROLES = ('Manager',)
CHIEF_ROLES = ('ChiefEditor',) + MANAGER_ROLES
EDITOR_ROLES = ('Editor',) + CHIEF_ROLES
AUTHOR_ROLES = ('Author',) + EDITOR_ROLES
#aaltepet: 1/12/06: we want to be able test reader_roles
#from pythonscripts.  e.g. to see if current user
#can access smi
module_security.declareProtected('Change Silva access',
                                 'READER_ROLES')
READER_ROLES = ('Reader',) + AUTHOR_ROLES

module_security.declareProtected('View',
                                 'ALL_ROLES')
ALL_ROLES = VIEWER_ROLES + READER_ROLES

_i18n_markers = (
    _('zope roles'),
    _('silva roles'),
    _('public silva roles'),
    _('Anonymous'),
    _('Authenticated'),
    _('Manager'),
    _('Viewer'),
    _('Viewer +'),
    _('Viewer ++'),
    _('Reader'),
    _('Author'),
    _('Editor'),
    _('ChiefEditor'),)

module_security.declareProtected('Change Silva access',
                                 'ASSIGNABLE_ROLES')
ASSIGNABLE_ROLES = SILVA_VIEWER_ROLES + READER_ROLES
ASSIGNABLE_ROLES_SET = set(ASSIGNABLE_ROLES)

module_security.declareProtected('Change Silva access',
                                 'ASSIGNABLE_VIEWER_ROLES')
ASSIGNABLE_VIEWER_ROLES = VIEWER_ROLES


def isEqualToOrGreaterThan(role1, role2):
    roles = list(READER_ROLES)
    try:
        return roles.index(role1) >= roles.index(role2)
    except ValueError:
        if role2 not in roles:
            return True
        return False
