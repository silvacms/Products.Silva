##parameters=url
model = context.REQUEST.model
view = context
url = unicode(url, 'UTF-8')
model.sec_update_last_author_info()
if not url.startswith('http://'):
    url = 'http://' + url
model.get_editable().set_url(url)

return view.tab_edit(message_type='feedback', message="Link changed")

