##parameters=tab_item
from Products.Silva.i18n import translate as _
model = context.REQUEST.model
view = context
tab_name, tab_id, tab_up_id, toplink_accesskey, tab_accesskey, uplink_accesskey = tab_item

if tab_up_id is not None:
    if model != model.get_root():
        uplink_url = model.aq_parent.absolute_url() + 'edit/' + tab_up_id
    else:
        uplink_url = None
    if model != model.get_root():
        toplink_url = model.aq_parent.get_publication().absolute_url() + 'edit/' + tab_up_id
    else:
        toplink_url = None
else:
    uplink_url = None
    toplink_url = None

if tab_id:
    u = model.absolute_url()
    if not u.endswith('/'):
        u += '/'
    tab_url = model.absolute_url() + 'edit/' + tab_id
else:
    tab_url = None

uplink_title = _('up a level: alt-${key}', mapping={'key': uplink_accesskey})
toplink_title = _('up to top of publication: alt-${key}',
                  mapping={'key': toplink_accesskey})
tab_title = _('access key: alt-${key}', mapping={'key': tab_accesskey})

return { 
  'tab_name' : _(tab_name),
  'tab_id' : tab_id,
  'toplink_url' : toplink_url,
  'tab_url' : tab_url,
  'uplink_url' : uplink_url,
  'toplink_accesskey' : toplink_accesskey,
  'tab_accesskey' : tab_accesskey,
  'uplink_accesskey' : uplink_accesskey,
  'uplink_title': uplink_title,
  'toplink_title': toplink_title,
  'tab_title': tab_title,
}
