##parameters=url
from Products.Silva.i18n import translate as _
model = context.REQUEST.model
view = context
url = unicode(url, 'UTF-8')
model.sec_update_last_author_info()

model.get_editable().set_url(url)

return view.tab_edit(message_type='feedback', message=_("Link changed"))

