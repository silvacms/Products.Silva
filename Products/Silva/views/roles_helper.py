## Script (Python) "roles_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

#This is needed so we can get the READER_ROLES from a page template.
#When I tried to access the READER_ROLES via modules['Products'].Silva.roleinfo.READER_ROLES,
#I got an unauthorized error.

from Products.Silva.roleinfo import READER_ROLES

return list(READER_ROLES)
