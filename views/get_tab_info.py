## Script (Python) "get_tab_info"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=tab_item
##title=
##
model = context.REQUEST.model
view = context
tab_name, tab_id, tab_up_id, toplink_accesskey, tab_accesskey, uplink_accesskey = tab_item

if tab_up_id is not None:
    if model != model.get_root():
        uplink_url = model.aq_parent.absolute_url() + '/edit/' + tab_up_id
    else:
        uplink_url = None
    if model != model.get_root():
        toplink_url = model.aq_parent.get_publication().absolute_url() + '/edit/' + tab_up_id
    else:
        toplink_url = None
else:
    uplink_url = None
    toplink_url = None

return { 
  'tab_name' : tab_name,
  'tab_id' : tab_id,
  'toplink_url' : toplink_url,
  'tab_url' : model.absolute_url() + '/edit/' + tab_id,
  'uplink_url' : uplink_url,
  'toplink_accesskey' : toplink_accesskey,
  'tab_accesskey' : tab_accesskey,
  'uplink_accesskey' : uplink_accesskey
}
