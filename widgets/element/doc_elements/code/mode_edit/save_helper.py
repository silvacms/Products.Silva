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
if not request.has_key('code'):
  return ''

node = request.node

# don't need to conver this, later on we will convert it in replace_text()
code = request['code']

# replace text in node
node.get_content().replace_text(node, code)
