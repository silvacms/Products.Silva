## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
node = request.node

if request['what'] != 'pre':
    context.element_switch()
    return

# don't need to conver this, later on we will convert it in replace_text()
data = request['data']

node.get_content().replace_pre(node, data)
