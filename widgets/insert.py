## Script (Python) "insert"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=what
##title=
##
node = context.REQUEST.node
wr_name = context.REQUEST.wr_name
if not context.is_allowed(wr_name, node, what):
    return

if not node.get_content().sec_create_lock():
    return context.redirect()

# create new node
doc = node.ownerDocument
new = doc.createElement(what)
new.appendChild(doc.createTextNode(''))

# insert new node, using insert method
context.insert_strategy(node, new)

# find widget for new node
widget = context.service_editor.getWidget(new)

node.get_content().sec_update_last_author_info()

# widget specific init
widget.insert_init()

# focus switching
widget.insert_helper()

return context.redirect()
