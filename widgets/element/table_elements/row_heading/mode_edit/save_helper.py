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
data = request['data']
editorsupport = context.service_editorsupport

editorsupport.replace_heading(node, data)
