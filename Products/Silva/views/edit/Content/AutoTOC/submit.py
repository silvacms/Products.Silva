#basically all we do here is save to my_types

request = context.REQUEST
model = request.model

model.set_local_types(request.toc_types)
model.set_toc_depth(int(request.depth))

model.set_sort_order(request.sort_order)

model.set_display_desc_flag(request.get('display_desc')=='yes')
model.set_show_icon(request.get('show_icon')=='yes')
model.set_show_container_link(request.get('show_container_link')=='yes')

model.sec_update_last_author_info()
model.reindex_object()

return context.tab_edit(message_type="feedback",
                    message="AutoTOC settings saved.")
