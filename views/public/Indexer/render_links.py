## Script (Python) "render_links"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=links
##title=
##
model = context.REQUEST.model

result = []
for name, url in links:
    result.append('<a class="indexer" href="%s">%s</a>' % (url, name))
return '<br />'.join(result)
