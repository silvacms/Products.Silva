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
if request.has_key('path'):
    path = request['path']
else:
    path = '' 
node.setAttribute('path', node.input_convert(path))
