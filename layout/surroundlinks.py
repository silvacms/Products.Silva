# This script looks in the current container and returns access 
# navigation links including First, Previous, Next, and Last docs.
# It only returns docs that are published, and it ignores assets,
# folders, and publications (it includes SilvaNews publications).
# Unfortunately it also ignores the index item.

if not context.implements_content():
   return None, None, None, None
current_id = context.id
if current_id == 'index':
   return None, None, None, None
folder = context.get_container()
ordered_ids = [doc.id for (indent, doc) in folder.get_public_tree(1)]
if len(ordered_ids) <= 1:
   return None, None, None, None
current_index = ordered_ids.index(current_id)
if current_index == 0:
   first_doc = None
else:
   first_doc =  getattr(folder, ordered_ids[0])
if current_index <= 1:
   previous_doc = None
else:
   previous_doc = getattr(folder, ordered_ids[current_index - 1])
if current_index >= len(ordered_ids) - 2:
   next_doc = None
else:
   next_doc = getattr(folder, ordered_ids[current_index + 1])
if current_index == len(ordered_ids) - 1:
   last_doc = None
else:
   last_doc = getattr(folder, ordered_ids[len(ordered_ids) - 1])

return first_doc, previous_doc, next_doc, last_doc

