##parameters=url,link_type
from Products.Silva.i18n import translate as _
model = context.REQUEST.model
view = context
url = unicode(url, 'UTF-8')

model.get_editable().set_link_type(link_type)
model.get_editable().set_url(url)

model.sec_update_last_author_info()

return view.tab_edit(message_type='feedback', message=_("Link changed"))

