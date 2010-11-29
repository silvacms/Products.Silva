## Script (Python) "is_item_in_ids"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ref
##title=test if item has been checked
##
request = container.REQUEST
if not request.has_key('refs'):
  return None
return ref in request['refs']
