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

toc_depth = request['toc_depth']
node.setAttribute('toc_depth', node.input_convert(toc_depth))
