## Script (Python) "frontend_render_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=elements
##title=
##
if not elements:
   return
if len(elements) == 1:
   return elements[0]
return ', '.join(elements[:-1]) + ' and ' + elements[-1]
