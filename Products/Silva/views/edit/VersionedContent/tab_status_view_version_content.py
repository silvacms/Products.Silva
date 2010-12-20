## Script (Python) "tab_status_revoke"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Revoke approval of approved content
##
request = context.REQUEST
model = request.model

from Products.Silva.adapters.version_management import \
                            getVersionManagementAdapter
adapter = getVersionManagementAdapter(model)
version = adapter.getVersionById(request.version)
return model.view_version('preview', version)
