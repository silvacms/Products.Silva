## Script (Python) "tab_status_version_user_infos"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=version
##title=Revoke approval of approved content
##
view = context
request = view.REQUEST
model = request.model

from Products.Silva.adapters.version_management import \
                            getVersionManagementAdapter
from Products.Silva import mangle

adapter = getVersionManagementAdapter(model)

lastauthor = adapter.getVersionLastAuthorInfo(version.id)
creator = adapter.getVersionCreatorInfo(version.id)

return lastauthor, creator
