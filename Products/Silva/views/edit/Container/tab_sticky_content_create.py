from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model
view = context

if model.hasObject('service_sticky_content'):
    return view.tab_sticky_content(
        message_Type='error',
        message=_('A Sticky Content Service already exists.'))

model.manage_addProduct['silva.core.contentlayout'].manage_addStickyContentService()

return view.tab_sticky_content(message_type='feedback',
                               message=_('Sticky Content Service created.'))
