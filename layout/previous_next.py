# This script looks in the current container and returns previous 
# and next links to neighboring documents. It only returns 
# documents that are published, and it ignores assets.

# This script should be superceded by one for 'regionalinks', which
# locates all possible access navigation links including Top, Up,
# First/Start, Previous, Next, Last/End.

if not context.implements_content():
   return None, None
current_id = context.id
if current_id == 'index':
   return None, None
folder = context.get_container()
ordered_ids = [doc.id for (indent, doc) in folder.get_public_tree(1)]
if len(ordered_ids) < 1:
   return None, None
current_index = ordered_ids.index(current_id)
if current_index == 0:
   previous_doc = None
else:
   previous_doc = getattr(folder, ordered_ids[current_index - 1])
if current_index == len(ordered_ids) - 1:
   next_doc = None
else:
   next_doc = getattr(folder, ordered_ids[current_index + 1])

return previous_doc, next_doc

