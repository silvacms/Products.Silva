## Script (Python) "move_up"
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
n = node
while 1:
    n = n.previousSibling
    if n is None or n.nodeType == node.ELEMENT_NODE:
        break
# can't go further up, so stop
if n is None:
    return

parent = node.parentNode
#parent.removeChild(node)
parent.insertBefore(node, n)
context.service_editor.setNodeWidget(node,
   context.get_widget_path()[:-1] + ('mode_done',))
return context.redirect()
