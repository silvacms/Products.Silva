##parameters=view_method='view'
content = 'content.html'
override = 'override.html'

# By default, the rendering is done by 'content', unless 
# a local 'override' exists (disregarding acquisition).
if hasattr(context.aq_explicit, override):
    renderer = override
else:
    renderer = content

# By default, the prefered view method is 'view()', unless
# a different view_method is passed to this script.
context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/html;charset=utf-8')
return getattr(context, renderer)(view_method=view_method)
