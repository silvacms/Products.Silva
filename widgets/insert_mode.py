## Script (Python) "insert_mode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
node.sec_update_last_author_info()
context.service_editor.setNodeWidget(node, 
   context.get_widget_path()[:-1] + ('mode_insert',))
return context.redirect()
