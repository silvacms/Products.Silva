## Script (Python) "get_edit_mode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
view = context
request = view.REQUEST
model = request.model

context.set_cache_headers()
xhtml = unicode(model.editor_storage(editor='epoz', encoding='UTF-8'), 'UTF-8')

return ('<html>'
        '<head>'
        '<title>%s</title>'
        '<link type="text/css" rel="stylesheet" href="%s" />'
        '<link type="text/css" rel="stylesheet" href="%s" />'
        '</head>\n'
        '%s\n'
        '</html>' % (model.get_title_editable(), 
                        getattr(context.globals, 'silva.css').absolute_url(),
                        getattr(context.globals, 'frontend.css').absolute_url(),
                        xhtml))
