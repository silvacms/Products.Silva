## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
model = request.model

unapproved = model.get_editable()
public = model.get_viewable()

result = []
if unapproved:
    r = {}
    r['version'] = unapproved
    r['name'] = 'unapproved'
    r['title'] = model.get_title_editable()
    result.append(r)
if public:
    r = {}
    r['version'] = public
    r['name'] = 'public'
    r['title'] = model.get_title()
    result.append(r)

return result



