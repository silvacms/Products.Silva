## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return '<tr colspan="%s" valign="top"><th class="transparent">%s</th></tr>' % (context.get_columns(), context.content())
