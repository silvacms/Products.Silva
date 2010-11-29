from Products.Silva.roleinfo import BUILTIN_VIEWER_ROLES, SILVA_VIEWER_ROLES, READER_ROLES

ar_roles = {'zope roles': BUILTIN_VIEWER_ROLES,
       'public silva roles' : SILVA_VIEWER_ROLES,
       'silva roles' : READER_ROLES}

local_roles = {
      'public silva roles' : SILVA_VIEWER_ROLES,
      'silva roles' : READER_ROLES}

return { 'ar_roles': ar_roles, 'local_roles': local_roles }
