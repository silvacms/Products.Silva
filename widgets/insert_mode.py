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
if not node.get_content().sec_create_lock():
    return context.redirect()

node.get_content().sec_update_last_author_info()
allowed_types = context.get_allowed_info(context.REQUEST.wr_name,node)
if len(allowed_types)==1:
   return context.insert(what = allowed_types[0][1])
else:
   context.service_editor.setNodeWidget(node, 
      context.get_widget_path()[:-1] + ('mode_insert',))
   return context.redirect()
