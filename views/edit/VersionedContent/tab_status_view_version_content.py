## Script (Python) "tab_status_revoke"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Revoke approval of approved content
##
view = context
request = view.REQUEST
model = request.model

from Products.Silva.adapters.version_management import \
                            getVersionManagementAdapter
adapter = getVersionManagementAdapter(model)
version = adapter.getVersionById(request.version)
node = version.content.documentElement

context.service_editor.setViewer('service_doc_previewer')
return context.service_editor.renderView(node)
